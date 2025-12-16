#!/usr/bin/env python3
"""
Send Jupyter Book project metadata to portfolio repository via GitHub repository dispatch.

This script extracts project metadata from _config.yml and sends it to a portfolio
repository, triggering an update to the portfolio's project gallery.

Usage:
    python send_metadata.py <deployed_url>

Example:
    python send_metadata.py https://your-deployed-url.com
"""

from typing import Any
import yaml
import sys
import os
import json
from datetime import datetime
from urllib import request, error

def load_config() -> dict[str, Any]:
    """Load and parse _config.yml file."""
    try:
        with open("_config.yml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: _config.yml not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing _config.yml: {e}")
        sys.exit(1)


def extract_metadata(config: dict[str, Any], deployed_url: str) -> dict[str, str]:
    """Extract project metadata from config."""

    # Get basic info
    title = config.get("title", "No Title")
    description = config.get("description", "No Description")
    author = config.get("author", "No Author")
    logo_path = f"{deployed_url}_static/" + config.get("logo", "No Logo")
    
    # Get tags from project_metadata
    project_meta = config.get("project_metadata", {})
    tags = project_meta.get("tags", [])
    
    # Get current date
    current_date = datetime.now().isoformat()
    
    return {
        "title": title,
        "description": description,
        "author": author,
        "tags": tags,
        "url": deployed_url,
        "logo_path": logo_path,
        "updated": current_date
    }


def send_repository_dispatch(metadata: dict[str, str]) -> bool:
    """
    Send repository dispatch event to portfolio repository.
    
    This requires:
    - PORTFOLIO_REPO environment variable (format: "owner/repo")
    - PORTFOLIO_PAT environment variable (GitHub Personal Access Token)
    """
    portfolio_repo = os.environ.get("PORTFOLIO_REPO")
    portfolio_pat = os.environ.get("PORTFOLIO_PAT")
    
    if not portfolio_repo:
        print("Warning: PORTFOLIO_REPO environment variable not set")
        print("Skipping portfolio notification")
        return False
    
    if not portfolio_pat:
        print("Warning: PORTFOLIO_PAT environment variable not set")
        print("Skipping portfolio notification")
        return False
    
    # GitHub API endpoint for repository dispatch
    api_url: str = f"https://api.github.com/repos/{portfolio_repo}/dispatches"
    
    # Prepare dispatch payload
    payload: dict[str, Any] = {
        "event_type": "project-updated",
        "client_payload": metadata
    }
    
    # Prepare request
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {portfolio_pat}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
    }
    
    req = request.Request(
        api_url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with request.urlopen(req) as response:
            if response.status == 204:
                print(f"✓ Successfully sent metadata to {portfolio_repo}")
                print(f"  Event type: project-updated")
                print(f"  Project: {metadata['title']}")
                return True
            else:
                print(f"Warning: Unexpected response code: {response.status}")
                return False
    except error.HTTPError as e:
        print(f"Error sending repository dispatch: {e.code} {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
        return False
    except error.URLError as e:
        print(f"Error connecting to GitHub API: {e.reason}")
        return False


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python send_metadata.py <deployed_url>")
        sys.exit(1)
    
    deployed_url = sys.argv[1]
    
    # Load configuration
    print("Loading project configuration...")
    config = load_config()
    
    # Extract metadata
    print("Extracting project metadata...")
    metadata = extract_metadata(config, deployed_url)
    
    # Display metadata
    print("\nProject Metadata:")
    print(f"  Title: {metadata['title']}")
    print(f"  Description: {metadata['description']}")
    print(f"  Logo Path: {metadata['logo_path']}")
    print(f"  Author: {metadata['author']}")
    print(f"  Tags: {', '.join(metadata['tags']) if metadata['tags'] else 'None'}")
    print(f"  URL: {metadata['url']}")
    print(f"  Updated: {metadata['updated']}")
    
    # Send to portfolio
    print("\nSending to portfolio repository...")
    success = send_repository_dispatch(metadata)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
