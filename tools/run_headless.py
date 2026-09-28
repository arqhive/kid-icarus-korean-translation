"""Run a ROM with the unmodified mGBA libretro core; capture framebuffer and RAM.

No UI overlay, video filter, cheat, or runtime memory writes are used.
"""
from pathlib import Path
import ctypes as C
import argparse, json
import numpy as np
from PIL import Image

from paths import WORK as HERE, FONTS, ASSETS, FINAL, STEM, MGBA
class Game(C.Structure):
    _fields_=[('path',C.c_char_p),('data',C.c_void_p),('size',C.c_size_t),('meta',C.c_char_p)]
class Variable(C.Structure):
    _fields_=[('key',C.c_char_p),('value',C.c_char_p)]
class MemDesc(C.Structure):
    _fields_=[('flags',C.c_uint64),('ptr',C.c_void_p),('offset',C.c_size_t),('start',C.c_size_t),('select',C.c_size_t),('disconnect',C.c_size_t),('len',C.c_size_t),('addrspace',C.c_char_p)]
class MemMap(C.Structure):
    _fields_=[('descriptors',C.POINTER(MemDesc)),('num_descriptors',C.c_uint)]
ENV=C.CFUNCTYPE(C.c_bool,C.c_uint,C.c_void_p)
VIDEO=C.CFUNCTYPE(None,C.c_void_p,C.c_uint,C.c_uint,C.c_size_t)
AUDIO=C.CFUNCTYPE(None,C.c_int16,C.c_int16)
BATCH=C.CFUNCTYPE(C.c_size_t,C.c_void_p,C.c_size_t)
POLL=C.CFUNCTYPE(None)
INPUT=C.CFUNCTYPE(C.c_int16,C.c_uint,C.c_uint,C.c_uint,C.c_uint)

class Emulator:
    def __init__(self,rom):
        self.core=C.CDLL(str(MGBA))
        self.fmt=0;self.keys=set();self.frame=None;self.maps=[];self.variables={}
        self.system_dir=str(MGBA.parent).encode('utf-8')
        self.callbacks=[ENV(self.environment),VIDEO(self.video),AUDIO(lambda l,r:None),BATCH(lambda p,n:n),POLL(lambda:None),INPUT(self.input)]
        names=['environment','video_refresh','audio_sample','audio_sample_batch','input_poll','input_state']
        for name,cb in zip(names,self.callbacks):
            fn=getattr(self.core,'retro_set_'+name);fn.argtypes=[type(cb)];fn(cb)
        self.core.retro_init()
        self.core.retro_load_game.argtypes=[C.POINTER(Game)];self.core.retro_load_game.restype=C.c_bool
        self.rom_buffer=C.create_string_buffer(Path(rom).read_bytes())
        game=Game(str(Path(rom).resolve()).encode('utf-8'),C.cast(self.rom_buffer,C.c_void_p),len(self.rom_buffer)-1,None)
        if not self.core.retro_load_game(C.byref(game)):raise RuntimeError('ROM load failed')
        self.core.retro_serialize_size.restype=C.c_size_t
        self.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];self.core.retro_serialize.restype=C.c_bool
    def environment(self,cmd,data):
        if cmd==10:
            self.fmt=C.cast(data,C.POINTER(C.c_uint))[0];return self.fmt in (0,1,2)
        if cmd in (9,31):
            C.cast(data,C.POINTER(C.c_char_p))[0]=self.system_dir;return True
        if cmd==3:
            C.cast(data,C.POINTER(C.c_bool))[0]=True;return True
        if cmd==16:
            p=C.cast(data,C.POINTER(Variable));n=0
            while p[n].key:
                self.variables[p[n].key]=p[n].value.split(b'; ',1)[-1].split(b'|')[0];n+=1
            return True
        if cmd==15:
            p=C.cast(data,C.POINTER(Variable));key=p[0].key
            if key not in self.variables:return False
            p[0].value=self.variables[key];return True
        if cmd==17:
            C.cast(data,C.POINTER(C.c_bool))[0]=False;return True
        if cmd==52:
            C.cast(data,C.POINTER(C.c_uint))[0]=0;return True
        if cmd==(36|0x10000):
            m=C.cast(data,C.POINTER(MemMap))[0]
            self.maps=[{k:getattr(d,k) for k in ['ptr','offset','start','len']} for d in m.descriptors[:m.num_descriptors]]
            return True
        return False
    def video(self,data,w,h,pitch):
        if not data:return
        raw=C.string_at(data,pitch*h)
        if self.fmt==1:
            a=np.frombuffer(raw,dtype=np.uint32).reshape(h,pitch//4)[:,:w]
            rgb=np.stack(((a>>16)&255,(a>>8)&255,a&255),axis=-1).astype('uint8')
        else:
            a=np.frombuffer(raw,dtype=np.uint16).reshape(h,pitch//2)[:,:w].astype(np.uint32)
            if self.fmt==2:r,g,bl=(a>>11)&31,(a>>5)&63,a&31;g=g*255//63
            else:r,g,bl=(a>>10)&31,(a>>5)&31,a&31;g=g*255//31
            rgb=np.stack((r*255//31,g,bl*255//31),axis=-1).astype('uint8')
        self.frame=Image.fromarray(rgb)
    def input(self,port,device,index,key):return int(port==0 and key in self.keys)
    def run(self,frames,keys=()):
        self.keys=set(keys)
        for _ in range(frames):self.core.retro_run()
    def capture(self,folder,number,ram=True):
        folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
        if self.frame is not None:
            self.frame.save(folder/f'frame_{number:05d}.png')
            self.frame.resize((720,480),Image.Resampling.NEAREST).save(folder/f'frame_{number:05d}_3x.png')
        if ram:
            for m in self.maps:
                if m['ptr'] and m['start'] in [0x02000000,0x03000000,0x04000000,0x05000000,0x06000000]:
                    (folder/f'mem_{number:05d}_{m["start"]:08x}.bin').write_bytes(C.string_at(m['ptr']+m['offset'],m['len']))
        print('Captured',number,flush=True)
    def close(self):self.core.retro_unload_game();self.core.retro_deinit()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--out',required=True);ap.add_argument('--frames',default='60,180,360,600');ap.add_argument('--press',default='')
    args=ap.parse_args();e=Emulator(args.rom)
    schedule=[]
    for entry in args.press.split(','):
        if entry:
            start,end,key=map(int,entry.split(':'));schedule.append((start,end,key))
    targets=set(map(int,args.frames.split(',')))
    for f in range(1,max(targets)+1):
        e.run(1,[key for start,end,key in schedule if start<=f<end])
        if f in targets:e.capture(args.out,f)
    Path(args.out,'core_options.json').write_text(json.dumps({k.decode():v.decode() for k,v in e.variables.items()},indent=2))
    e.close()
if __name__=='__main__':main()
