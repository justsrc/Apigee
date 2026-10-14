import json
import sys
import time
import urllib.request
import os
from typing import IO, cast


def get(url: str, path: str) -> dict[str, object] | None:
    if os.path.exists(path) and os.path.getsize(path) > 300:
        with open(path) as f:
            return cast(dict[str, object], json.load(f))
    last: Exception | None = None
    for a in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
            with cast(IO[bytes], urllib.request.urlopen(req, timeout=45)) as r:
                d = cast(dict[str, object], json.load(r))
            with open(path, 'w') as f:
                json.dump(d, f)
            return d
        except Exception as e:
            last = e
            time.sleep(3 * (a + 1))
    print("FAIL", url, last, file=sys.stderr)
    return None


if __name__ == '__main__':
    ids = sys.argv[1:]
    for i in ids:
        cb = f"&cb={time.time()}"
        _ = get(f"https://api.stackexchange.com/2.3/questions/{i}?site=stackoverflow&filter=withbody{cb}", f"so/q_{i}.json")
        time.sleep(1.2)
        _ = get(f"https://api.stackexchange.com/2.3/questions/{i}/answers?site=stackoverflow&filter=withbody&sort=votes{cb}", f"so/a_{i}.json")
        time.sleep(1.2)
        print("done", i, flush=True)
