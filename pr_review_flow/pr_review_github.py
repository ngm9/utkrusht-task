"""GitHub operations for PR Review tasks: branch creation, PR file upload, PR opening."""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Tuple

from github import Github, InputGitTreeElement, GithubException
from dotenv import load_dotenv

from github_utils import create_github_repo, upload_files_batch

load_dotenv()
logger = logging.getLogger(__name__)

REPO_OWNER = os.getenv("REPO_OWNER")
GITHUB_TOKEN = os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN")
MAX_API_RETRIES = 2


def _get_repo_obj(repo_name: str):
    """Get PyGithub repo object."""
    github = Github(GITHUB_TOKEN)
    return github.get_repo(f"{REPO_OWNER}/{repo_name}")


def _retry_on_failure(func, *args, **kwargs):
    """Retry a function up to MAX_API_RETRIES times on transient GitHub failures."""
    last_error = None
    for attempt in range(MAX_API_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except GithubException as e:
            if e.status >= 500 or e.status == 403:
                last_error = e
                if attempt < MAX_API_RETRIES:
                    time.sleep(2 ** attempt)
                    continue
            raise
        except Exception as e:
            last_error = e
            if attempt < MAX_API_RETRIES:
                time.sleep(2 ** attempt)
                continue
            raise
    raise last_error  # type: ignore[misc]


def create_branch_from_main(repo_obj, branch_name: str) -> str:
    """Create a new branch from main. Returns the branch name."""
    main_ref = repo_obj.get_git_ref("heads/main")
    main_sha = main_ref.object.sha
    repo_obj.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_sha)
    logger.info(f"Created branch '{branch_name}' from main ({main_sha[:8]})")
    return branch_name


def upload_pr_files_to_branch(
    repo_obj,
    branch_name: str,
    modified_files: Dict[str, str],
    added_files: Dict[str, str],
    deleted_files: List[str],
    commit_message: str = "Add feature implementation",
) -> bool:
    """Upload PR files to a branch, supporting modifications, additions, and deletions.

    Unlike upload_files_batch, this supports file deletion via tree entries with sha=None.
    """
    try:
        ref = repo_obj.get_git_ref(f"heads/{branch_name}")
        base_commit = repo_obj.get_git_commit(ref.object.sha)
        base_tree = base_commit.tree

        element_list = []

        # Modified and added files -- create blobs
        all_files = {**modified_files, **added_files}
        for file_path, content in all_files.items():
            clean_path = file_path.lstrip('/')
            if isinstance(content, dict):
                content = json.dumps(content, indent=2, ensure_ascii=False)
            blob = repo_obj.create_git_blob(str(content), "utf-8")
            element_list.append(
                InputGitTreeElement(path=clean_path, mode="100644", type="blob", sha=blob.sha)
            )

        # Deleted files -- tree entries with sha=None
        for file_path in deleted_files:
            clean_path = file_path.lstrip('/')
            element_list.append(
                InputGitTreeElement(path=clean_path, mode="100644", type="blob", sha=None)
            )

        new_tree = repo_obj.create_git_tree(element_list, base_tree)
        new_commit = repo_obj.create_git_commit(
            message=commit_message, tree=new_tree, parents=[base_commit]
        )
        ref.edit(new_commit.sha)

        logger.info(f"Pushed {len(all_files)} files ({len(deleted_files)} deletions) to '{branch_name}'")
        return True
    except Exception as e:
        logger.error(f"Error uploading PR files to branch: {e}")
        return False


def open_pull_request(
    repo_obj, branch_name: str, title: str, body: str, base: str = "main"
) -> str:
    """Open a pull request. Returns the PR URL."""
    pr = repo_obj.create_pull(title=title, body=body, head=branch_name, base=base)
    logger.info(f"Opened PR #{pr.number}: {pr.html_url}")
    return pr.html_url


def create_pr_review_repo(
    task_name: str,
    base_repo_files: Dict[str, str],
    pr_data: Dict,
    branch_name: str,
) -> Tuple[str, str]:
    """Full GitHub flow: create repo, push base, create branch, push PR files, open PR.

    Returns (repo_url, pr_url).
    """
    # Step 1: Create repo
    repo_name = _retry_on_failure(create_github_repo, task_name, True)
    repo_url = f"https://github.com/{REPO_OWNER}/{repo_name}"
    logger.info(f"Created repo: {repo_url}")

    repo_obj = _get_repo_obj(repo_name)

    # Step 2: Push base files to main
    success = _retry_on_failure(
        upload_files_batch, repo_obj, base_repo_files, "Initial project setup", "main"
    )
    if not success:
        raise RuntimeError(f"Failed to push base files to main. Repo created: {repo_url}")

    # Step 3: Create branch
    _retry_on_failure(create_branch_from_main, repo_obj, branch_name)

    # Step 4: Push PR files to branch
    success = _retry_on_failure(
        upload_pr_files_to_branch,
        repo_obj,
        branch_name,
        pr_data.get("modified_files", {}),
        pr_data.get("added_files", {}),
        pr_data.get("deleted_files", []),
        f"feat: {pr_data.get('pr_title', 'Add feature')}",
    )
    if not success:
        raise RuntimeError(f"Failed to push PR files to branch. Repo: {repo_url}, Branch: {branch_name}")

    # Step 5: Open PR
    pr_url = _retry_on_failure(
        open_pull_request,
        repo_obj,
        branch_name,
        pr_data.get("pr_title", "Feature implementation"),
        pr_data.get("pr_description", ""),
    )

    return repo_url, pr_url
