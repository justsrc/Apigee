# Superseded research tooling

These were written during research by workers that needed something `fetch.sh` did not
do at the time. They are kept for provenance and are not used.

The supported path is `../fetch.sh` plus the `build_*.py` scripts one directory up. Where
these differ from `fetch.sh`, `fetch.sh` is the one that was hardened: it detects soft
404s, trims to the article container before converting, and warns on suspiciously small
extractions. The earlier versions did none of those things.

| File | Superseded by | Why |
| --- | --- | --- |
| `xfetch.sh`, `xbatch.sh` | `../fetch.sh` | No soft-404 detection, no truncation guard |
| `fetch.py`, `fetch-url.sh` | `../fetch.sh` | Same, plus a second fetch path to keep in sync |
| `extract.py` | inline in `../fetch.sh` | Separate extraction step that could drift from the fetch step |
| `extract_errors.py` | `../build_error_index.py` | Predates the HTML-table normalisation and found fewer codes |
| `linktree.sh` | `grep -oE` in `RESEARCH-RECIPE.md` | Extracts from raw HTML; the recipe method is enough |
| `verify-all.sh` | `../../tests/check_urls.sh` | Did not check response bodies, so soft 404s passed |
| `batch.sh` | `xargs -P` inline | No advantage over a one-line loop |
| `cited-urls.txt` | `../../tests/check_urls.sh` | A snapshot list rather than a live check |

`verify-all.sh` is the one to be most careful about. It checked status codes only, which
means it would have reported the eight soft-404 pages as healthy.

Do not reintroduce any of these. If `fetch.sh` cannot do something, extend `fetch.sh`
rather than adding a parallel script, which is how the two fetchers drifted in the first
place.