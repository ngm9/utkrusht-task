"""
Google Drive utilities for uploading task resources.

Converts CSV files to Google Sheets, TXT/JSON to Google Docs,
and creates a shared folder with "anyone with link can view" access.

Supports two auth modes:
  1. OAuth2 (preferred) — uses your personal Google account's 15GB quota
     Run `python google_drive_utils.py setup` once to authorize
  2. Service Account (fallback) — needs quota allocation

Requires:
    pip install google-api-python-client google-auth google-auth-oauthlib
"""

import json
import mimetypes
import os
from pathlib import Path
from typing import Dict, Optional

from logger_config import logger

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaInMemoryUpload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.info("Google API libraries not installed. Install with: pip install google-api-python-client google-auth google-auth-oauthlib")


DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
DEFAULT_PARENT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID", "1_oycj7UeNTmVJz4xv_WJE2TeHtaPM-YZ")
TOKEN_PATH = Path(__file__).parent / ".google_token.json"
_secrets_env = os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS", "")
if not _secrets_env:
    from dotenv import load_dotenv
    load_dotenv()
    _secrets_env = os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS", "")
CLIENT_SECRETS_PATH = Path(_secrets_env) if _secrets_env else Path(__file__).parent / "client_secrets.json"


def _build_drive_service_oauth():
    """Build Drive service using OAuth2 credentials (user's own quota)."""
    if not TOKEN_PATH.exists():
        raise FileNotFoundError(
            f"OAuth token not found at {TOKEN_PATH}. "
            "Run `python google_drive_utils.py setup` to authorize."
        )

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), DRIVE_SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())
        logger.info("OAuth token refreshed")

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _build_drive_service_sa(service_account_key_path: str):
    """Build Drive service using a service account key."""
    credentials = service_account.Credentials.from_service_account_file(
        service_account_key_path, scopes=DRIVE_SCOPES
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def _get_drive_service(service_account_key_path: str = None):
    """Get Drive service — prefer OAuth2, fall back to service account."""
    if TOKEN_PATH.exists():
        try:
            return _build_drive_service_oauth()
        except Exception as e:
            logger.warning(f"OAuth auth failed, trying service account: {e}")

    if service_account_key_path and Path(service_account_key_path).exists():
        return _build_drive_service_sa(service_account_key_path)

    raise RuntimeError(
        "No Google credentials available. Either:\n"
        "  1. Run `python google_drive_utils.py setup` for OAuth2, or\n"
        "  2. Set GOOGLE_SERVICE_ACCOUNT_KEY_PATH in .env"
    )


def _create_folder(service, folder_name: str, parent_id: str = None) -> str:
    """Create a Google Drive folder and return its ID."""
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def _share_folder(service, folder_id: str) -> None:
    """Set folder to 'anyone with link can view'."""
    permission = {"type": "anyone", "role": "reader"}
    service.permissions().create(fileId=folder_id, body=permission).execute()


def _upload_as_google_sheet(service, filename: str, content: str, folder_id: str) -> str:
    """Upload CSV content as a Google Sheet."""
    media = MediaInMemoryUpload(
        content.encode("utf-8"), mimetype="text/csv", resumable=False
    )
    metadata = {
        "name": filename,
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "parents": [folder_id],
    }
    result = service.files().create(
        body=metadata, media_body=media, fields="id"
    ).execute()
    return result["id"]


def _upload_as_google_doc(service, filename: str, content: str, folder_id: str) -> str:
    """Upload text content as a Google Doc."""
    media = MediaInMemoryUpload(
        content.encode("utf-8"), mimetype="text/plain", resumable=False
    )
    metadata = {
        "name": filename,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],
    }
    result = service.files().create(
        body=metadata, media_body=media, fields="id"
    ).execute()
    return result["id"]


def _format_json_for_doc(content: str) -> str:
    """Pretty-print JSON for readable Google Doc display."""
    try:
        parsed = json.loads(content)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return content


def _get_display_name(filepath: str) -> str:
    """Extract a clean display name from a file path like 'data/call_logs.csv'."""
    name = Path(filepath).stem
    return name.replace("_", " ").title()


def create_google_drive_folder(
    files: Dict[str, str],
    task_name: str,
    service_account_key_path: str = None,
) -> Optional[str]:
    """Create a Google Drive folder with task resources.

    CSV files become Google Sheets, TXT/MD files become Google Docs,
    JSON files become formatted Google Docs.

    Args:
        files: Dict mapping file paths to content strings (from code_files)
        task_name: Task name used as the folder name
        service_account_key_path: Path to service account key (fallback if no OAuth token)

    Returns:
        Google Drive folder URL, or None on failure
    """
    if not GOOGLE_AVAILABLE:
        logger.warning("Google API libraries not available — skipping Drive upload")
        return None

    if not files:
        logger.warning("No files to upload to Google Drive")
        return None

    try:
        service = _get_drive_service(service_account_key_path)
        logger.info("Google Drive service initialized")

        # Create folder inside shared parent
        clean_name = task_name[:100].strip()
        folder_id = _create_folder(service, clean_name, parent_id=DEFAULT_PARENT_FOLDER_ID)
        logger.info(f"Created Drive folder: {clean_name} ({folder_id})")

        # Upload each file
        uploaded = 0
        for filepath, content in files.items():
            if not content or not content.strip():
                continue

            content_size = len(content.encode("utf-8"))
            if content_size > MAX_FILE_SIZE_BYTES:
                logger.warning(f"  Skipping large file: {filepath} ({content_size} bytes)")
                continue

            display_name = _get_display_name(filepath)
            ext = Path(filepath).suffix.lower()

            try:
                if ext == ".csv":
                    _upload_as_google_sheet(service, display_name, content, folder_id)
                    logger.info(f"  Uploaded as Sheet: {filepath} -> '{display_name}'")
                elif ext in (".txt", ".md"):
                    _upload_as_google_doc(service, display_name, content, folder_id)
                    logger.info(f"  Uploaded as Doc: {filepath} -> '{display_name}'")
                elif ext == ".json":
                    formatted = _format_json_for_doc(content)
                    _upload_as_google_doc(service, display_name, formatted, folder_id)
                    logger.info(f"  Uploaded as Doc (JSON): {filepath} -> '{display_name}'")
                else:
                    mime_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
                    media = MediaInMemoryUpload(
                        content.encode("utf-8"), mimetype=mime_type, resumable=False
                    )
                    metadata = {"name": Path(filepath).name, "parents": [folder_id]}
                    service.files().create(body=metadata, media_body=media, fields="id").execute()
                    logger.info(f"  Uploaded as file: {filepath}")
                uploaded += 1
            except Exception as e:
                logger.error(f"  Failed to upload {filepath}: {e}")
                continue

        if uploaded == 0:
            logger.error("No files were uploaded — Drive folder is empty")
            return None

        # Share folder
        _share_folder(service, folder_id)
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        logger.info(f"Drive folder shared: {folder_url}")

        return folder_url

    except Exception as e:
        logger.error(f"Google Drive folder creation failed: {e}")
        return None


def setup_oauth():
    """One-time OAuth2 setup — opens browser, saves refresh token."""
    if not GOOGLE_AVAILABLE:
        print("Install: pip install google-api-python-client google-auth google-auth-oauthlib")
        return

    secrets_path = CLIENT_SECRETS_PATH
    if not secrets_path.exists():
        # Create OAuth client ID at https://console.cloud.google.com/apis/credentials
        print("To set up OAuth2:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID (Desktop app)")
        print("3. Download the JSON file")
        print(f"4. Set GOOGLE_OAUTH_CLIENT_SECRETS=/path/to/client_secrets.json in .env")
        print(f"   Or save it as: {Path(__file__).parent / 'client_secrets.json'}")
        return

    flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), DRIVE_SCOPES)
    creds = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(creds.to_json())
    print(f"OAuth token saved to: {TOKEN_PATH}")
    print("Google Drive uploads will now use your personal account.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_oauth()
    else:
        print("Usage: python google_drive_utils.py setup")
