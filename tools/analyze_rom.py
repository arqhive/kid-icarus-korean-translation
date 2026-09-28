from pathlib import Path
import json, hashlib, re, struct

from paths import ROM, WORK as OUT


def custom_lz(b, start, size):
    pos=start; out=bytearray()
    while len(out)<size:
        flags=b[pos]; pos+=1
        for bit in range(7,-1,-1):
            if flags & (1<<bit):
                out.append(b[pos]); pos+=1
            else:
                a,c=b[pos:pos+2]; pos+=2
                length=a>>4
                if length==0:
                    length=b[pos]+16; pos+=1
                length+=2
                dist=((a&15)<<8)+c+1
                if dist>len(out): raise ValueError((hex(pos),dist,len(out)))
                for _ in range(length):out.append(out[-dist])
            if len(out)>=size:break
    return bytes(out[:size]),pos

def lz10(b, start, limit=0x80000):
    if b[start] != 0x10:
        raise ValueError('signature')
    size = int.from_bytes(b[start+1:start+4], 'little')
    if not 32 <= size <= limit:
        raise ValueError('size')
    pos = start + 4
    out = bytearray()
    while len(out) < size:
        flags = b[pos]; pos += 1
        for bit in range(7, -1, -1):
            if flags & (1 << bit):
                v = b[pos] << 8 | b[pos+1]; pos += 2
                length, dist = (v >> 12) + 3, (v & 0xfff) + 1
                if dist > len(out): raise ValueError('distance')
                for _ in range(length): out.append(out[-dist])
            else:
                out.append(b[pos]); pos += 1
            if len(out) >= size: break
    if len(out) != size: raise ValueError('overrun')
    return bytes(out), pos

def main():
    b = ROM.read_bytes()
    boot, end=custom_lz(b,0x17380,0x824c)
    (OUT/'boot_vram.bin').write_bytes(boot)
    print('boot custom LZ',hex(end),len(boot))
    payload, end=custom_lz(b,0x2ae0,0x2f187b8-0x2efe000)
    (OUT/'game_payload.bin').write_bytes(payload)
    print('game custom LZ',hex(end),len(payload))
    for sig in [b'NINTENDO',b'*NINTENDO-HVC*',b'GAME',b'PTM',b'PAL',b'OVER']:
        print('payload',sig,[hex(m.start()) for m in re.finditer(re.escape(sig),payload)][:20])
    results=[]
    for off in range(0,0x1c400,4):
        if b[off] != 0x10: continue
        try: data,end=lz10(b,off)
        except (ValueError,IndexError): continue
        if len(data) < 128: continue
        name=f'lz_{off:06x}.bin'
        (OUT/name).write_bytes(data)
        row={'offset':hex(off),'end':hex(end),'compressed_bytes':end-off,'expanded_bytes':len(data),'file':name}
        results.append(row)
        print(row)
        for sig in [b'NINTENDO',b'NES\x1a',b'FDS\x1a',b'GAME',b'PTM']:
            p=data.find(sig)
            if p>=0: print('  signature',sig,hex(p))
    report={'file':str(ROM),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'title':b[0xa0:0xac].decode('ascii').rstrip('\0'),'game_code':b[0xac:0xb0].decode('ascii'),'lz10_candidates':results,
        'custom_lz':[
            {'source_offset':'0x2ae0','source_end_exclusive':'0x1737f','expanded_bytes':108472,'file':'game_payload.bin'},
            {'source_offset':'0x17380','source_end_exclusive':'0x1bd49','expanded_bytes':33356,'file':'boot_vram.bin'}],
        'scope':'Original ROM extraction only; final verification is performed separately.'}
    (OUT/'scan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
