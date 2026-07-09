"""Build the ``tasks.expected_ports`` JSONB array from a task's generated
``docker-compose.yml`` + ``run.sh``.

``expected_ports`` drives the candidate SandboxLayout: each entry becomes a tab
(see Utkrushta ``shared/models/_task_common.py::InteractionPort``). This is a
DETERMINISTIC parser — no LLM — so the same repo always yields the same tabs.

Generation spec (per-task):
  * ALWAYS: ``terminal`` (7681) + ``editor`` (8443).
  * ``db_console`` (8080, Adminer) when a SQL DB service (postgres / mysql /
    mariadb) is present, with credentials read from the compose ``environment``.
  * one ``app_preview`` (globe) per HTTP host port — read from the left side of
    each non-DB / non-infra service's ``ports:`` binding, supplemented from
    ``run.sh`` when the server is started directly (no compose).

Conservative by design: prose ``instructions`` are emitted only where they are
provably true after ``run.sh`` has run (editor git-push reminder, Adminer login
hint). The app-preview prose is omitted because what the app *does* can't be
known from compose alone — "omit if unsure".
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import yaml

from infra.logger_config import logger

# Fixed sandbox ports provided by the template base (start.sh).
TERMINAL_PORT = 7681
EDITOR_PORT = 8443
DB_CONSOLE_PORT = 8080
DEFAULT_TASK_FOLDER = "/home/user/task"

_COMPOSE_NAMES = (
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
)
_RUNSH_NAMES = ("run.sh",)

# image substring → Adminer "System" value (must be exact: wrong value breaks login)
_SQL_SYSTEMS: Tuple[Tuple[str, str], ...] = (
    ("postgis", "PostgreSQL"),
    ("postgres", "PostgreSQL"),
    ("mariadb", "MySQL"),
    ("mysql", "MySQL"),
    ("percona", "MySQL"),
)

# services that expose ports but are NOT browsable HTTP apps (no app_preview)
_NON_HTTP_IMAGE_HINTS = (
    "redis", "mongo", "kafka", "zookeeper", "rabbitmq", "qdrant", "chroma",
    "weaviate", "elasticsearch", "opensearch", "memcached", "cassandra",
    "nats", "etcd", "consul", "clickhouse", "neo4j", "minio", "adminer",
)

# run.sh: explicit bind flags, e.g. ``--port 8000`` / ``--bind 0.0.0.0:8000``.
# Long-form only — `-p`/`-b` are too ambiguous (ssh, scp, docker run, pytest, …).
_RUNSH_PORT_FLAG_RE = re.compile(
    r"(?:--port|--http-port|--bind)[=\s]+(?:[\d.]*:)?(\d{2,5})\b"
)
_RUNSH_PORT_ENV_RE = re.compile(r"\bPORT\s*=\s*(\d{2,5})\b")
# run.sh: framework → conventional default port when no explicit port is given
_RUNSH_FRAMEWORK_DEFAULTS: Tuple[Tuple[str, int], ...] = (
    ("uvicorn", 8000),
    ("gunicorn", 8000),
    ("hypercorn", 8000),
    ("flask run", 5000),
    ("manage.py runserver", 8000),
    ("php artisan serve", 8000),
    ("streamlit run", 8501),
    ("rails server", 3000),
    ("npm start", 3000),
    ("npm run start", 3000),
    ("yarn start", 3000),
    ("pnpm start", 3000),
)

_RESERVED_PORTS = {TERMINAL_PORT, EDITOR_PORT, DB_CONSOLE_PORT}


def build_expected_ports(
    code_files: Dict[str, str], *, task_folder: str = DEFAULT_TASK_FOLDER
) -> List[Dict]:
    """Return the ``tasks.expected_ports`` descriptor list for a task.

    ``code_files`` is the flat ``{path: content}`` map the creator passes (the
    legacy ``{"files": {...}}`` shape is also accepted). Never raises — a
    malformed compose degrades to terminal + editor only.
    """
    ports: List[Dict] = [_terminal_tab(), _editor_tab(task_folder)]

    services = _parse_services(_find_file(code_files, _COMPOSE_NAMES))

    sql_db = _detect_sql_db(services)
    if sql_db is not None:
        ports.append(_db_console_tab(sql_db))

    http_ports = _http_ports_from_compose(services)
    for port in _http_ports_from_runsh(_find_file(code_files, _RUNSH_NAMES)):
        if port not in http_ports:
            http_ports.append(port)

    for index, port in enumerate(http_ports):
        ports.append(_app_preview_tab(port, index))

    return ports


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def _terminal_tab() -> Dict:
    return {
        "icon": "terminal",
        "port": TERMINAL_PORT,
        "label": "terminal",
        "title": "Terminal",
        "public": True,
        "cta_label": "Open Terminal",
    }


def _editor_tab(task_folder: str) -> Dict:
    return {
        "icon": "editor",
        "port": EDITOR_PORT,
        "label": "editor",
        "title": "Editor",
        "public": True,
        "cta_label": "Open Editor",
        "url_params": {"folder": task_folder},
        "instructions": (
            "Before submitting, run git push so your work reaches the grading "
            "pipeline."
        ),
    }


def _db_console_tab(sql_db: SqlDb) -> Dict:
    return {
        "icon": "database",
        "port": DB_CONSOLE_PORT,
        "label": "db_console",
        "title": "Database",
        "public": True,
        "cta_label": "Open Database",
        # Sandbox-only, disposable DB credentials read from the generated
        # compose — never production secrets.
        "credentials": [
            {"label": "System", "value": sql_db.system},
            {"label": "Server", "value": "127.0.0.1"},
            {"label": "Username", "value": sql_db.username},
            {"label": "Password", "value": sql_db.password},
            {"label": "Database", "value": sql_db.database},
        ],
        "instructions": "Paste the credentials below into the Adminer login form.",
    }


def _app_preview_tab(port: int, index: int) -> Dict:
    # first preview keeps the clean "app_preview" label; extras are suffixed
    # from _2 (the sequence app_preview, app_preview_2, … is intentional).
    label = "app_preview" if index == 0 else f"app_preview_{index + 1}"
    return {
        "icon": "globe",
        "port": port,
        "label": label,
        "title": "Preview",
        "public": True,
        "cta_label": "Open Preview",
    }


# ---------------------------------------------------------------------------
# File lookup
# ---------------------------------------------------------------------------

def _find_file(code_files: Dict[str, str], names: Tuple[str, ...]) -> str:
    """Return the content of the first file whose basename matches ``names``
    (case-insensitive). Accepts the flat ``{path: content}`` map or the legacy
    ``{"files": {...}}`` wrapper."""
    if not isinstance(code_files, dict):
        return ""
    nested = code_files.get("files")
    files = nested if isinstance(nested, dict) else code_files
    wanted = {name.lower() for name in names}
    for path, content in files.items():
        basename = str(path).rsplit("/", 1)[-1].lower()
        if basename in wanted and isinstance(content, str):
            return content
    return ""


# ---------------------------------------------------------------------------
# docker-compose parsing
# ---------------------------------------------------------------------------

def _parse_services(compose_text: str) -> Dict[str, Dict]:
    """Return the ``services`` mapping from compose text, or ``{}`` on any
    problem (missing / malformed / unexpected shape)."""
    if not compose_text or not compose_text.strip():
        return {}
    try:
        data = yaml.safe_load(compose_text)
    except yaml.YAMLError as exc:
        logger.warning("expected_ports: could not parse docker-compose.yml: %s", exc)
        return {}
    if not isinstance(data, dict):
        return {}
    services = data.get("services")
    return services if isinstance(services, dict) else {}


@dataclass(frozen=True)
class SqlDb:
    """Resolved SQL database connection surfaced via the Adminer console."""

    system: str
    username: str
    password: str
    database: str


def _detect_sql_db(services: Dict[str, Dict]) -> Optional[SqlDb]:
    """Return the first SQL DB service as a ``SqlDb`` (Adminer can target one
    server), or ``None``. NoSQL stores are intentionally skipped — they can't be
    surfaced through the Adminer SQL login."""
    for service in services.values():
        system = _sql_system(_image(service))
        if system:
            return _credentials(system, _environment(service))
    return None


def _credentials(system: str, env: Dict[str, str]) -> SqlDb:
    if system == "PostgreSQL":
        username = env.get("POSTGRES_USER", "postgres")
        password = env.get("POSTGRES_PASSWORD", "postgres")
        # postgres' default database name equals the role name.
        database = env.get("POSTGRES_DB", username)
        return SqlDb(system, username, password, database)
    # MySQL / MariaDB (MariaDB 10.4+ also accepts MARIADB_* aliases).
    user = env.get("MYSQL_USER") or env.get("MARIADB_USER")
    if user:
        username = user
        password = env.get("MYSQL_PASSWORD") or env.get("MARIADB_PASSWORD", "")
    else:
        username = "root"
        password = env.get("MYSQL_ROOT_PASSWORD") or env.get("MARIADB_ROOT_PASSWORD", "")
    database = env.get("MYSQL_DATABASE") or env.get("MARIADB_DATABASE", "")
    return SqlDb(system, username, password, database)


def _http_ports_from_compose(services: Dict[str, Dict]) -> List[int]:
    """Host ports of services that are browsable HTTP apps (not SQL DB, not
    known infra), in compose declaration order, de-duplicated."""
    ports: List[int] = []
    for service in services.values():
        image = _image(service)
        if _sql_system(image) or _is_non_http(image):
            continue
        for port in _host_ports(service):
            if port not in ports and port not in _RESERVED_PORTS:
                ports.append(port)
    return ports


def _image(service: Dict) -> str:
    if not isinstance(service, dict):
        return ""
    image = service.get("image")
    return str(image).lower() if image else ""


def _sql_system(image: str) -> Optional[str]:
    for hint, system in _SQL_SYSTEMS:
        if hint in image:
            return system
    return None


def _is_non_http(image: str) -> bool:
    return any(hint in image for hint in _NON_HTTP_IMAGE_HINTS)


def _environment(service: Dict) -> Dict[str, str]:
    """Normalise compose ``environment`` (dict OR ``KEY=VALUE`` list) to a dict."""
    raw = service.get("environment") if isinstance(service, dict) else None
    env: Dict[str, str] = {}
    if isinstance(raw, dict):
        for key, value in raw.items():
            env[str(key)] = _clean_value(value)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str) and "=" in item:
                key, value = item.split("=", 1)
                env[key.strip()] = _clean_value(value)
    return env


def _clean_value(value) -> str:
    text = str(value).strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1]
    return text


def _host_ports(service: Dict) -> List[int]:
    raw = service.get("ports") if isinstance(service, dict) else None
    if not isinstance(raw, list):
        return []
    out: List[int] = []
    for entry in raw:
        port = _parse_port_entry(entry)
        if port is not None:
            out.append(port)
    return out


def _parse_port_entry(entry) -> Optional[int]:
    """Extract the HOST/published port from a single compose ``ports`` entry.

    Handles ``"H:C"``, ``"IP:H:C"``, bare ``"C"``, ``"H:C/tcp"``, ints, and the
    long form ``{published: H, target: C}``.
    """
    if isinstance(entry, dict):
        # Prefer the declared host (published) port; fall back to the container
        # (target) port only when no host port is given. `is None` so a
        # legitimate `published: 0` isn't swallowed by truthiness.
        published = entry.get("published")
        return _to_int(entry.get("target") if published is None else published)
    if isinstance(entry, int):
        return entry
    if isinstance(entry, str):
        text = entry.strip().split("/", 1)[0]
        parts = text.split(":")
        if len(parts) == 1:
            # Bare "C" = container port only; Docker assigns a random host port,
            # so there is no routable host port to surface as a tab.
            return None
        host = parts[0] if len(parts) == 2 else parts[-2]  # "H:C" or "IP:H:C"
        return _to_int(host)
    return None


def _to_int(value) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if "-" in text:  # port range "8000-8001" → take the first
        text = text.split("-", 1)[0].strip()
    return int(text) if text.isdigit() else None


# ---------------------------------------------------------------------------
# run.sh parsing (fallback when the server is started outside compose)
# ---------------------------------------------------------------------------

def _http_ports_from_runsh(run_sh: str) -> List[int]:
    """Best-effort, conservative server-port detection from run.sh.

    Prefers explicit ``--port`` / ``--bind`` / ``PORT=`` values; otherwise falls
    back to a single framework-default port when a known launcher is present.
    """
    if not run_sh:
        return []
    found: List[int] = []
    for match in _RUNSH_PORT_FLAG_RE.finditer(run_sh):
        found.append(int(match.group(1)))
    for match in _RUNSH_PORT_ENV_RE.finditer(run_sh):
        found.append(int(match.group(1)))
    if not found:
        lowered = run_sh.lower()
        for keyword, port in _RUNSH_FRAMEWORK_DEFAULTS:
            if keyword in lowered:
                found.append(port)
                break
    out: List[int] = []
    for port in found:
        if 1 <= port <= 65535 and port not in out and port not in _RESERVED_PORTS:
            out.append(port)
    return out
