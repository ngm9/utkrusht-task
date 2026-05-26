import re
import os
import random
import string
from dotenv import load_dotenv
import logging
from github import Github, InputGitTreeElement

logger = logging.getLogger(__name__)

# Load environment variables from local .env file
load_dotenv()

REPO_OWNER = os.getenv("REPO_OWNER")
GITHUB_UTKRUSHTAPPS_TOKEN = os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN")

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def create_github_template_repo(base_name: str, is_private: bool = True) -> str:
    """Create a new GitHub template repository for the task under the organization, public by default."""
    try:
        logger.info(f"Creating GitHub template repo with owner: {REPO_OWNER}, base name: {base_name}")
        
        github = Github(GITHUB_UTKRUSHTAPPS_TOKEN)
        repo_name = slugify(base_name)
        if not repo_name:
            repo_name = "task-template"
        # Try to create the repo, if it exists, append a short random string
        org = github.get_organization(REPO_OWNER)
        final_repo_name = repo_name
        for _ in range(3):
            try:
                repo = org.create_repo(
                    name=final_repo_name,
                    private= is_private, 
                    description=f"Assessment task template repository - Use this template to create new repositories",
                    auto_init=True,
                    is_template=True  # This makes it a template repository
                )
                return final_repo_name
            except Exception as e:
                if 'name already exists' in str(e).lower():
                    # Append a short random string and try again
                    rand_str = ''.join(random.choices(string.hexdigits.lower(), k=4))
                    final_repo_name = f"{repo_name}-{rand_str}"
                    logger.warning(f"Repo name collision, trying: {final_repo_name}")
                else:
                    logger.error(f"Error creating template repository: {str(e)}")
                    raise
        raise Exception(f"Could not create a unique template repo name after 3 attempts.")
    except Exception as e:
        logger.error(f"Error creating template repository: {str(e)}")
        raise

def create_github_repo(base_name: str, is_public: bool = True) -> str:
    """Create a new GitHub repository for the task under the organization, public by default."""
    try:
        logger.info(f"Creating GitHub repo with owner: {REPO_OWNER}, base name: {base_name}")
        
        github = Github(GITHUB_UTKRUSHTAPPS_TOKEN)
        repo_name = slugify(base_name)
        if not repo_name:
            repo_name = "task"
        # Try to create the repo, if it exists, append a short random string
        org = github.get_organization(REPO_OWNER)
        final_repo_name = repo_name
        for _ in range(3):
            try:
                repo = org.create_repo(
                    name=final_repo_name,
                    private=not is_public,  # Set to public by default
                    description=f"Assessment task repository",
                    auto_init=True
                )
                logger.info(f"Created {'public' if is_public else 'private'} repository: {final_repo_name}")
                return final_repo_name
            except Exception as e:
                if 'name already exists' in str(e).lower():
                    # Append a short random string and try again
                    rand_str = ''.join(random.choices(string.hexdigits.lower(), k=4))
                    final_repo_name = f"{repo_name}-{rand_str}"
                    logger.warning(f"Repo name collision, trying: {final_repo_name}")
                else:
                    logger.error(f"Error creating repository: {str(e)}")
                    raise
        raise Exception(f"Could not create a unique repo name after 3 attempts.")
    except Exception as e:
        logger.error(f"Error creating repository: {str(e)}")
        raise

def create_repo_from_template(template_repo_name: str, new_repo_name: str, is_private: bool = True, owner: str = None) -> str:
    """Create a new repository from a template repository."""
    try:
        github = Github(GITHUB_UTKRUSHTAPPS_TOKEN)
        
        # Get the template repository
        template_repo = github.get_repo(f"{REPO_OWNER}/{template_repo_name}")
        
        # Determine the owner for the new repo (can be user or organization)
        if owner is None:
            # Create under the same organization
            org = github.get_organization(REPO_OWNER)
            new_repo = org.create_repo_from_template(
                template=template_repo,
                name=new_repo_name,
                private=is_private,
                description=f"Repository created from template {template_repo_name}"
            )
        else:
            # Create under a specific user/organization
            target_owner = github.get_user(owner) if owner != REPO_OWNER else github.get_organization(REPO_OWNER)
            new_repo = target_owner.create_repo_from_template(
                template=template_repo,
                name=new_repo_name,
                private=is_private,
                description=f"Repository created from template {template_repo_name}"
            )
        
        logger.info(f"Created {'private' if is_private else 'public'} repository '{new_repo_name}' from template '{template_repo_name}'")
        return new_repo.name
        
    except Exception as e:
        logger.error(f"Error creating repository from template: {str(e)}")
        raise

def revoke_push_access(base_name: str, github_username: str):
    try:
        github = Github(GITHUB_UTKRUSHTAPPS_TOKEN)
        repo = github.get_repo(f"{REPO_OWNER}/{base_name}")
        # Update collaborator permission to 'pull' instead of removing
        repo.add_to_collaborators(github_username, permission='pull')
        logger.info(f"Changed {github_username} to read-only access in {base_name}")
    except Exception as e:
        logger.error(f"Error revoking push access: {str(e)}")
        raise

def remove_collaborator(base_name: str, github_username: str):
    try:
        github = Github(GITHUB_UTKRUSHTAPPS_TOKEN)
        repo = github.get_repo(f"{REPO_OWNER}/{base_name}")
        repo.remove_collaborator(github_username)
        logger.info(f"Removed collaborator {github_username} from {base_name}")
    except Exception as e:
        logger.error(f"Error removing collaborator: {str(e)}")
        raise

def upload_files_batch(repo_obj, files_dict: dict, commit_message: str = "Initial commit", branch: str = "main") -> bool:
    """
    Upload multiple files to a GitHub repository in a single commit.
    
    Args:
        repo_obj: PyGithub repository object
        files_dict: Dictionary with file paths as keys and content as values
        commit_message: Commit message for the batch upload
        branch: Branch name to commit to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Uploading {len(files_dict)} files in a single commit")
        
        # Get the reference to the branch
        ref = repo_obj.get_git_ref(f"heads/{branch}")
        base_commit = repo_obj.get_git_commit(ref.object.sha)
        base_tree = base_commit.tree
        
        # Create a list of InputGitTreeElement objects for all files
        element_list = []
        for file_path, content in files_dict.items():
            # Strip leading slash from file path
            clean_file_path = file_path.lstrip('/')
            
            # Convert content to string if it's a dict
            if isinstance(content, dict):
                import json
                content_str = json.dumps(content, indent=2, ensure_ascii=False)
            else:
                content_str = str(content)
            
            # Create blob for the file content
            blob = repo_obj.create_git_blob(content_str, "utf-8")
            
            # Add to element list using InputGitTreeElement
            element = InputGitTreeElement(
                path=clean_file_path,
                mode="100644",  # File mode (normal file)
                type="blob",
                sha=blob.sha
            )
            element_list.append(element)
            logger.info(f"Prepared file: {clean_file_path}")
        
        # Create a new tree with all files
        new_tree = repo_obj.create_git_tree(element_list, base_tree)
        
        # Create a new commit
        new_commit = repo_obj.create_git_commit(
            message=commit_message,
            tree=new_tree,
            parents=[base_commit]
        )
        
        # Update the reference to point to the new commit
        ref.edit(new_commit.sha)
        
        logger.info(f"Successfully uploaded {len(files_dict)} files in a single commit")
        return True
        
    except Exception as e:
        logger.error(f"Error uploading files in batch: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False