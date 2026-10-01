"""Add Galmuri7 Korean GBA wrapper UI to the verified v2 game translation."""
from pathlib import Path
import csv, hashlib, json, shutil, struct
import numpy as np
from analyze_rom import ROM, custom_lz
from build_test_patch import compress, glyph
from ips import ips_extended, apply_patch
from audit_kana import wrapper_glyph
from wrapper_ko import MESSAGES, EXTRA_TEXT
from rom_delivery import copy_to_desktop

from paths import WORK as HERE, FONTS, ASSETS, FINAL, STEM, MGBA
OUT=FINAL
ENGINE_SLOT,ENGINE_SLOT_END=0x17380,0x1bd49
FILLER_START,FILLER_END=0x1c200,0x400000


def main():
    OUT.mkdir(exist_ok=True)
    original=ROM.read_bytes()
    base=(HERE/'korean_text_v2/Palthena_Korean_Text_v2.gba').read_bytes()
    base_meta=json.loads((HERE/'korean_text_v2/build.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(base).hexdigest()==base_meta['patched_sha256']
    engine,_=custom_lz(base,0x17380,0x824c)
    audit=json.loads((HERE/'static_kana_audit/audit.json').read_text(encoding='utf-8'))
    assert set(MESSAGES)=={r['id'] for r in audit['messages'] if r['kana']}
    # Copy every message first, including empty and icon-only helper scripts.
    old_scripts={r['id']:base[int(r['offset'],16):int(r['end'],16)] for r in audit['messages']}
    chars=sorted(set(EXTRA_TEXT+''.join(s for lines in MESSAGES.values() for x,y,s in lines)))
    specials=set(range(0x92,0x98))|{0x9a}
    available=[c for c in range(0x0b,0xff) if c not in specials and c!=0x20]
    codes={' ':0x20}|dict(zip([c for c in chars if c!=' '],available))
    assert len(codes)==len(chars)
    # Retain the fixed blank/cursor tiles 1B8..1BB; pack 3 monochrome glyphs
    # into each remaining tile using the original palette planes 1,2,3.
    font=bytearray(engine[0xbd0:0xbd0+0x900])
    # The frame painter also emits tile IDs directly (1BC fill, 1E2..1E6
    # edges), bypassing the character lookup. Keep those original tiles.
    reserved_tiles=set(range(5))|set(range(0x1e2-0x1b8,0x1e7-0x1b8))
    free_tiles=[i for i in range(72) if i not in reserved_tiles]
    for tile in free_tiles:font[tile*32:(tile+1)*32]=b'\x88'*32
    lookup=[0x11bc]*256
    bitmaps={code:glyph(ch) for ch,code in codes.items() if ch!=' '}
    for code in specials:
        lookup[code]=struct.unpack_from('<H',base,0x17d0+code*2)[0]
        assert (lookup[code]&1023)-0x1b8 in reserved_tiles
    assert len(bitmaps)<=len(free_tiles)*3
    for slot,(code,rows) in enumerate(sorted(bitmaps.items())):
        tile,plane=free_tiles[slot//3],slot%3
        lookup[code]=(0x1b8+tile)|((plane+1)<<12)
        for y in range(8):
            for x in range(8):
                pos=tile*32+y*4+x//2;shift=(x%2)*4
                pixel=8|(((rows[y]>>(7-x))&1)<<plane)
                font[pos]|=pixel<<shift
    # Keep the original 4 MiB size. 0x1C200.. is filler after the EEPROM_V124
    # library; wiping it leaves boot/title/name-entry frames identical.
    font_rom_offset=FILLER_START
    rom=bytearray(base)
    assert len(rom)==len(original)==0x400000
    rom[font_rom_offset:font_rom_offset+len(font)]=font
    # Original lookup has 254 entries; preserve the following message bytes.
    struct.pack_into('<254H',rom,0x17d0,*lookup[:254])
    rom[0x17c0:0x17d0]=bytes(codes[c] for c in '0123456789ABCDEF')
    position=font_rom_offset+len(font)
    records=[]
    for ident in range(1,60):
        entry=0x27cc+ident*8
        x0,y0,w,h=rom[entry:entry+4]
        body=bytearray()
        def enc(text):return bytes(codes[c] for c in text)
        def at(x,y):return bytes([5,(x-x0)&255,(y-y0)&255])
        if ident in (2,3):
            # Preserve original yes/no highlight semantics and cursor cells.
            if ident==2:body+=at(10,14)+enc(' ')+bytes([3])+enc('예 ')+enc('  ')+bytes([2,4,2])+enc('아니요')
            else:body+=at(10,14)+bytes([4])+enc('     ')+bytes([3])+enc('아니요')+at(11,14)+bytes([2])+enc('예 ')
            text=['예 / 아니요']
        elif ident in (22,23,24):
            # 1P/2P/cancel retain their original tile positions and flag codes.
            body+=at(7,18)
            if ident==22:body+=bytes([4,2])+enc('1P')+bytes([3])+enc('   2P   취소    ')
            elif ident==23:body+=bytes([3])+enc(' 1P  ')+bytes([4,2])+enc('2P')+bytes([3])+enc('   취소    ')
            else:body+=bytes([3])+enc(' 1P   2P  ')+bytes([4,2])+enc('취소    ')
            text=['1P / 2P / 취소']
        elif ident in MESSAGES:
            lines=MESSAGES[ident]
            if w and h:
                left=min([x0]+[x for x,y,s in lines]);right=max([x0+w]+[x+len(s)+1 for x,y,s in lines])
                x0=left;w=right-left
                assert right<=30
                rom[entry]=x0;rom[entry+2]=w
            for i,(x,y,s) in enumerate(lines):
                assert 0<=x and x+len(s)<=30 and 0<=y<20,(ident,s)
                if w and h:
                    assert x0<x and x+len(s)<x0+w,(ident,'horizontal frame overlap',s)
                    assert (y0<y<y0+h-1) if h>2 else (y0<=y<y0+h),(ident,'vertical frame overlap',s)
                style=3 if ident==7 and i>0 else (1 if i==0 else 2)
                body+=at(x,y)+bytes([style])+enc(s)
            text=[s for x,y,s in lines]
        else:
            body+=old_scripts[ident][:-1];text=[]
        body.append(255)
        rom[position:position+len(body)]=body
        struct.pack_into('<I',rom,entry+4,0x08000000+position)
        records.append({'id':ident,'script_offset':hex(position),'bytes':len(body),'translated':ident in MESSAGES,'text':text})
        position+=len(body)
    # Remove unreferenced old Japanese message bodies. Table entry zero overlaps
    # the old last message, so leave the table itself intact.
    rom[0x19cc:0x27cc]=b'\xff'*(0x27cc-0x19cc)
    engine_new=bytearray(engine)
    assert struct.unpack_from('<3I',engine,0x4e0)==(0x06000bd0,0x06007700,0x84000240)
    struct.pack_into('<I',engine_new,0x4e0,0x08000000+font_rom_offset)
    assert position<=FILLER_END
    packed=compress(engine_new)
    # Re-packed engine goes back into its original slot; the 0x128 pointer
    # stays at the original 0x08017380.
    engine_offset=ENGINE_SLOT
    assert len(packed)<=ENGINE_SLOT_END-ENGINE_SLOT
    rom[engine_offset:engine_offset+len(packed)]=packed
    assert struct.unpack_from('<I',rom,0x128)[0]==0x08000000+ENGINE_SLOT
    unpacked,consumed=custom_lz(rom,engine_offset,len(engine))
    assert unpacked==engine_new and consumed==engine_offset+len(packed)
    game,_=custom_lz(rom,0x2ae0,108472)
    assert game==(HERE/'korean_text_v2/edited_payload.bin').read_bytes()
    patch=ips_extended(original,rom);assert apply_patch(original,patch)==rom
    target=OUT/(STEM+'.gba')
    target.write_bytes(rom)
    (OUT/(STEM+'.ips')).write_bytes(patch)
    (OUT/'wrapper_font.bin').write_bytes(font)
    (OUT/'engine.bin').write_bytes(engine_new)
    report={'original_sha256':hashlib.sha256(original).hexdigest(),'patched_sha256':hashlib.sha256(rom).hexdigest(),
            'rom_bytes':len(rom),'engine_rom_offset':hex(engine_offset),'engine_compressed_bytes':len(packed),
            'font_rom_offset':hex(font_rom_offset),'wrapper_glyphs':len(bitmaps),'korean_glyphs':sum('가'<=c<='힣' for c in chars),
            'translated_messages':len(MESSAGES),'codes':codes,'messages':records,'game_payload_identical_to_v2':True,'ips_roundtrip':True}
    (OUT/'build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    with (OUT/'공통메뉴_번역.csv').open('w',encoding='utf-8-sig',newline='') as f:
        wcsv=csv.writer(f);wcsv.writerow(['ID','원문','번역'])
        for row in records:
            if row['translated']:
                old=next(r['text'] for r in audit['messages'] if r['id']==row['id'])
                wcsv.writerow([row['id'],old,'\n'.join(row['text'])])
    shutil.copyfile(FONTS/'Galmuri-OFL.md',OUT/'Galmuri-OFL.md')
    desktop=copy_to_desktop(target)
    (OUT/'desktop_copy.json').write_text(json.dumps({'path':str(desktop),'sha256':report['patched_sha256']},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Built', STEM, ':',len(rom),'bytes;',len(MESSAGES),'messages;',len(bitmaps),'glyphs')


if __name__=='__main__':main()
