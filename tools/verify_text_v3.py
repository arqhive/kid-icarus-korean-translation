"""Static verification of every wrapper script plus a focused UI regression."""
from pathlib import Path
import hashlib,json,struct
import numpy as np
from PIL import Image,ImageDraw
from analyze_rom import ROM,custom_lz
from ips import apply_patch
from run_headless import Emulator

from paths import WORK as HERE, FONTS, ASSETS, FINAL, STEM, MGBA
OUT=FINAL


def main():
    meta=json.loads((OUT/'build.json').read_text(encoding='utf-8'))
    rom=(OUT/(STEM+'.gba')).read_bytes()
    assert hashlib.sha256(rom).hexdigest()==meta['patched_sha256']
    assert apply_patch(ROM.read_bytes(),(OUT/(STEM+'.ips')).read_bytes())==rom
    game,_=custom_lz(rom,0x2ae0,108472)
    assert game==(HERE/'korean_text_v2/edited_payload.bin').read_bytes()
    engine,_=custom_lz(rom,int(meta['engine_rom_offset'],16),0x824c)
    assert engine==(OUT/'engine.bin').read_bytes()
    ptr,dst,mode=struct.unpack_from('<III',engine,0x4e0)
    assert dst==0x06007700 and mode==0x84000240
    font=rom[ptr-0x8000000:ptr-0x8000000+0x900]
    assert font==(OUT/'wrapper_font.bin').read_bytes()
    inverse={v:k for k,v in meta['codes'].items()}
    static=OUT/'static';static.mkdir(exist_ok=True)
    counts={}
    for record in meta['messages']:
        ident=record['id'];base_x,base_y,w,h,ptr=struct.unpack_from('<BBBBI',rom,0x27cc+ident*8)
        p=ptr-0x08000000;assert p==int(record['script_offset'],16)
        ax,x=base_x,base_x;ay,y=base_y,base_y;cells={};used=[]
        while rom[p]!=255:
            v=rom[p];p+=1
            if v in (5,6):
                dx,dy=struct.unpack_from('<bb',rom,p);p+=2
                ax,ay=(base_x+dx,base_y+dy) if v==5 else (ax+dx,ay+dy)
                x,y=ax,ay
            elif v in (4,7,8,9,10):x+=1
            elif v<=3:pass
            else:
                if record['translated']:
                    assert v in inverse,(ident,hex(v))
                    ch=inverse[v];assert not '\u3040'<=ch<='\u30ff'
                    used.append(ch)
                    assert 0<=x<30 and 0<=y<20,(ident,x,y)
                cells[x,y]=v;x+=1
        counts[str(ident)]=len(used)
        image=Image.new('RGB',(240,160),'black')
        for (x,y),v in cells.items():
            tile=struct.unpack_from('<H',rom,0x17d0+v*2)[0]
            off=((tile&1023)-0x1b8)*32
            assert 0<=off<=len(font)-32
            raw=np.frombuffer(font[off:off+32],dtype=np.uint8)
            pix=np.stack((raw&15,raw>>4),axis=1).reshape(8,8)
            pal=np.array(struct.unpack_from('<16H',engine,0x9b8+(tile>>12)*32))
            pic=Image.fromarray(np.uint8(pal[pix]>0)*255).convert('RGB')
            image.paste(pic,(x*8,y*8))
        if record['translated']:
            image.resize((720,480),Image.Resampling.NEAREST).save(static/f'message_{ident:02d}.png')
    qa=OUT/'qa';qa.mkdir(exist_ok=True)
    e=Emulator(OUT/(STEM+'.gba'))
    e.run(600);title=np.asarray(e.frame).copy();e.capture(qa,600,ram=False)
    e.run(4,[10,11]);e.run(90);e.capture(qa,694)
    font_snapshot=(qa/'mem_00694_06000000.bin').read_bytes()[0x7700:0x8000]
    # The stock UI updates its cursor tiles 1B9/1BA after DMA. Text and frame
    # tiles begin at 1BC and must still exactly match the new ROM resource.
    assert font_snapshot[0x80:]==font[0x80:],'Text font differs from the ROM resource'
    region=np.asarray(e.frame)[24:136,88:184].copy();changes=[]
    for _ in range(120):
        e.run(1);a=np.asarray(e.frame)[24:136,88:184]
        changes.append(int(np.count_nonzero(np.any(a!=region,axis=2))))
    assert max(changes)==0,changes
    e.run(4,[8]);e.run(120);e.capture(qa,938,ram=False) # continue
    e.run(4,[10,11]);e.run(30)
    e.run(4,[5]);e.run(10);e.run(4,[8]);e.run(600);e.capture(qa,1590,ram=False) # reset
    e.close()
    # Same input and frame number before opening the wrapper must remain identical.
    e=Emulator(HERE/'korean_text_v2/Palthena_Korean_Text_v2.gba')
    e.run(600);assert np.array_equal(title,np.asarray(e.frame));e.close()
    report={'rom_sha256':meta['patched_sha256'],'translated_scripts_verified':sum(r['translated'] for r in meta['messages']),
            'live_translated_script_kana':0,'script_glyph_bounds_checked':True,'game_payload_identical_to_v2':True,
            'ips_roundtrip':True,'engine_roundtrip':True,'text_font_dma_matches_rom':True,'title_pixels_match_v2':True,
            'menu_text_stability_frames':120,'menu_text_max_changed_pixels':max(changes),
            'runtime_scope':'Fresh boot, L+R menu, continue, reset. No full game playthrough. Other messages statically rendered.',
            'decoded_characters_per_message':counts}
    (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Verified 47 translated wrapper scripts; no kana references; 120 stable menu frames.')


if __name__=='__main__':main()
