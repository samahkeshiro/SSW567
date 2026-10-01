import unittest
import requests

import github_repo_stats as ghs

KNOWN_USER = "richkempinski"
KNOWN_REPO = "hellogitworld"
# GitHub usernames can't contain "--", so this user can never exist.
NONEXISTENT_USER = "no--such--user-567"


# Pure logic tests -- no network, just plain data in/out.

class TestExtractRepoNames(unittest.TestCase):
    def test_extracts_names_from_multiple_repos(self):
        sample = [{"name": "Triangle567"}, {"name": "Square567"}]
        self.assertEqual(ghs.extract_repo_names(sample), ["Triangle567", "Square567"])

    def test_empty_list_for_user_with_no_repos(self):
        self.assertEqual(ghs.extract_repo_names([]), [])

    def test_single_repo(self):
        self.assertEqual(ghs.extract_repo_names([{"name": "hellogitworld"}]), ["hellogitworld"])


class TestCountCommits(unittest.TestCase):
    def test_counts_multiple_commits(self):
        self.assertEqual(ghs.count_commits([{"sha": "a"}, {"sha": "b"}, {"sha": "c"}]), 3)

    def test_zero_commits_for_empty_list(self):
        self.assertEqual(ghs.count_commits([]), 0)

    def test_single_commit(self):
        self.assertEqual(ghs.count_commits([{"sha": "a"}]), 1)


class TestFormatRepoCommitLine(unittest.TestCase):
    def test_matches_assignment_required_format(self):
        self.assertEqual(ghs.format_repo_commit_line("Triangle567", 10),
                         "Repo: Triangle567 Number of commits: 10")

    def test_zero_commits_still_formats_correctly(self):
        self.assertEqual(ghs.format_repo_commit_line("EmptyRepo", 0),
                         "Repo: EmptyRepo Number of commits: 0")


# Real GitHub API tests. Live data changes over time, so these check facts
# that should stay true rather than exact commit counts. The full listing is
# fetched once and reused to stay under GitHub's 60 requests/hour limit.

class TestRealGitHubApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = ghs.get_user_repo_commit_counts(KNOWN_USER)
        cls.counts = dict(cls.results)

    def test_known_repo_is_listed(self):
        self.assertIn(KNOWN_REPO, self.counts)

    def test_known_repo_has_commits(self):
        self.assertGreater(self.counts[KNOWN_REPO], 0)

    def test_every_result_is_name_and_non_negative_count(self):
        for name, count in self.results:
            self.assertIsInstance(name, str)
            self.assertIsInstance(count, int)
            self.assertGreaterEqual(count, 0)

    def test_single_repo_lookup_matches_full_listing(self):
        self.assertEqual(ghs.get_commit_count(KNOWN_USER, KNOWN_REPO),
                         self.counts[KNOWN_REPO])

    def test_nonexistent_user_raises_http_error(self):
        with self.assertRaises(requests.exceptions.HTTPError):
            ghs.get_repo_names(NONEXISTENT_USER)

    def test_nonexistent_repo_raises_http_error(self):
        with self.assertRaises(requests.exceptions.HTTPError):
            ghs.get_commit_count(KNOWN_USER, "no-such-repo-567xyz")


if __name__ == "__main__":
    unittest.main(verbosity=2)