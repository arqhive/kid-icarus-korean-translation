"""Read-only ROM audit: decompress files and render message assets, never run a game."""
from pathlib import Path
import csv, hashlib, json, re, struct, unicodedata
import numpy as np
from PIL import Image, ImageDraw
from analyze_rom import ROM, custom_lz

from paths import WORK as HERE, FONTS, ASSETS, FINAL, STEM, MGBA
OUT = HERE / 'static_kana_audit'
KANA = re.compile('[\u3041-\u3096\u30a1-\u30fa]')

# Transcribed from the extracted wrapper font atlas, not Shift-JIS/ASCII.
ROWS = [
    ' 98()N6D5B30む,へ→',
    'のに74.?へFや21っめあレル',
    'りPひなふちムそせケうんホンAサ',
    'もワわろれよまハテタコこクえイア',
    'TSRLEC+をはとてたすしさく',
    'きかおい゜モフスょカシエラーら゛',
    'ゅーるつけュッリメニトセヤェチみ',
    'ャキ└─│┐□☆ほゆ[HナヒWV',
    '、ィウゥョョ※゜ガキミ。※※※※',
]
CHARMAP = {0x20 + 16*r + c: ch for r, row in enumerate(ROWS) for c, ch in enumerate(row)}


def wrapper_glyph(rom, engine, code):
    tile = struct.unpack_from('<H', rom, 0x17d0 + code*2)[0]
    # Engine DMA descriptor at 0x4e0 copies font 0xBD0 -> VRAM 0x7700.
    # BG0 control 0x8D04 selects character base 0x4000, 4bpp.
    source = 0xbd0 + 0x4000 + (tile & 1023)*32 - 0x7700
    raw = np.frombuffer(engine[source:source+32], dtype=np.uint8)
    pixels = np.stack((raw & 15, raw >> 4), axis=1).reshape(8, 8)
    palette = np.array(struct.unpack_from('<16H', engine, 0x9b8 + (tile >> 12)*32))
    return Image.fromarray(np.uint8(palette[pixels] > 0)*255).convert('RGB')


def parse_wrapper(rom, engine, ident):
    entry = 0x27cc + ident*8
    base_x, base_y, width, height, ptr = struct.unpack_from('<BBBBI', rom, entry)
    p = start = ptr - 0x08000000
    assert 0x19cc <= p < 0x27d2
    anchor_x, anchor_y = base_x, base_y
    x, y = anchor_x, anchor_y
    cells, literal = {}, []
    while rom[p] != 255:
        at = p; v = rom[p]; p += 1
        if v in (5, 6):
            dx, dy = struct.unpack_from('<bb', rom, p); p += 2
            anchor_x, anchor_y = (base_x+dx, base_y+dy) if v == 5 else (anchor_x+dx, anchor_y+dy)
            x, y = anchor_x, anchor_y
        elif v in (0, 1, 2, 3):
            pass  # no output / palette flags
        elif v == 4:
            x += 1  # blank tile
        elif v in (7, 8, 9, 10):
            x += 1  # frame tiles, not characters
        else:
            cells[x, y] = v
            literal.append({'offset':hex(at), 'code':hex(v), 'char':CHARMAP.get(v, f'<{v:02X}>')})
            x += 1
    image = Image.new('RGB', (256, 176), 'black')
    for (x,y), v in cells.items():
        if 0 <= x < 32 and 0 <= y < 22:
            image.paste(wrapper_glyph(rom, engine, v), (x*8, y*8))
    image.resize((768,528), Image.Resampling.NEAREST).save(OUT / f'wrapper_{ident:02d}.png')
    # Diacritics occupy the row above the letter. Combine only when supported.
    lines = []
    for y in sorted({y for x,y in cells}):
        line = []
        for x in range(32):
            v = cells.get((x,y), 0x20); ch = CHARMAP.get(v, f'<{v:02X}>')
            if ch in ('゛','゜'): ch = ' '
            above = CHARMAP.get(cells.get((x,y-1)))
            if above in ('゛','゜') and KANA.search(ch):
                ch = unicodedata.normalize('NFC', ch + ('\u3099' if above == '゛' else '\u309a'))
            line.append(ch)
        s = ''.join(line).strip()
        if s: lines.append(s)
    text = '\n'.join(lines)
    return {'id':ident,'table_offset':hex(entry),'offset':hex(start),'end':hex(p+1),
            'text':text,'kana':bool(KANA.search(text)),'literal':literal}


def main():
    OUT.mkdir(exist_ok=True)
    local_original = HERE / ROM.name
    original_rom = (local_original if local_original.exists() else ROM).read_bytes()
    assert hashlib.sha256(original_rom).hexdigest() == '7a2118c605713898a8befa0dce2835998481bcbdd92850379620450de6209e4b'
    rom = (HERE/'korean_text_v2/Palthena_Korean_Text_v2.gba').read_bytes()
    game, game_end = custom_lz(rom, 0x2ae0, 108472)
    original, _ = custom_lz(original_rom, 0x2ae0, 108472)
    engine_start = struct.unpack_from('<I', rom, 0x128)[0]-0x08000000
    engine, engine_end = custom_lz(rom, engine_start, 0x824c)
    assert game == (HERE/'korean_text_v2/edited_payload.bin').read_bytes()
    assert engine == (HERE/'boot_vram.bin').read_bytes()
    files=[]
    for side, p in [('A',0x2000),('B',0xe4ac)]:
        count=game[p+11];p+=12
        for _ in range(count):
            assert game[p]==3 and game[p+8]==4
            num, ident, address, size, kind = struct.unpack_from('<BBHHB',game,p+1)
            files.append({'side':side,'number':num,'id':ident,'address':address,
                          'size':size,'type':kind,'data':p+9,'end':p+9+size})
            p+=9+size
    # Search original encoding, retaining original/patched bytes side-by-side.
    game_map={i:str(i) for i in range(10)}|{0x12:' ',0x0a:'?',0x0c:',',0x0d:'.',0x0e:'!',0x0f:'ー',0x10:'゛',0x11:'゜'}
    game_map.update({0x16+i:c for i,c in enumerate('アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワッャュョヲンァィゥェォ')})
    candidates=[]
    for f in files:
        if f['type'] != 0: continue
        for m in re.finditer(rb'[\x00-\x12\x16-\x4d]{3,}', original[f['data']:f['end']]):
            raw=m.group()
            if sum(0x16<=v<=0x4c for v in raw)<3:continue
            a=f['data']+m.start(); z=a+len(raw)
            candidates.append({'offset':hex(a),'file':f"{f['side']}/{f['number']}",
                'original_decode':''.join(game_map.get(v,f'<{v:02X}>') for v in raw),
                'changed':game[a:z]!=raw,'original_hex':raw.hex(),'patched_hex':game[a:z].hex()})
    with (OUT/'game_candidates.csv').open('w',encoding='utf-8-sig',newline='') as fp:
        w=csv.DictWriter(fp,fieldnames=list(candidates[0]));w.writeheader();w.writerows(candidates)
    messages=[]
    for ident in range(1,60):
        row=parse_wrapper(rom,engine,ident)
        a,z=int(row['offset'],16),int(row['end'],16)
        row['unchanged_from_original']=rom[a:z]==original_rom[a:z]
        messages.append(row)
    with (OUT/'wrapper_messages.csv').open('w',encoding='utf-8-sig',newline='') as fp:
        w=csv.DictWriter(fp,fieldnames=['id','table_offset','offset','end','kana','unchanged_from_original','text']);w.writeheader()
        w.writerows({k:v for k,v in row.items() if k!='literal'} for row in messages)
    kana_messages=[r for r in messages if r['kana']]
    unique={r['offset']:r for r in kana_messages}
    build=json.loads((HERE/'korean_text_v2/build.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(rom).hexdigest() == build['patched_sha256']
    # Check encoded replacement strings in the actual decompressed ROM as well
    # as the build manifest; importing the builder does not execute its main().
    from build_text_patch import MENU, STATUS, OVER, ENDING, DIALOGS, status_order, HUD_GU, HUD_GAN
    banks=[MENU,STATUS,OVER,ENDING]+DIALOGS
    maps=[]
    for n,bank in enumerate(banks):
        chars=list(dict.fromkeys(c for s in bank for c in s if '\uac00'<=c<='\ud7a3'))
        if n==1:chars=status_order(chars)  # see build_text_patch.py
        maps.append({c:(0x16 if n==3 else 0x30)+2*i for i,c in enumerate(chars)})
    maps[4+12]=maps[1]  # dialog 12 shares the STATUS bank layout (see build_text_patch.py)
    checks=[]
    for row in build['translations']:
        if row['bank']=='title':continue
        at=int(row['offset'],16);bank=row['bank']
        alphabet={str(i):i for i in range(10)}|{chr(65+i):0x16+i for i in range(26)}|{' ':0x12,'!':0x0e,'?':0x0a,'.':0x0d,',':0x0c,'-':0x0f,HUD_GU:0x10,HUD_GAN:0x11}|maps[bank]
        parts=row['text'].split(' / ')
        limit=0x6ab7 if bank>=4 else at+32
        if 4<=bank<17:limit=struct.unpack_from('<H',game,0x695e+(bank-3)*2)[0]-0x3b05
        matched=all(bytes(alphabet[c] for c in s) in game[at:limit] for s in parts)
        assert matched,(row,hex(limit))
        checks.append({'offset':row['offset'],'text':row['text'],'encoded_bytes_verified':matched})
    remaining_font=[]
    for tile in range(0x16,0x4d):
        p=0xbf0c+tile*16
        if game[p:p+16]==original[p:p+16]:remaining_font.append({'tile':hex(tile),'payload_offset':hex(p),'character':game_map.get(tile)})
    report={'rom_sha256':hashlib.sha256(rom).hexdigest(),'method':'Static file analysis only; no emulator or gameplay.',
        'game_payload':{'gba_offset':hex(0x2ae0),'gba_end':hex(game_end),'bytes':len(game),'fds_files':len(files),'candidate_runs':len(candidates)},
        'wrapper_engine':{'gba_offset':hex(engine_start),'gba_end':hex(engine_end),'bytes':len(engine)},
        'wrapper_table':{'offset':'0x27cc','indexed_entries':len(messages),'kana_entries':len(kana_messages),'unique_kana_pointers':len(unique)},
        'messages':messages,'remaining_original_game_font_tiles':remaining_font,'known_translations':build['translations'],
        'known_game_string_checks':checks,
        'limits':['A matching kana-range byte in code/map/audio is not proof of Japanese text.',
                  'Original game font slots are reused by runtime Korean banks; retained glyph data does not prove a live untranslated line.',
                  'Wrapper table includes common-library messages; not every indexed message is necessarily reachable in this game.']}
    (OUT/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    # Compact contact sheets are static reconstructions from ROM font and script bytes.
    for page in range((len(unique)+7)//8):
        rows=list(unique.values())[page*8:page*8+8]
        sheet=Image.new('RGB',(1024,4*378),'#222222');d=ImageDraw.Draw(sheet)
        for j,row in enumerate(rows):
            x=(j%2)*512;y=(j//2)*378
            d.text((x+8,y+6),f"ID {row['id']:02d} | ROM {row['offset']}",fill='white')
            im=Image.open(OUT/f"wrapper_{row['id']:02d}.png").resize((512,352),Image.Resampling.NEAREST)
            sheet.paste(im,(x,y+24))
        sheet.save(OUT/f'wrapper_contact_{page+1}.png')
    print(json.dumps(report['wrapper_table'],ensure_ascii=False))
    for row in unique.values():print(row['id'],row['offset'],row['text'].replace('\n',' / '))
    print('Retained original game kana glyphs:',len(remaining_font))


if __name__=='__main__':main()
