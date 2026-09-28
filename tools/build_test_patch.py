"""Custom LZ encoder, Galmuri glyph loader and fixed-size IPS helpers."""
from collections import defaultdict, deque
from paths import FONTS


def compress(data):
    data=bytes(data)
    index=defaultdict(deque);matches=[]
    for p in range(len(data)):
        candidates=index[data[p:p+3]]
        while candidates and candidates[0]<p-4096:candidates.popleft()
        best=0;distance=0;limit=min(273,len(data)-p)
        if limit>=3:
            for q in reversed(candidates):
                n=3
                while n<limit and data[q+n]==data[p+n]:n+=1
                if n>best:best=n;distance=p-q
                if n==limit:break
        matches.append((best,distance));candidates.append(p)
    # Minimize token bytes plus amortized flag cost, considering every match length.
    cost=[0]*(len(data)+1);choice=[1]*len(data)
    for p in range(len(data)-1,-1,-1):
        cost[p]=9+cost[p+1]
        maximum,_=matches[p]
        for lo,hi,price in [(3,min(17,maximum),17),(18,maximum,25)]:
            if hi<lo:continue
            following=cost[p+lo:p+hi+1];cheapest=min(following)
            if price+cheapest<cost[p]:
                cost[p]=price+cheapest;choice[p]=lo+following.index(cheapest)
    out=bytearray();p=0
    while p<len(data):
        flag_pos=len(out);out.append(0);flags=0
        for bit in range(7,-1,-1):
            if p>=len(data):break
            best=choice[p];distance=matches[p][1]
            if best>=3:
                d=distance-1
                if best<=17:out.extend((((best-2)<<4)|(d>>8),d&255))
                else:out.extend((d>>8,d&255,best-18))
                advance=best
            else:
                flags|=1<<bit;out.append(data[p]);advance=1
            p+=advance
        out[flag_pos]=flags
    return bytes(out)

def glyph(ch):
    text=(FONTS/'Galmuri7.bdf').read_text(encoding='utf-8')
    marker='ENCODING '+str(ord(ch))+'\n'
    p=text.index(marker);end=text.index('ENDCHAR',p)
    block=text[p:end].splitlines();bbx=next(x for x in block if x.startswith('BBX')).split()
    w,h,x,y=map(int,bbx[1:]);rows=block[block.index('BITMAP')+1:]
    assert w+x<=8 and h+y<=8 and x>=0 and y>=0
    # Baseline at the bottom of the seven-pixel cap height, final tile row blank.
    pixels=bytearray(8)
    for j,row in enumerate(rows):pixels[7-h-y+j]=int(row,16)>>x
    return bytes(pixels)

def ips(original,modified):
    out=bytearray(b'PATCH');i=0
    while i<len(modified):
        if original[i]==modified[i]:i+=1;continue
        start=i;i+=1
        while i<len(modified) and i-start<65535:
            if original[i]==modified[i] and original[i:i+8]==modified[i:i+8]:break
            i+=1
        out.extend(start.to_bytes(3,'big'));out.extend((i-start).to_bytes(2,'big'));out.extend(modified[start:i])
    out.extend(b'EOF');return bytes(out)

def apply_ips(original,patch):
    assert patch[:5]==b'PATCH';out=bytearray(original);p=5
    while patch[p:p+3]!=b'EOF':
        off=int.from_bytes(patch[p:p+3],'big');size=int.from_bytes(patch[p+3:p+5],'big');p+=5
        assert size>0
        out[off:off+size]=patch[p:p+size];p+=size
    return bytes(out)
