#!/usr/bin/env python3
import requests
import sys
from datetime import datetime

# GitHub API settings
GITHUB_API = "https://api.github.com"
TOKEN = "your_personal_access_token_here"  # Replace with your GitHub PAT
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Repo settings
REPO_OWNER = "your_username"  # Replace with your GitHub username
REPO_NAME = "utils-index"     # Replace with your repo name
README_PATH = "README.md"     # Path to README in repo

def create_gist(filename):
    """Create a public gist from a file and return its URLs."""
    with open(filename, "r") as f:
        content = f.read()
    
    gist_data = {
        "description": f"Utility script: {os.path.basename(filename)}",
        "public": True,  # Public gists for discoverability
        "files": {os.path.basename(filename): {"content": content}}
    }
    
    response = requests.post(f"{GITHUB_API}/gists", json=gist_data, headers=HEADERS)
    if response.status_code != 201:
        print(f"Failed to create gist: {response.text}")
        sys.exit(1)
    
    gist = response.json()
    return gist["html_url"], gist["files"][os.path.basename(filename)]["raw_url"]

def get_readme_sha():
    """Get the current README's SHA for updating it."""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{README_PATH}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch README: {response.text}")
        sys.exit(1)
    return response.json()["sha"]

def update_readme(script_name, purpose, gist_url, raw_url):
    """Update the README on GitHub with a new table entry."""
    # Fetch current README content
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{README_PATH}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch README: {response.text}")
        sys.exit(1)
    
    import base64
    current_content = base64.b64decode(response.json()["content"]).decode("utf-8")
    sha = response.json()["sha"]
    
    # Split into lines and find table to insert new row
    lines = current_content.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("| `") and not line.strip().startswith("|----"):  # Table row
            new_row = f"| `{script_name}` | {purpose} | [Gist]({gist_url}) | [Raw]({raw_url}) |"
            lines.insert(i + 1, new_row)
            break
    
    # Update the date
    today = datetime.now().strftime("%B %d, %Y")
    for i, line in enumerate(lines):
        if line.startswith("Last updated:"):
            lines[i] = f"Last updated: {today}"
            break
    
    new_content = "\n".join(lines) + "\n"  # Ensure trailing newline
    
    # Push updated README
    update_data = {
        "message": f"Add {script_name} to README",
        "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    response = requests.put(url, json=update_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to update README: {response.text}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: script.py <filename> <purpose>")
        sys.exit(1)
    
    filename = sys.argv[1]
    purpose = sys.argv[2]
    
    if not os.path.isfile(filename):
        print(f"Error: {filename} not found")
        sys.exit(1)
    
    # Create gist and get URLs
    gist_url, raw_url = create_gist(filename)
    script_name = os.path.basename(filename)
    
    # Update README directly on GitHub
    update_readme(script_name, purpose, gist_url, raw_url)
    
    print(f"Added {script_name} to README. Gist URL: {gist_url}")

if __name__ == "__main__":
    main()
