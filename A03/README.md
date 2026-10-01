# GitHubApi-hw03a

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/samahkeshiro/SSW567/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/samahkeshiro/SSW567/tree/main)

Given a GitHub user ID, this program retrieves the list of repositories
owned by that user, along with the number of commits in each repository,
using GitHub's public REST API (no authentication needed).

## Files

- `github_repo_stats.py` — the main program. Also runnable directly:
  `python3 github_repo_stats.py <github-username>`
- `test_github_repo_stats.py` — unit tests (all mocked; no real network
  calls or GitHub API rate limit usage).
- `requirements.txt` — dependencies (`requests`).
- `DESIGN_NOTES.md` — write-up on the design/testing decisions made for
  this assignment.
- CI: tests run on CircleCI on every push, configured in .circleci/config.yml at the repository root.

## Running it yourself

```bash
pip install -r requirements.txt
python3 github_repo_stats.py richkempinski
```

Expected output looks like:

```
Repo: hellogitworld Number of commits: 19
...
```

(Exact repo list/commit counts depend on the live state of that user's
GitHub account at the time you run it.)

## Running the tests

```bash
python3 -m unittest test_github_repo_stats.py -v
```

All 20 tests run in well under a second, since none of them make a real
network call — see `DESIGN_NOTES.md` for why that was a deliberate design
choice.
