"""Reproducible Korean text patch. Original input is never modified."""
from pathlib import Path
import struct,json,hashlib,shutil
from analyze_rom import ROM,custom_lz
from build_test_patch import compress,glyph

from paths import WORK as HERE, FONTS, ASSETS, FINAL, STEM, MGBA
OUT=HERE/'korean_text_v2'
# Famicom Mini alternates between CHR rows 1/2 and 5/6. These pairs
# must agree to avoid temporal jitter. Six stable output rows per tile.
STABLE_ROWS=(0,1,1,2,3,4,4,5,6,7,7,7,7,7,7,7)

class Asm:
    def __init__(self,base):self.base=base;self.b=bytearray();self.labels={};self.fix=[]
    @property
    def pc(self):return self.base+len(self.b)
    def label(self,n):self.labels[n]=self.pc
    def emit(self,*v):self.b.extend(v)
    def word(self,op,a):self.emit(op,a&255,a>>8)
    def ref(self,op,label):self.emit(op);self.fix.append((len(self.b),label,False));self.emit(0,0)
    def branch(self,op,label):self.emit(op);self.fix.append((len(self.b),label,True));self.emit(0)
    def finish(self):
        for p,n,rel in self.fix:
            a=self.labels[n]
            if rel:
                d=a-(self.base+p+1);assert -128<=d<128;self.b[p]=d&255
            else:self.b[p:p+2]=struct.pack('<H',a)
        return bytes(self.b)

from game_ko import MENU, STATUS, OVER, ENDING, DIALOGS, NAME_AFTER_LINE1


from ips import ips_extended, apply_patch


def main():
    BASE=(HERE/'korean_logo_v2/edited_payload.bin').read_bytes()
    ORIG=(HERE/'game_payload.bin').read_bytes()
    OUT.mkdir(exist_ok=True);b=bytearray(BASE);changes=[]
    # Retain one existing phase of the approved logo, making both phases equal.
    logo_info=json.loads((HERE/'korean_logo_v2/build.json').read_text(encoding='utf-8'))
    for tile in logo_info['tile_slots']:
        for plane in (0,8):
            off=0xb233+tile*16+plane
            b[off+2]=b[off+1];b[off+6]=b[off+5]
    # Latin letters occupy permanent kana slots. Korean slots are banked.
    banks=[MENU,STATUS,OVER,ENDING]+DIALOGS
    chars=[list(dict.fromkeys(c for s in bank for c in s if '\uac00'<=c<='\ud7a3')) for bank in banks]
    starts=[0x30]*len(banks);starts[3]=0x16
    for i,c in enumerate(chars):assert len(c)*2<=0x4e-starts[i],(i,len(c),''.join(c))
    pool=list(dict.fromkeys(c for cs in chars for c in cs));print('Glyphs',len(pool),'Bank sizes',list(map(len,chars)),flush=True)
    mappings=[{c:st+i*2 for i,c in enumerate(cs)} for cs,st in zip(chars,starts)]
    def enc(s,bank):
        m={str(i):i for i in range(10)}|{chr(65+i):0x16+i for i in range(26)}|{' ':0x12,'!':0x0e,'?':0x0a,'.':0x0d,',':0x0c,'-':0x0f}|mappings[bank]
        return bytes(m[c] for c in s)
    def put(off,n,s,bank,align='left'):
        raw=enc(s,bank);assert len(raw)<=n,(hex(off),s,n)
        raw=raw.center(n,b'\x12') if align=='center' else raw.ljust(n,b'\x12')
        b[off:off+n]=raw;changes.append({'offset':hex(off),'text':s,'bank':bank})
    latin=['0e111f1111','1e111e111e','0f1010100f','1e1111111e','1f101e101f','1f101e1010','0f1013110f','11111f1111','0e0404040e','070202120c','1112141211','101010101f','111b151111','1119151311','0e1111110e','1e111e1010','0e1111150f','1e111e1211','0f100e011e','1f04040404','111111110e','1111110a04','1111151b11','110a040a11','110a040404','1f0204081f']
    for i in range(26):
        rows=bytes.fromhex(latin[i]);font=bytes(rows[j]<<2 for j in [0,1,1,2,3,4,4])+b'\x00'
        b[0xbf0c+(0x16+i)*16:0xbf0c+(0x17+i)*16]=font+bytes(8)
    # Restore the real copyright date after the earlier font proof.
    b[0xae43:0xae83]=ORIG[0xae43:0xae83]
    put(0x722d,10,MENU[0],0);put(0x724b,8,MENU[1],0);put(0x7257,9,MENU[2],0);b[0x723a]=0x12
    put(0x783e,7,MENU[1],0);put(0x7849,8,MENU[3],0)
    # Delete-mode heading and exit label.
    put(0x78b0,12,MENU[2],0,'center');put(0x78c0,8,MENU[4],0)
    # Keyboard: retain A-Z in the first kana slots and the native digits.
    for off in range(0x776f,0x77ba):
        v=b[off]
        if v>=0x30 or v in [0x10,0x11]:b[off]=0x12
    keys=bytearray()
    for row in range(5):
        for group in range(3):
            vals=b[0x776f+row*15+group*5:0x7774+row*15+group*5]
            dest=0x245+row*0x40+group*8
            if all(v==0x12 for v in vals):continue
            if vals==bytes(range(vals[0],vals[0]+5)):keys.extend(bytes([7])+struct.pack('<H',dest)+bytes([5,vals[0]]))
            else:keys.extend(bytes([4])+struct.pack('<H',dest)+bytes([5])+vals)
    assert len(keys)<=0x7839-0x77e3
    b[0x77e3:0x7839]=keys.ljust(0x7839-0x77e3,b'\x80')
    for off,n,s in [(0x4ac4,3,'수'),(0x4acb,5,'체력'),(0x4ad4,8,'공격력'),(0x4ae6,8,'도구'),(0x4af2,9,'신기'),(0x4b3b,8,'기록'),(0x4b44,4,'총'),(0x4b48,3,'점수'),(0x4b4b,5,'구간')]:put(off,n,s,1)
    for off,n,s in [(0x29b4,7,OVER[0]),(0x29bb,10,OVER[1]),(0x29c5,7,OVER[2]),(0x29d0,8,OVER[3])]:put(off,n,s,2)
    for off,n,s in [(0x66ec,7,'총점'),(0x66f6,3,'점수'),(0x6704,8,'구간 - '),(0x670f,3,'보스')]:put(off,n,s,1)
    # Compact dialogue scripts keep their two-line control format.
    ptrs=struct.unpack_from('<14H',ORIG,0x695e)
    for i,lines in enumerate(DIALOGS):
        start=ptrs[i]-0x3b05;end=ptrs[i+1]-0x3b05 if i<13 else 0x6ab7
        raw=bytearray()
        if i==13:
            # $A59D..$A5A4 is overwritten with the registered name at runtime.
            raw.extend(ORIG[start:start+12]);raw[-1]=0x12
        for j,s in enumerate(lines):
            dest=(0x20c8 if i<12 else (0x29cc if i==12 else 0x2928))+j*0x40
            raw.extend(b'\xfe'+struct.pack('<H',dest)+enc(s,4+i))
            # Temple greetings insert the registered name ($0120, 8 tiles) after line 1.
            if i in NAME_AFTER_LINE1 and j==0:raw.extend(b'\xfd\x08\x20\x01')
        raw.append(0xff);assert len(raw)<=end-start,(i,len(raw),end-start)
        b[start:end]=raw.ljust(end-start,b'\xff');changes.append({'offset':hex(start),'text':' / '.join(lines),'bank':4+i})
    # Ending has three fixed rows of 21 tiles.
    for i,s in enumerate(ENDING):put(0x8c2e+i*21,21,s,3,'center')
    # BIOS boot artwork is unused by this wrapper: reuse F700-FE33, retain BIOS code.
    a=Asm(0xf700)
    a.label('load')
    a.emit(0x08,0x48,0x8a,0x48,0x98,0x48) # P,A,X,Y
    for z in range(6):a.emit(0xa5,z,0x48)
    # Recover input A from stack (six ZP + Y + X pushes).
    a.emit(0xba);a.word(0xbd,0x0109);a.word(0x8d,0xdfe8);a.emit(0x0a,0xaa)
    a.ref(0xbd,'bankptr');a.emit(0x85,0x00);a.ref(0xbd,'bankptr_hi');a.emit(0x85,0x01)
    a.emit(0xa5,0xff,0x29,0x7b);a.word(0x8d,0x2000);a.emit(0xa9,0);a.word(0x8d,0x2001)
    a.emit(0xa0,0,0xb1,0,0x85,4,0x0a,0xc8,0x18,0x71,0);a.word(0x8d,0xdfed)
    a.emit(0xb1,0,0x85,5);a.word(0x8d,0xdfec)
    a.word(0xad,0x2002);a.emit(0xa5,5,0x4a,0x4a,0x4a,0x4a,0x09,0x10);a.word(0x8d,0x2006)
    a.emit(0xa5,5,0x0a,0x0a,0x0a,0x0a);a.word(0x8d,0x2006)
    a.emit(0xa9,2,0x85,5)
    a.label('next');a.emit(0xa4,5,0xb1,0,0xa2,0,0x86,3,0x0a,0x26,3,0x0a,0x26,3,0x0a,0x26,3,0x18)
    # Font base patched once label assigned.
    a.emit(0x69,0);fontlo=len(a.b)-1;a.emit(0x85,2,0xa5,3,0x69,0);fonthi=len(a.b)-1;a.emit(0x85,3,0xa2,0)
    a.label('rows');a.ref(0xbc,'stretch');a.emit(0xb1,2);a.word(0x8d,0x2007);a.emit(0xe8,0xe0,8);a.branch(0xd0,'rows')
    a.emit(0xa9,0,0xa2,8);a.label('zero');a.word(0x8d,0x2007);a.emit(0xca);a.branch(0xd0,'zero')
    a.emit(0xa2,8);a.label('rows2');a.ref(0xbc,'stretch');a.emit(0xb1,2);a.word(0x8d,0x2007);a.emit(0xe8,0xe0,16);a.branch(0xd0,'rows2')
    a.emit(0xa9,0,0xa2,8);a.label('zero2');a.word(0x8d,0x2007);a.emit(0xca);a.branch(0xd0,'zero2')
    a.emit(0xe6,5,0xc6,4);a.branch(0xd0,'next')
    a.emit(0xa5,0xff);a.word(0x8d,0x2000);a.emit(0xa5,0xfe);a.word(0x8d,0x2001)
    for z in reversed(range(6)):a.emit(0x68,0x85,z)
    a.emit(0x68,0xa8,0x68,0xaa,0x68,0x28,0x60)
    a.label('menu');a.emit(0xa9,0);a.ref(0x20,'load');a.emit(0xa0,0);a.word(0x4c,0x8697)
    a.label('status');a.word(0xad,0xdfe8);a.word(0x8d,0xdfe9);a.emit(0xa9,1);a.ref(0x20,'load');a.word(0x20,0x8695);a.emit(0x60)
    a.label('restore');a.word(0xad,0xdfe9);a.ref(0x20,'load');a.word(0x4c,0x8dab)
    a.label('over');a.emit(0x48,0xa9,2);a.ref(0x20,'load');a.emit(0x68);a.word(0x20,0x63c7);a.emit(0x60)
    a.label('extra');a.word(0x20,0x63c7);a.ref(0x4c,'direct')
    a.label('ending');a.emit(0xa9,3);a.ref(0x20,'load');a.emit(0xa2,0,0xa5,0x4b);a.word(0x4c,0xa6bb)
    a.label('dialog');a.word(0xad,0x04e2);a.emit(0x18,0x69,3);a.ref(0x20,'load');a.word(0xae,0x04e2);a.word(0x4c,0xa405)
    # Literal text cursor, shared by menu opcode 4 and spaced opcode 9.
    a.label('addr');a.word(0x8d,0x2006);a.word(0x8d,0xdfef);a.word(0x8e,0x2006);a.word(0x8e,0xdfee);a.emit(0x60)
    a.label('put');a.emit(0x08,0x48);a.word(0x8d,0x2007)
    a.emit(0xc9,0x12);a.branch(0xf0,'bottom')
    a.word(0xcd,0xdfec);a.branch(0x90,'advance');a.word(0xcd,0xdfed);a.branch(0xb0,'advance')
    a.emit(0x29,1);a.branch(0xd0,'advance')
    a.label('bottom')
    a.emit(0x18);a.word(0xad,0xdfee);a.emit(0x69,32,0x48);a.word(0xad,0xdfef);a.emit(0x69,0);a.word(0x8d,0x2006);a.emit(0x68);a.word(0x8d,0x2006)
    a.emit(0x68,0x48,0xc9,0x12);a.branch(0xf0,'bottom_blank');a.emit(0x18,0x69,1)
    a.label('bottom_blank');a.word(0x8d,0x2007)
    a.label('advance');a.word(0xee,0xdfee);a.branch(0xd0,'no_carry');a.word(0xee,0xdfef)
    a.label('no_carry');a.word(0xad,0xdfef);a.word(0x8d,0x2006);a.word(0xad,0xdfee);a.word(0x8d,0x2006);a.emit(0x68,0x28,0x60)
    a.label('direct');a.word(0xad,0x2002);a.emit(0xa5,0x42);a.word(0x8d,0x2006);a.word(0x8d,0xdfef);a.emit(0xa5,0x41);a.word(0x8d,0x2006);a.word(0x8d,0xdfee);a.emit(0xa0,0)
    a.label('direct_loop');a.emit(0xb1,0x43);a.ref(0x20,'put');a.emit(0xc8,0xc4,0x45);a.branch(0xd0,'direct_loop');a.emit(0x60)
    a.label('hi');a.word(0x8d,0x2006);a.word(0x8d,0xdfef);a.emit(0x60)
    a.label('lo');a.word(0x8d,0x2006);a.word(0x8d,0xdfee);a.emit(0x60)
    a.label('xy');a.word(0x8e,0x2006);a.word(0x8e,0xdfef);a.word(0x8c,0x2006);a.word(0x8c,0xdfee);a.emit(0x60)
    a.label('score');a.emit(0xa9,1);a.ref(0x20,'load');a.emit(0xa9,5);a.word(0x8d,0x0766);a.word(0x4c,0xa018)
    a.label('stretch');a.emit(*STABLE_ROWS)
    a.label('bankptr');a.labels['bankptr_hi']=a.pc+1
    for i in range(len(banks)):a.fix.append((len(a.b),f'bank{i}',False));a.emit(0,0)
    for i,cs in enumerate(chars):a.label(f'bank{i}');a.emit(len(cs),starts[i],*(pool.index(c) for c in cs))
    a.label('font');a.b[fontlo]=a.pc&255;a.b[fonthi]=a.pc>>8
    for c in pool:a.b.extend(glyph(c))
    # Title prompt uses its own CHR set and a contiguous two-row PPU transfer.
    title_nt=(HERE/'korean_logo_v2/title_nt.bin').read_bytes()
    protected=set(title_nt[:960])|set(BASE[0x6d88:0x6d9a])|set(range(10))
    free=[i for i in range(205) if i not in protected]
    top=[];bottom=[]
    for ch in '시작 버튼':
        if ch==' ':top.append(0x12);bottom.append(0x12);continue
        source=glyph(ch);rows=bytes(source[j] for j in STABLE_ROWS)
        ids=[]
        for half in [rows[:8],rows[8:]]:
            tile=free.pop(0);ids.append(tile);b[0xb233+tile*16:0xb243+tile*16]=half+bytes(8)
        top.append(ids[0]);bottom.append(ids[1])
    prompt=bytes(top).center(18,b'\x12')+bytes([0x12])*14+bytes(bottom).center(18,b'\x12')
    struct.pack_into('<HB',b,0x6d26,a.pc,len(prompt));a.b.extend(prompt)
    changes.append({'offset':'0x6d24','text':'시작 버튼','bank':'title'})
    blob=a.finish();assert a.pc<=0xfe34,hex(a.pc)
    b[0x1700:0x1700+len(blob)]=blob
    def hook(off,label,n=3):b[off:off+n]=bytes([0x20])+struct.pack('<H',a.labels[label])+bytes([0xea])*(n-3)
    # Only menu call sites receive the menu bank; status uses its own.
    for off in [0x714d,0x7162,0x716e,0x717a,0x73b6,0x73d7,0x73e7,0x73f7,0x7407]:hook(off,'menu')
    hook(0x4734,'status');hook(0x45e8,'restore');hook(0x292b,'over');hook(0x68fd,'dialog');hook(0x292e,'direct')
    hook(0x2939,'extra');b[0x2939]=0x4c
    hook(0x4d0d,'addr',6)  # $8812, writes high/low PPU address
    for off in [0x4c44,0x4c59,0x4cd3,0x4cd7,0x67dc,0x6826,0x6560]:hook(off,'put')
    for off in [0x67d0,0x6550]:hook(off,'hi')
    for off in [0x67d6,0x6556]:hook(off,'lo')
    hook(0x681c,'xy',6)
    hook(0x650e,'score',5);b[0x650e]=0x4c
    # Dialog hook replaces LDX $04e2 and tail-jumps to original continuation.
    b[0x68fd]=0x4c
    ending_off=0x8a4b+0xa6b7-0xa5f8;hook(ending_off,'ending',4);b[ending_off]=0x4c
    hook(0x8a4b+0xa6cb-0xa5f8,'direct')
    original=ROM.read_bytes();packed=compress(b);unpacked,consumed=custom_lz(packed,0,len(b));assert unpacked==b and consumed==len(packed)
    rom=bytearray(original)
    relocation=None
    if len(packed)>0x17380-0x2ae0:
        assert 0x2ae0+len(packed)<=0x1bd49
        engine=original[0x17380:0x1bd49]
        relocation=0x400000;rom.extend(bytes([255])*(0x800000-len(rom)));rom[relocation:relocation+len(engine)]=engine
        struct.pack_into('<I',rom,0x128,0x08000000+relocation)
    rom[0x2ae0:0x2ae0+len(packed)]=packed
    patch=ips_extended(original,rom);assert apply_patch(original,patch)==rom
    (OUT/'Palthena_Korean_Text_v2.gba').write_bytes(rom);(OUT/'Palthena_Korean_Text_v2.ips').write_bytes(patch);(OUT/'edited_payload.bin').write_bytes(b)
    from rom_delivery import copy_to_desktop
    copy_to_desktop(OUT/'Palthena_Korean_Text_v2.gba')
    info={'original_sha256':hashlib.sha256(original).hexdigest(),'patched_sha256':hashlib.sha256(rom).hexdigest(),'compressed_size':len(packed),'engine_relocation':relocation,'bios_font_end':hex(a.pc),'glyphs':len(pool),'bank_sizes':list(map(len,chars)),'hooks':a.labels,'translations':changes,'ips_verified':True,'roundtrip_verified':True}
    (OUT/'build.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8');shutil.copyfile(FONTS/'Galmuri-OFL.md',OUT/'Galmuri-OFL.md')
    print('Built',len(rom),len(packed),'BIOS end',hex(a.pc),flush=True)

if __name__=='__main__':main()
