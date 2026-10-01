# Design Notes: Testing Perspective (HW03a)

## How I split the code up, and why

Before writing anything, I split the program into two kinds of functions: ones that talk to the network, and ones that just take data that's already been fetched and compute something from it. `extract_repo_names()` and `count_commits()` never call `requests.get` themselves — they just take a plain Python list (the kind of thing you'd get back from parsing JSON) and return an answer. That means I can test them by just typing in a small fake list by hand, with no mocking library and no network involved at all. Almost all of my test cases ended up being this kind of test, and they run in milliseconds.

The only functions that actually touch the network are `_fetch_paginated()`, `get_repo_names()`, and `get_commit_count()`. Since those can't be tested with plain data, I used Python's `unittest.mock` to fake out `requests.get()` so I could still test them without ever making a real API call. This was the single biggest decision I made for testability, and it came directly from thinking like a tester before writing any code: if I know I'm going to need to test this a lot, I should design it so most of that testing doesn't depend on the network at all.

## The pagination bug I almost missed

The instructions make it sound like `/users/<ID>/repos` just gives you "a list" and `/repos/<ID>/<REPO>/commits` gives you "a list of commits," and my first instinct as a developer was to just read that list and count it. But GitHub's API only returns 30 items per page by default, and caps out at 100 even if you ask for more. If I'd shipped that first version, it would have silently under-counted commits for any repo with more than 30 commits, and it would have passed every test I could think to write with a small example — because small examples never hit the page boundary.

This is exactly the kind of thing a "tester" mindset catches that a "developer" mindset doesn't: it's not a bug you'd notice by reading the code, it's a bug you'd only notice by asking "what happens at the edges of what this API promises to do?" I ended up writing `_fetch_paginated()` to keep requesting pages until it gets back a page with fewer than 100 items, and I wrote tests that specifically simulate a full 100-item page followed by a partial page, to make sure the looping logic actually stops when it's supposed to.

## The "empty repository" edge case

While reading GitHub's API docs to figure out the pagination behavior, I found another edge case I wouldn't have thought to test for on my own: if a repository has zero commits, GitHub doesn't return an empty list — it returns an HTTP 409 error with a message saying the repository is empty. If I hadn't caught that, my program would have crashed (or reported a confusing error) for any brand-new, empty repo, instead of just correctly reporting "0 commits." I added a specific case for this in the code and a specific test for it, rather than just letting all non-200 responses be treated as one generic error.

## Why almost none of my tests touch the real API

The assignment specifically warns that GitHub will start rejecting requests if you make too many of them in a short time. That warning shaped my whole testing approach: if my test suite made a real API call every time I ran it, then running my tests often (which you're supposed to do) would actually work against me by burning through my rate limit, and worse, my tests would become flaky — sometimes failing not because my code is wrong, but because GitHub is temporarily blocking me. That's a bad property for a test suite to have, especially one that's supposed to run automatically in CI on every commit.

So instead, all 20 of my unit tests use mocked fake responses instead of the real API, and I only ran the actual program against the live API a couple of times by hand, to sanity check the mocked tests were faking realistic data. This felt like the right trade-off: the tests catch real logic bugs (pagination, empty repos, malformed responses) without ever depending on GitHub actually being reachable or within rate limits at test time.

## What I'd still want to test more, given more time

I didn't write a test for what happens if the GitHub user ID itself doesn't exist at all (a 404 on the very first `/repos` call) — I do handle it (it raises an `HTTPError`), but I didn't spend time deciding what the *caller* should see in that case (a friendlier error message vs. letting the exception bubble up). I also didn't test what happens if GitHub's response is valid JSON but missing an expected field entirely (e.g., a repo object with no `"name"` key) — right now that would raise a raw `KeyError` rather than a clear error message, which is something worth hardening before building further on top of this next week.
