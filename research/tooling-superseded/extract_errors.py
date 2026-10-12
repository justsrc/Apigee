import re,sys,os

def sections(t):
    parts=re.split(r'\n(#{2,4}) ',t)
    out=[]
    for i in range(1,len(parts),2):
        body=parts[i+1]
        nl=body.find('\n')
        title=(parts[i]+' '+(body[:nl] if nl>0 else body)).strip()
        out.append((title, body[nl+1:] if nl>0 else ''))
    return out

ROW=re.compile(r'<tr>\s*<td><code translate="no" dir="ltr">([^<]+)</code></td>\s*<td>(?:<p><strong>)?(?:<code translate="no" dir="ltr">)?([^<]*)')

def main(fn):
    t=open(fn).read()
    sec=None
    print("########## "+os.path.basename(fn))
    for h,body in sections(t):
        iserr = ('Error reference' in h) or bool(re.match(r'#{3,4} (Runtime errors|Deployment errors|Fault variables|JWT token-specific)',h))
        if iserr:
            sec=h
            print("  -- "+h)
        elif sec and re.match(r'#{2,4} ',h):
            sec=None
        if sec and not ('Error reference' in h):
            for m in ROW.finditer(body):
                code=m.group(1).strip(); st=m.group(2).strip().rstrip(')(').strip()
                print("  %-62s %s" % (code,st))
            for m in re.finditer(r'^\|\s*`([^`]+)`\s*\|',body,re.M):
                print("  [dep] "+m.group(1).strip())

for p in sys.argv[1:]:
    main(p)