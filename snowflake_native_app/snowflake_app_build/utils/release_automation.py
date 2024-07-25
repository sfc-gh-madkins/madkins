import requests
import json
import sys
import os

def create_github_release(token, repo, tag, target_commitish, release_name, body):
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {
        "tag_name": tag,
        "target_commitish": target_commitish,
        "name": release_name,
        "body": body,
        "draft": False,
        "prerelease": False,
        "generate_release_notes": False
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    token = os.getenv('GITHUB_TOKEN')  # Get the GitHub token from environment variable
    print(token)
    repo = "sfc-gh-madkins/snowflake_native_app"  # Replace with your GitHub repo (e.g., 'username/repository')
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1.0.0"  # Release tag from argument or default
    target_commitish = "master"  # The branch or commit SHA to attach the release to
    release_name = "Release " + tag
    body = "Description of the release"

    release_info = create_github_release(token, repo, tag, target_commitish, release_name, body)
    print(release_info)
