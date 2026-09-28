"""Bitmap font and NES tile helpers used by the approved Korean logo."""
import numpy as np
from paths import FONTS


def bdf_glyph(ch,font,cap):
    s=(FONTS/font).read_text('utf-8');p=s.index(f'ENCODING {ord(ch)}\n');e=s.index('ENDCHAR',p)
    lines=s[p:e].splitlines();w,h,x,y=map(int,next(t for t in lines if t.startswith('BBX ')).split()[1:])
    rows=[t for t in lines[lines.index('BITMAP')+1:] if t]
    a=np.zeros((cap,12 if cap==11 else 8),dtype=np.uint8)
    for yy,row in enumerate(rows):
        n=int(row,16);bits=len(row)*4
        for xx in range(w):a[cap-h-y+yy,x+xx]=(n>>(bits-1-xx))&1
    return a

def text_mask(text,cap,sx,sy):
    font=f'Galmuri{cap}.bdf' if cap==11 else 'Galmuri7.bdf'
    parts=[]
    for ch in text:
        parts.append(np.zeros((cap,5 if cap==11 else 4),dtype=np.uint8) if ch==' ' else bdf_glyph(ch,font,cap))
    a=np.concatenate(parts,axis=1)
    nonzero=np.where(a.any(axis=0))[0];a=a[:,nonzero[0]:nonzero[-1]+1]
    return np.repeat(np.repeat(a,sy,axis=0),sx,axis=1)

def encode_tile(a):
    return bytes(sum(((int(a[y,x])>>plane)&1)<<(7-x) for x in range(8)) for plane in range(2) for y in range(8))
