"""Encode the ImageGen wordmark into the original ROM's 2bpp title assets.

The image operations below are the deterministic crop, pixel-grid resampling,
and palette encoding required by the ROM format; artwork is logo_source.png.
"""
from pathlib import Path
import struct,json,hashlib,shutil
import numpy as np
from PIL import Image
from analyze_rom import ROM,custom_lz
from build_test_patch import compress,ips,apply_ips,glyph
from build_logo_patch import text_mask,encode_tile

from paths import WORK as HERE, FONTS, ASSETS, FINAL, STEM, MGBA
OUT=HERE/'korean_logo_v2'
START,END,SIZE=0x2ae0,0x17380,108472
CHR=0xb233;TILE_COUNT=205

def make_art():
    # Crop black margins from the generated artwork, retaining the entire red shadow.
    im=Image.open(ASSETS/'title_logo_ko.png').convert('RGB');a=np.asarray(im)
    mask=(a[:,:,0]>65)&(a[:,:,0]>a[:,:,1]*1.3)&(a[:,:,0]>a[:,:,2]*1.3)
    yy,xx=np.where(mask);box=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
    # Stay within the original all-orange palette quadrants; the top row is shared
    # with the pink subtitle and the left edge with the blue clouds.
    small=im.crop(box).resize((160,64),Image.Resampling.LANCZOS)
    rgb=np.asarray(small).astype(np.int32)
    palette=np.array([[0,0,0],[255,133,82],[189,33,0]],dtype=np.int32)
    encoded=np.argmin(np.sum((rgb[:,:,None,:]-palette[None,None,:,:])**2,axis=3),axis=2).astype(np.uint8)
    # No antialiased colors remain: only the original title's two nonzero pixel indices.
    art=np.zeros((240,256),dtype=np.uint8);art[80:144,48:208]=encoded
    sub=text_mask('광신화',11,1,1)
    sub=np.asarray(Image.fromarray(sub).resize((sub.shape[1],16),Image.Resampling.NEAREST))
    x=88+(48-sub.shape[1])//2;art[56:72,x:x+sub.shape[1]]=sub
    Image.fromarray(palette[encoded].astype(np.uint8)).resize((640,256),Image.Resampling.NEAREST).save(OUT/'encoded_logo_preview.png')
    return art,{'source_crop':box,'encoded_dimensions':[160,64],'source_sha256':hashlib.sha256((ASSETS/'title_logo_ko.png').read_bytes()).hexdigest()}

def main():
    OUT.mkdir(exist_ok=True)
    original=ROM.read_bytes();payload,_=custom_lz(original,START,SIZE);edited=bytearray(payload)
    nt=bytearray([0x12]*960+[0]*64);locations={}
    for i in range(20):
        dst,src,n=struct.unpack_from('<HHB',payload,0x6d24+5*i);off=src-0x3b05
        if 0x2800<=dst<0x2c00:
            for j in range(n):
                ix=dst-0x2800+j;nt[ix]=payload[off+j];locations[ix]=off+j
    before=bytes(nt)
    region={(x,y) for y in range(9,19) for x in range(5,27)}|{(x,y) for y in range(7,9) for x in range(11,17)}|{(x,8) for x in range(7,10)}
    region.remove((26,9))
    art,art_info=make_art()
    protected={nt[y*32+x] for y in range(30) for x in range(32) if (x,y) not in region}
    protected.update(payload[0x6d88:0x6d9a]);protected.add(0x12)
    protected.update(range(10))  # Keeping these also preserves the rightmost framebuffer column.
    free=[i for i in range(TILE_COUNT) if i not in protected]
    patterns={bytes(16):0x12};used=[]
    for x,y in sorted(region,key=lambda p:(p[1],p[0])):
        tile=encode_tile(art[y*8:y*8+8,x*8:x*8+8]);ix=y*32+x
        attribute=before[960+(y//4)*8+x//4]
        pal=(attribute>>((y%4//2)*4+(x%4//2)*2))&3
        if tile==bytes(16) and (pal==2 or before[ix] in {0xa6,0xa7,0xa8,0xa9,0xab,0x8f,0x9b,0x9c}):continue
        if tile not in patterns:
            assert free,('Not enough title tiles',len(used))
            slot=free.pop(0);patterns[tile]=slot;used.append(slot)
            edited[CHR+slot*16:CHR+(slot+1)*16]=tile
        slot=patterns[tile]
        if ix not in locations:assert slot==before[ix],(x,y,slot,before[ix])
        else:edited[locations[ix]]=slot
        nt[ix]=slot
    for i,ch in enumerate('한글성공'):edited[0xae43+i*16:0xae53+i*16]=glyph(ch)+bytes(8)
    packed=compress(edited);roundtrip,consumed=custom_lz(packed,0,SIZE)
    assert roundtrip==edited and consumed==len(packed)
    assert len(packed)<=END-START,(len(packed),END-START)
    modified=bytearray(original);modified[START:START+len(packed)]=packed
    patch=ips(original,modified);assert apply_ips(original,patch)==modified
    (OUT/'Palthena_Korean_Logo_v2.gba').write_bytes(modified)
    from rom_delivery import copy_to_desktop
    copy_to_desktop(OUT/'Palthena_Korean_Logo_v2.gba')
    (OUT/'Palthena_Korean_Logo_v2.ips').write_bytes(patch)
    (OUT/'edited_payload.bin').write_bytes(edited);(OUT/'title_nt.bin').write_bytes(nt)
    info={'title':'광신화 파르테나의 거울','artwork':'ImageGen built-in, original Japanese title as style reference','subtitle_font':'Galmuri11','compression_bytes':len(packed),'available_bytes':END-START,'new_tile_count':len(used),'remaining_tile_slots':len(free),'tile_slots':used,'original_sha256':hashlib.sha256(original).hexdigest(),'patched_sha256':hashlib.sha256(modified).hexdigest(),'roundtrip_verified':True,'ips_verified':True,**art_info}
    (OUT/'build.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    shutil.copyfile(FONTS/'Galmuri-OFL.md',OUT/'Galmuri-OFL.md')
    print(json.dumps({k:v for k,v in info.items() if k!='tile_slots'},ensure_ascii=True,indent=2))

if __name__=='__main__':main()
