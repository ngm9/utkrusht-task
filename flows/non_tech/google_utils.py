import csv
import io
import json
import os
from pathlib import Path
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from infra.logger_config import logger

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]

TASK_RESOURCES_FOLDER_NAME = "task-resources"
_folder_id_cache: Optional[str] = None


def get_google_credentials():
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON env var not set")
    info = json.loads(service_account_json)
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


def get_shared_drive_id() -> str:
    drive_id = os.getenv("GOOGLE_UTKRUSHT_TASK_RESOURCES_SHARED_DRIVE_ID")
    if not drive_id:
        raise ValueError("GOOGLE_UTKRUSHT_TASK_RESOURCES_SHARED_DRIVE_ID env var not set")
    return drive_id


def get_or_create_task_resources_folder(drive_service) -> str:
    global _folder_id_cache
    if _folder_id_cache:
        return _folder_id_cache

    shared_drive_id = get_shared_drive_id()

    query = (
        f"name='{TASK_RESOURCES_FOLDER_NAME}' "
        "and mimeType='application/vnd.google-apps.folder' "
        "and trashed=false "
        f"and '{shared_drive_id}' in parents"
    )
    results = drive_service.files().list(
        q=query,
        fields="files(id, name)",
        corpora="drive",
        driveId=shared_drive_id,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
    ).execute()
    files = results.get("files", [])

    if files:
        _folder_id_cache = files[0]["id"]
        logger.info(f"Found existing task-resources folder in Shared Drive: {_folder_id_cache}")
        return _folder_id_cache

    folder = drive_service.files().create(
        body={
            "name": TASK_RESOURCES_FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [shared_drive_id],
        },
        fields="id",
        supportsAllDrives=True,
    ).execute()
    folder_id = folder["id"]

    _folder_id_cache = folder_id
    logger.info(f"Created task-resources folder in Shared Drive: {folder_id}")
    return folder_id


def create_task_folder(drive_service, task_id: str) -> str:
    parent_folder_id = get_or_create_task_resources_folder(drive_service)
    folder = drive_service.files().create(
        body={
            "name": task_id,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id],
        },
        fields="id",
        supportsAllDrives=True,
    ).execute()
    folder_id = folder["id"]
    logger.info(f"Created task folder for {task_id}: {folder_id}")
    return folder_id


def resource_display_name(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace("_", " ").replace("-", " ").title()


def _share_publicly(drive_service, file_id: str) -> None:
    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        supportsAllDrives=True,
    ).execute()


def create_google_sheet(task_name: str, display_name: str, csv_content: str, parent_folder_id: str, drive_service, sheets_service) -> str:
    file_title = f"{task_name} — {display_name}"

    spreadsheet = drive_service.files().create(
        body={
            "name": file_title,
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "parents": [parent_folder_id],
        },
        fields="id",
        supportsAllDrives=True,
    ).execute()
    spreadsheet_id = spreadsheet["id"]

    rows = list(csv.reader(io.StringIO(csv_content)))
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    _share_publicly(drive_service, spreadsheet_id)

    logger.info(f"Created Google Sheet: {file_title} ({spreadsheet_id})")
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit?usp=sharing"


def create_google_doc(task_name: str, display_name: str, text_content: str, parent_folder_id: str, drive_service, docs_service) -> str:
    file_title = f"{task_name} — {display_name}"

    doc = drive_service.files().create(
        body={
            "name": file_title,
            "mimeType": "application/vnd.google-apps.document",
            "parents": [parent_folder_id],
        },
        fields="id",
        supportsAllDrives=True,
    ).execute()
    document_id = doc["id"]

    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={"requests": [{"insertText": {"location": {"index": 1}, "text": text_content}}]},
    ).execute()

    _share_publicly(drive_service, document_id)

    logger.info(f"Created Google Doc: {file_title} ({document_id})")
    return f"https://docs.google.com/document/d/{document_id}/edit?usp=sharing"


def upload_resources_to_google(task_name: str, task_id: str, code_files: dict) -> dict:
    creds = get_google_credentials()
    drive_service = build("drive", "v3", credentials=creds)
    sheets_service = build("sheets", "v4", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    task_folder_id = create_task_folder(drive_service, task_id)
    resources = {}

    for filename, content in code_files.items():
        ext = Path(filename).suffix.lower()
        display_name = resource_display_name(filename)
        try:
            if ext == ".csv":
                url = create_google_sheet(task_name, display_name, content, task_folder_id, drive_service, sheets_service)
            elif ext in (".md", ".txt"):
                url = create_google_doc(task_name, display_name, content, task_folder_id, drive_service, docs_service)
            else:
                logger.warning(f"Skipping unsupported resource type: {filename}")
                continue
            resources[display_name] = url
        except Exception as e:
            logger.warning(f"Failed to upload {filename} to Google: {e}")

    return resources
