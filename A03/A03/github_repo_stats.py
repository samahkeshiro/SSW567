import requests

GITHUB_API_BASE = "https://api.github.com"

# GitHub returns commits as an empty list for a repo with commits, but as a
# 409 Conflict with a JSON error body for a repo that has NO commits at all
# (an "empty" repository). We treat that specific case as "0 commits"
# rather than an error, since from the caller's point of view it's a
# perfectly valid, if unusual, real-world case.
class EmptyRepositoryError(Exception):
    """Raised internally when GitHub reports a repository as empty (409)."""

# I/O layer: the only functions that touch the network.

def _fetch_paginated(url, timeout=10):
    results = []
    page = 1
    while True:
        response = requests.get(
            url, params={"per_page": 100, "page": page}, timeout=timeout
        )
        if response.status_code == 409:
            raise EmptyRepositoryError(url)
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, list):
            # A non-list JSON body (e.g. {"message": "Not Found"}) means
            # something unexpected happened even though the HTTP status
            # itself didn't indicate an error.
            raise ValueError(f"Unexpected (non-list) response from {url}: {data}")

        if not data:
            break
        results.extend(data)

        if len(data) < 100:
            break
        page += 1

    return results


def get_repo_names(user_id):
    """Return a list of repository name strings owned by the given user."""
    url = f"{GITHUB_API_BASE}/users/{user_id}/repos"
    repos_json = _fetch_paginated(url)
    return extract_repo_names(repos_json)


def get_commit_count(user_id, repo_name):
    """Return the number of commits in the given user's repository."""
    url = f"{GITHUB_API_BASE}/repos/{user_id}/{repo_name}/commits"
    try:
        commits_json = _fetch_paginated(url)
    except EmptyRepositoryError:
        return 0
    return count_commits(commits_json)


# Pure logic layer: no network access, trivially testable with plain data.

def extract_repo_names(repos_json):
    """Given a parsed JSON list of GitHub repo objects, return their names."""
    return [repo["name"] for repo in repos_json]


def count_commits(commits_json):
    """Given a parsed JSON list of GitHub commit objects, return the count."""
    return len(commits_json)


# Orchestration + presentation.

def get_user_repo_commit_counts(user_id):
    """
    Return a list of (repo_name, commit_count) tuples for every repository
    owned by the given user.
    """
    return [
        (name, get_commit_count(user_id, name))
        for name in get_repo_names(user_id)
    ]


def format_repo_commit_line(repo_name, commit_count):
    """Format a single result line exactly as required by the assignment."""
    return f"Repo: {repo_name} Number of commits: {commit_count}"


def print_user_repo_commit_counts(user_id):
    """Print one formatted line per repository for the given user."""
    for name, count in get_user_repo_commit_counts(user_id):
        print(format_repo_commit_line(name, count))


if __name__ == "__main__":
    import sys
    target_user = sys.argv[1] if len(sys.argv) > 1 else "richkempinski"
    print_user_repo_commit_counts(target_user)