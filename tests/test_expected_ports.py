"""Unit tests for ``build_expected_ports`` — the deterministic
docker-compose.yml + run.sh → ``tasks.expected_ports`` descriptor builder.

Covers the generation spec:
  - terminal (7681) + editor (8443) are ALWAYS present.
  - db_console (8080, Adminer) added for SQL DB services, with creds extracted
    from the compose ``environment`` (dict and list forms).
  - app_preview (globe) added per HTTP host port (compose ``ports`` left-side,
    supplemented from run.sh), with unique labels; DB / infra services excluded.
  - pure script tasks (no DB, no server) → terminal + editor only.
"""
from generators.task.expected_ports import build_expected_ports


def _by_label(ports, label):
    """Return the single descriptor with ``label`` (or None)."""
    matches = [p for p in ports if p.get("label") == label]
    assert len(matches) <= 1, f"duplicate label {label!r}"
    return matches[0] if matches else None


def _labels(ports):
    return [p["label"] for p in ports]


# --------------------------------------------------------------------------
# Always-present tabs
# --------------------------------------------------------------------------

def test_pure_script_task_terminal_and_editor_only():
    ports = build_expected_ports({"main.py": "print('hi')", "run.sh": "python main.py\n"})
    assert _labels(ports) == ["terminal", "editor"]


def test_empty_code_files_still_returns_terminal_and_editor():
    assert _labels(build_expected_ports({})) == ["terminal", "editor"]


def test_terminal_descriptor_shape():
    term = _by_label(build_expected_ports({}), "terminal")
    assert term == {
        "icon": "terminal",
        "port": 7681,
        "label": "terminal",
        "title": "Terminal",
        "public": True,
        "cta_label": "Open Terminal",
    }
    assert "instructions" not in term  # terminal needs no prose


def test_editor_descriptor_shape_and_git_push_instruction():
    editor = _by_label(build_expected_ports({}), "editor")
    assert editor["icon"] == "editor"
    assert editor["port"] == 8443
    assert editor["url_params"] == {"folder": "/home/user/task"}
    assert "git push" in editor["instructions"]


def test_editor_folder_is_configurable():
    editor = _by_label(build_expected_ports({}, task_folder="/workspace"), "editor")
    assert editor["url_params"] == {"folder": "/workspace"}


# --------------------------------------------------------------------------
# Database (Adminer) tab
# --------------------------------------------------------------------------

_POSTGRES_COMPOSE = """
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: shopuser
      POSTGRES_PASSWORD: s3cret
      POSTGRES_DB: shop
    ports:
      - "5432:5432"
  api:
    build: .
    ports:
      - "8000:8000"
"""


def test_postgres_creates_db_console_with_credentials():
    ports = build_expected_ports({"docker-compose.yml": _POSTGRES_COMPOSE})
    db = _by_label(ports, "db_console")
    assert db is not None
    assert db["port"] == 8080
    assert db["icon"] == "database"
    creds = {c["label"]: c["value"] for c in db["credentials"]}
    assert creds["System"] == "PostgreSQL"          # exact match required by Adminer
    assert creds["Server"] == "127.0.0.1"
    assert creds["Username"] == "shopuser"
    assert creds["Password"] == "s3cret"
    assert creds["Database"] == "shop"
    assert "Adminer" in db["instructions"]


def test_postgres_defaults_when_env_missing():
    compose = "services:\n  db:\n    image: postgres\n"
    db = _by_label(build_expected_ports({"docker-compose.yml": compose}), "db_console")
    creds = {c["label"]: c["value"] for c in db["credentials"]}
    assert creds["System"] == "PostgreSQL"
    assert creds["Username"] == "postgres"
    assert creds["Database"] == "postgres"


def test_environment_list_form_is_parsed():
    compose = (
        "services:\n"
        "  database:\n"
        "    image: postgres:15\n"
        "    environment:\n"
        '      - "POSTGRES_USER=alice"\n'
        "      - POSTGRES_PASSWORD=pw123\n"
        "      - POSTGRES_DB=catalog\n"
    )
    db = _by_label(build_expected_ports({"docker-compose.yml": compose}), "db_console")
    creds = {c["label"]: c["value"] for c in db["credentials"]}
    assert creds["Username"] == "alice"
    assert creds["Password"] == "pw123"
    assert creds["Database"] == "catalog"


def test_mysql_creates_db_console():
    compose = (
        "services:\n"
        "  mysqldb:\n"
        "    image: mysql:8\n"
        "    environment:\n"
        "      MYSQL_USER: appuser\n"
        "      MYSQL_PASSWORD: apppw\n"
        "      MYSQL_DATABASE: store\n"
    )
    db = _by_label(build_expected_ports({"docker-compose.yml": compose}), "db_console")
    creds = {c["label"]: c["value"] for c in db["credentials"]}
    assert creds["System"] == "MySQL"
    assert creds["Username"] == "appuser"
    assert creds["Password"] == "apppw"
    assert creds["Database"] == "store"


def test_mariadb_maps_to_mysql_system():
    compose = "services:\n  db:\n    image: mariadb:11\n    environment:\n      MYSQL_ROOT_PASSWORD: rootpw\n"
    db = _by_label(build_expected_ports({"docker-compose.yml": compose}), "db_console")
    creds = {c["label"]: c["value"] for c in db["credentials"]}
    assert creds["System"] == "MySQL"
    assert creds["Username"] == "root"
    assert creds["Password"] == "rootpw"


def test_nosql_only_has_no_db_console():
    # Mongo can't be surfaced through the Adminer SQL login → no db_console.
    compose = "services:\n  mongo:\n    image: mongo:7\n    ports:\n      - '27017:27017'\n"
    ports = build_expected_ports({"docker-compose.yml": compose})
    assert _labels(ports) == ["terminal", "editor"]


# --------------------------------------------------------------------------
# HTTP preview tab(s)
# --------------------------------------------------------------------------

def test_http_service_creates_app_preview_from_host_port():
    ports = build_expected_ports({"docker-compose.yml": _POSTGRES_COMPOSE})
    app = _by_label(ports, "app_preview")
    assert app is not None
    assert app["port"] == 8000
    assert app["icon"] == "globe"
    assert app["title"] == "Preview"
    # omit prose instructions when we can't know what the app does
    assert "instructions" not in app


def test_db_port_is_not_an_app_preview():
    ports = build_expected_ports({"docker-compose.yml": _POSTGRES_COMPOSE})
    preview_ports = [p["port"] for p in ports if p["label"].startswith("app_preview")]
    assert 5432 not in preview_ports          # the postgres port must not leak in
    assert preview_ports == [8000]


def test_ip_prefixed_and_plain_port_bindings():
    compose = (
        "services:\n"
        "  web:\n"
        "    build: .\n"
        "    ports:\n"
        '      - "127.0.0.1:3000:3000"\n'
    )
    app = _by_label(build_expected_ports({"docker-compose.yml": compose}), "app_preview")
    assert app["port"] == 3000


def test_long_form_port_mapping():
    compose = (
        "services:\n"
        "  web:\n"
        "    build: .\n"
        "    ports:\n"
        "      - target: 8000\n"
        "        published: 8000\n"
        "        protocol: tcp\n"
    )
    app = _by_label(build_expected_ports({"docker-compose.yml": compose}), "app_preview")
    assert app["port"] == 8000


def test_bare_container_port_is_not_emitted_as_app_preview():
    # ports: ["8000"] = container port only; Docker picks a random host port,
    # so there is no routable host port → no app_preview tab.
    compose = "services:\n  web:\n    build: .\n    ports:\n      - '8000'\n"
    ports = build_expected_ports({"docker-compose.yml": compose})
    assert _by_label(ports, "app_preview") is None
    assert _labels(ports) == ["terminal", "editor"]


def test_build_only_service_generates_app_preview():
    compose = "services:\n  web:\n    build: .\n    ports:\n      - '8000:8000'\n"
    app = _by_label(build_expected_ports({"docker-compose.yml": compose}), "app_preview")
    assert app["port"] == 8000


def test_mariadb_env_aliases_are_parsed():
    compose = (
        "services:\n"
        "  db:\n"
        "    image: mariadb:11\n"
        "    environment:\n"
        "      MARIADB_USER: appuser\n"
        "      MARIADB_PASSWORD: apppw\n"
        "      MARIADB_DATABASE: store\n"
    )
    db = _by_label(build_expected_ports({"docker-compose.yml": compose}), "db_console")
    creds = {c["label"]: c["value"] for c in db["credentials"]}
    assert creds["System"] == "MySQL"
    assert creds["Username"] == "appuser"
    assert creds["Password"] == "apppw"
    assert creds["Database"] == "store"


def test_long_form_published_zero_is_not_swallowed():
    compose = (
        "services:\n"
        "  web:\n"
        "    build: .\n"
        "    ports:\n"
        "      - target: 8000\n"
        "        published: 0\n"
    )
    app = _by_label(build_expected_ports({"docker-compose.yml": compose}), "app_preview")
    assert app["port"] == 0


def test_infra_service_with_ports_is_not_a_preview():
    compose = (
        "services:\n"
        "  cache:\n"
        "    image: redis:7\n"
        "    ports:\n"
        "      - '6379:6379'\n"
        "  app:\n"
        "    build: .\n"
        "    ports:\n"
        "      - '5000:5000'\n"
    )
    ports = build_expected_ports({"docker-compose.yml": compose})
    preview_ports = [p["port"] for p in ports if p["label"].startswith("app_preview")]
    assert preview_ports == [5000]          # redis excluded, only the app


def test_multiple_http_services_get_unique_labels():
    compose = (
        "services:\n"
        "  web:\n"
        "    build: ./web\n"
        "    ports:\n"
        "      - '8000:8000'\n"
        "  worker_api:\n"
        "    build: ./worker\n"
        "    ports:\n"
        "      - '9000:9000'\n"
    )
    ports = build_expected_ports({"docker-compose.yml": compose})
    previews = [p for p in ports if p["label"].startswith("app_preview")]
    assert [p["label"] for p in previews] == ["app_preview", "app_preview_2"]
    assert {p["port"] for p in previews} == {8000, 9000}


def test_db_plus_http_full_set():
    ports = build_expected_ports({"docker-compose.yml": _POSTGRES_COMPOSE})
    assert _labels(ports) == ["terminal", "editor", "db_console", "app_preview"]


# --------------------------------------------------------------------------
# run.sh fallback (no compose, server started directly)
# --------------------------------------------------------------------------

def test_runsh_explicit_uvicorn_port_when_no_compose():
    run_sh = "#!/usr/bin/env bash\nuvicorn app.main:app --host 0.0.0.0 --port 8000\n"
    app = _by_label(build_expected_ports({"run.sh": run_sh}), "app_preview")
    assert app["port"] == 8000


def test_runsh_framework_default_flask():
    run_sh = "#!/usr/bin/env bash\nexport FLASK_APP=app\nflask run --host 0.0.0.0\n"
    app = _by_label(build_expected_ports({"run.sh": run_sh}), "app_preview")
    assert app["port"] == 5000


def test_runsh_port_deduped_against_compose():
    # compose already exposes 8000 via the app service; run.sh also names it.
    run_sh = "uvicorn app:app --port 8000\n"
    ports = build_expected_ports(
        {"docker-compose.yml": _POSTGRES_COMPOSE, "run.sh": run_sh}
    )
    previews = [p for p in ports if p["label"].startswith("app_preview")]
    assert [p["port"] for p in previews] == [8000]   # not duplicated


# --------------------------------------------------------------------------
# Robustness
# --------------------------------------------------------------------------

def test_malformed_compose_does_not_crash():
    ports = build_expected_ports({"docker-compose.yml": "services: [this: is: not: valid"})
    assert _labels(ports) == ["terminal", "editor"]


def test_nested_files_shape_is_supported():
    # creator passes the flat dict, but accept the legacy {"files": {...}} shape too.
    ports = build_expected_ports({"files": {"docker-compose.yml": _POSTGRES_COMPOSE}})
    assert _by_label(ports, "db_console") is not None
    assert _by_label(ports, "app_preview")["port"] == 8000


def test_compose_under_subdirectory_path_is_found():
    ports = build_expected_ports({"infra/docker-compose.yml": _POSTGRES_COMPOSE})
    assert _by_label(ports, "db_console") is not None
