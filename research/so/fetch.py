import json, sys, time, urllib.request, os
def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 300:
        return json.load(open(path))
    last=None
    for a in range(3):
        try:
            req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Accept-Encoding':'identity'})
            with urllib.request.urlopen(req, timeout=45) as r:
                d=json.load(r)
            json.dump(d, open(path,'w'))
            return d
        except Exception as e:
            last=e; time.sleep(3*(a+1))
    print("FAIL", url, last, file=sys.stderr); return None
if __name__ == '__main__':
    ids = sys.argv[1:]
    for i in ids:
        cb = f"&cb={time.time()}"
        get(f"https://api.stackexchange.com/2.3/questions/{i}?site=stackoverflow&filter=withbody{cb}", f"so/q_{i}.json")
        time.sleep(1.2)
        get(f"https://api.stackexchange.com/2.3/questions/{i}/answers?site=stackoverflow&filter=withbody&sort=votes{cb}", f"so/a_{i}.json")
        time.sleep(1.2)
        print("done", i, flush=True)
