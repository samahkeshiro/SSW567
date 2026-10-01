import io
import unittest
import requests
from unittest.mock import patch, MagicMock

import github_repo_stats as ghs

# Pure logic tests -- no mocking, no network, just plain data in/out.

class TestExtractRepoNames(unittest.TestCase):
    def test_extracts_names_from_multiple_repos(self):
        sample = [{"name": "Triangle567"}, {"name": "Square567"}]
        self.assertEqual(ghs.extract_repo_names(sample), ["Triangle567", "Square567"])

    def test_empty_list_for_user_with_no_repos(self):
        self.assertEqual(ghs.extract_repo_names([]), [])

    def test_single_repo(self):
        sample = [{"name": "hellogitworld"}]
        self.assertEqual(ghs.extract_repo_names(sample), ["hellogitworld"])


class TestCountCommits(unittest.TestCase):
    def test_counts_multiple_commits(self):
        sample = [{"sha": "aaa"}, {"sha": "bbb"}, {"sha": "ccc"}]
        self.assertEqual(ghs.count_commits(sample), 3)

    def test_zero_commits_for_empty_list(self):
        self.assertEqual(ghs.count_commits([]), 0)

    def test_single_commit(self):
        self.assertEqual(ghs.count_commits([{"sha": "aaa"}]), 1)


class TestFormatRepoCommitLine(unittest.TestCase):
    def test_matches_assignment_required_format(self):
        line = ghs.format_repo_commit_line("Triangle567", 10)
        self.assertEqual(line, "Repo: Triangle567 Number of commits: 10")

    def test_zero_commits_still_formats_correctly(self):
        line = ghs.format_repo_commit_line("EmptyRepo", 0)
        self.assertEqual(line, "Repo: EmptyRepo Number of commits: 0")

# I/O layer tests -- requests.get is mocked, so no real network call is made.

def _mock_response(status_code=200, json_data=None):
    """Build a fake requests.Response-like object for use in mocks."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    if status_code >= 400 and status_code != 409:
        mock_resp.raise_for_status.side_effect = requests_http_error(status_code)
    else:
        mock_resp.raise_for_status.side_effect = None
    return mock_resp


def requests_http_error(status_code):
    error = requests.exceptions.HTTPError(f"{status_code} error")
    error.response = MagicMock(status_code=status_code)
    return error


class TestFetchPaginated(unittest.TestCase):
    @patch("github_repo_stats.requests.get")
    def test_single_page_under_100_items(self, mock_get):
        mock_get.return_value = _mock_response(200, [{"name": "a"}, {"name": "b"}])
        result = ghs._fetch_paginated("https://fake.url/repos")
        self.assertEqual(result, [{"name": "a"}, {"name": "b"}])
        mock_get.assert_called_once()

    def test_empty_repos_list_returns_empty(self):
        with patch("github_repo_stats.requests.get") as mock_get:
            mock_get.return_value = _mock_response(200, [])
            result = ghs._fetch_paginated("https://fake.url/repos")
            self.assertEqual(result, [])

    @patch("github_repo_stats.requests.get")
    def test_follows_multiple_pages_until_short_page(self, mock_get):
        # Page 1: exactly 100 items (a "full" page, so there might be more).
        # Page 2: only 30 items (a "short" page, meaning this is the last one).
        page1 = [{"name": f"repo{i}"} for i in range(100)]
        page2 = [{"name": f"repo{i}"} for i in range(100, 130)]
        mock_get.side_effect = [
            _mock_response(200, page1),
            _mock_response(200, page2),
        ]
        result = ghs._fetch_paginated("https://fake.url/repos")
        self.assertEqual(len(result), 130)
        self.assertEqual(mock_get.call_count, 2)

    @patch("github_repo_stats.requests.get")
    def test_stops_immediately_when_first_page_is_short(self, mock_get):
        mock_get.return_value = _mock_response(200, [{"name": "only_one"}])
        result = ghs._fetch_paginated("https://fake.url/repos")
        self.assertEqual(len(result), 1)
        mock_get.assert_called_once()

    @patch("github_repo_stats.requests.get")
    def test_raises_for_404_not_found(self, mock_get):
        mock_get.return_value = _mock_response(404, {"message": "Not Found"})
        with self.assertRaises(requests.exceptions.HTTPError):
            ghs._fetch_paginated("https://fake.url/users/doesnotexist12345/repos")

    @patch("github_repo_stats.requests.get")
    def test_raises_empty_repository_error_on_409(self, mock_get):
        mock_get.return_value = _mock_response(409, {"message": "Git Repository is empty."})
        with self.assertRaises(ghs.EmptyRepositoryError):
            ghs._fetch_paginated("https://fake.url/repos/user/emptyrepo/commits")


class TestGetRepoNames(unittest.TestCase):
    @patch("github_repo_stats._fetch_paginated")
    def test_returns_names_from_fetched_json(self, mock_fetch):
        mock_fetch.return_value = [{"name": "Triangle567"}, {"name": "Square567"}]
        result = ghs.get_repo_names("John567")
        self.assertEqual(result, ["Triangle567", "Square567"])
        # Confirm the correct URL shape was requested.
        called_url = mock_fetch.call_args[0][0]
        self.assertIn("John567", called_url)
        self.assertIn("/repos", called_url)

    @patch("github_repo_stats._fetch_paginated")
    def test_user_with_no_repos_returns_empty_list(self, mock_fetch):
        mock_fetch.return_value = []
        self.assertEqual(ghs.get_repo_names("SomeoneWithNoRepos"), [])


class TestGetCommitCount(unittest.TestCase):
    @patch("github_repo_stats._fetch_paginated")
    def test_returns_correct_commit_count(self, mock_fetch):
        mock_fetch.return_value = [{"sha": "a"}, {"sha": "b"}, {"sha": "c"}]
        self.assertEqual(ghs.get_commit_count("John567", "Triangle567"), 3)

    @patch("github_repo_stats._fetch_paginated")
    def test_empty_repository_returns_zero_not_an_error(self, mock_fetch):
        mock_fetch.side_effect = ghs.EmptyRepositoryError("fake url")
        self.assertEqual(ghs.get_commit_count("John567", "BrandNewEmptyRepo"), 0)


class TestGetUserRepoCommitCounts(unittest.TestCase):
    @patch("github_repo_stats.get_commit_count")
    @patch("github_repo_stats.get_repo_names")
    def test_combines_repo_names_with_their_commit_counts(self, mock_names, mock_counts):
        mock_names.return_value = ["Triangle567", "Square567"]
        mock_counts.side_effect = [10, 27]  # one value per call, in order

        result = ghs.get_user_repo_commit_counts("John567")

        self.assertEqual(result, [("Triangle567", 10), ("Square567", 27)])

    @patch("github_repo_stats.get_commit_count")
    @patch("github_repo_stats.get_repo_names")
    def test_user_with_no_repos_returns_empty_list(self, mock_names, mock_counts):
        mock_names.return_value = []
        result = ghs.get_user_repo_commit_counts("SomeoneWithNoRepos")
        self.assertEqual(result, [])
        mock_counts.assert_not_called()


# HW03b: end-to-end mocking at the requests.get boundary.

class TestMockedGitHubApi(unittest.TestCase):
    @patch("github_repo_stats.requests.get")
    def test_full_flow_prints_expected_lines(self, mock_get):
        def fake_get(url, params=None, timeout=None):
            if url.endswith("/users/John567/repos"):
                return _mock_response(200, [{"name": "Triangle567"}, {"name": "Square567"}, {"name": "EmptyRepo"}])
            if url.endswith("/repos/John567/Triangle567/commits"):
                return _mock_response(200, [{"sha": str(i)} for i in range(10)])
            if url.endswith("/repos/John567/Square567/commits"):
                return _mock_response(200, [{"sha": str(i)} for i in range(27)])
            if url.endswith("/repos/John567/EmptyRepo/commits"):
                return _mock_response(409, {"message": "Git Repository is empty."})
            raise AssertionError(f"Unexpected URL requested: {url}")

        mock_get.side_effect = fake_get
        with patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            ghs.print_user_repo_commit_counts("John567")

        self.assertEqual(fake_out.getvalue().splitlines(), [
            "Repo: Triangle567 Number of commits: 10",
            "Repo: Square567 Number of commits: 27",
            "Repo: EmptyRepo Number of commits: 0",
        ])

    @patch("github_repo_stats.requests.get")
    def test_requests_100_per_page_starting_at_page_1(self, mock_get):
        mock_get.return_value = _mock_response(200, [])
        ghs._fetch_paginated("https://fake.url/repos")
        self.assertEqual(mock_get.call_args.kwargs["params"], {"per_page": 100, "page": 1})

    @patch("github_repo_stats.requests.get")
    def test_exactly_100_items_checks_next_page_then_stops(self, mock_get):
        mock_get.side_effect = [
            _mock_response(200, [{"sha": str(i)} for i in range(100)]),
            _mock_response(200, []),
        ]
        self.assertEqual(ghs.get_commit_count("John567", "Exactly100"), 100)
        self.assertEqual(mock_get.call_count, 2)

    @patch("github_repo_stats.requests.get")
    def test_rate_limit_403_raises_http_error(self, mock_get):
        mock_get.return_value = _mock_response(403, {"message": "API rate limit exceeded"})
        with self.assertRaises(requests.exceptions.HTTPError):
            ghs.get_repo_names("John567")

    @patch("github_repo_stats.requests.get")
    def test_non_list_json_raises_value_error(self, mock_get):
        mock_get.return_value = _mock_response(200, {"message": "Not Found"})
        with self.assertRaises(ValueError):
            ghs.get_repo_names("John567")


if __name__ == "__main__":
    unittest.main(verbosity=2)
