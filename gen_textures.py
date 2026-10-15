import numpy as np, random, os, json
from PIL import Image
TEX="/home/claude/warden_dimension/src/main/resources/assets/warden_dimension/textures/block"
os.makedirs(TEX,exist_ok=True)
def vn(seed, s=4):
    """ruido de valor suave y tileable 16x16"""
    r=np.random.RandomState(seed); g=r.rand(s,s)
    ys,xs=np.mgrid[0:16,0:16]/16.0*s
    x0=np.floor(xs).astype(int)%s; y0=np.floor(ys).astype(int)%s; x1=(x0+1)%s; y1=(y0+1)%s
    fx=xs-np.floor(xs); fy=ys-np.floor(ys); fx=fx*fx*(3-2*fx); fy=fy*fy*(3-2*fy)
    return (g[y0,x0]*(1-fx)+g[y0,x1]*fx)*(1-fy)+(g[y1,x0]*(1-fx)+g[y1,x1]*fx)*fy
def ramp(cols,t):
    t=np.clip(t,0,0.9999)*(len(cols)-1); i=t.astype(int); f=(t-i)[...,None]
    c=np.array(cols,float); return c[i]*(1-f)+c[np.minimum(i+1,len(cols)-1)]*f
def img(rgb,a=None):
    out=np.zeros((16,16,4),np.uint8); out[...,:3]=np.clip(rgb,0,255).astype(np.uint8); out[...,3]=255 if a is None else a
    return Image.fromarray(out)
def mix(*n): 
    return sum(n)/len(n)
STONE=[(6,14,24),(12,28,42),(20,46,64),(32,70,92),(46,96,120)]
CY=[(8,70,90),(14,120,140),(22,178,200),(70,226,240),(170,250,255)]
VI=[(24,12,60),(52,28,108),(86,52,170),(140,100,235),(214,180,255)]
BONE=[(60,86,100),(120,160,176),(176,208,220),(214,236,242),(240,250,252)]

def stone_base(seed):
    n=mix(vn(seed,4),vn(seed+1,8)*1.0)
    rgb=ramp(STONE,n*0.9+np.random.RandomState(seed).rand(16,16)*0.18)
    return rgb
def cracks(rgb,seed,n=3,col=(4,10,18)):
    r=random.Random(seed)
    for _ in range(n):
        x,y=r.randint(0,15),r.randint(0,15)
        for _ in range(r.randint(4,8)):
            rgb[y%16,x%16]=col; x+=r.choice((-1,0,1,1)); y+=r.choice((0,1,1))
    return rgb
def veins(rgb,seed,n=2):
    r=random.Random(seed)
    for _ in range(n):
        x,y=r.randint(0,15),r.randint(0,15)
        for k in range(r.randint(3,6)):
            rgb[y%16,x%16]=CY[2] if k%2 else CY[1]; x+=r.choice((-1,1)); y+=r.choice((0,1))
        rgb[y%16,x%16]=CY[4]
    return rgb

T={}
# --- piedra sculk
rgb=stone_base(1); rgb=cracks(rgb,11,3); rgb=veins(rgb,12,2); T["sculk_stone"]=img(rgb)
# --- musgo eco arriba
n=mix(vn(2,4),vn(3,8),np.random.RandomState(2).rand(16,16)*0.6)
rgb=ramp(CY,n*0.85+0.05); r=random.Random(4)
for _ in range(14): rgb[r.randint(0,15),r.randint(0,15)]=CY[3]
for _ in range(4): rgb[r.randint(0,15),r.randint(0,15)]=CY[4]
T["echo_moss_top"]=img(rgb)
# --- musgo eco lado (piedra + flequillo + mechones)
rgb=stone_base(5); rgb=cracks(rgb,13,2); r=random.Random(6)
for x in range(16):
    hgt=4+r.randint(0,2)+(1 if x%5==2 else 0)
    for y in range(hgt):
        c=CY[2] if y<hgt-2 else CY[1] if y<hgt-1 else CY[0]
        rgb[y,x]=np.array(c)*(0.85+0.3*r.random())
    if r.random()<0.35: rgb[hgt,x]=CY[0]
for _ in range(3): rgb[r.randint(0,3),r.randint(0,15)]=CY[3]
T["echo_moss_side"]=img(rgb)
# --- sculk crepuscular
n=mix(vn(7,4),vn(8,8),np.random.RandomState(7).rand(16,16)*0.6)
rgb=ramp(VI,n*0.85+0.05); r=random.Random(9)
for _ in range(14): rgb[r.randint(0,15),r.randint(0,15)]=VI[3]
for _ in range(5): rgb[r.randint(0,15),r.randint(0,15)]=VI[4]
T["twilight_sculk_top"]=img(rgb)
rgb=stone_base(10); rgb=cracks(rgb,14,2)
for x in range(16):
    hgt=4+r.randint(0,2)+(1 if x%4==1 else 0)
    for y in range(hgt):
        c=VI[2] if y<hgt-2 else VI[1] if y<hgt-1 else VI[0]
        rgb[y,x]=np.array(c)*(0.85+0.3*r.random())
T["twilight_sculk_side"]=img(rgb)
# --- ladrillos con bisel
rgb=np.zeros((16,16,3)); r=np.random.RandomState(15)
for by in range(2):
    for bx in range(2):
        off=4 if by else 0
        for y in range(8):
            for x in range(8):
                X=(bx*8+x+off)%16; Y=by*8+y
                if y==0 or x==0+0 and False: c=(4,10,18)
                base=np.array(STONE[2])*(0.85+0.3*r.rand())
                if y==1: base=np.array(STONE[4])
                elif y==7: base=np.array(STONE[1])
                if y==0 or x==7+0 and False: base=np.array((4,10,18))
                if x==0: base=np.array((4,10,18))
                elif x==1 and y not in (0,): base=np.maximum(base,np.array(STONE[3]))
                rgb[Y,X]=base
rgb=veins(rgb,16,1); T["sculk_bricks"]=img(rgb)
# --- tronco: lado
rgb=np.zeros((16,16,3)); r=np.random.RandomState(17)
col=r.rand(16)
for x in range(16):
    for y in range(16):
        g=(x%4)
        base=np.array((10,30,44)) if g in (0,1) else np.array((14,42,60))
        if g==3: base=np.array((22,60,82))
        rgb[y,x]=base*(0.85+0.3*r.rand()+0.1*np.sin(y*0.8+x))
for x in (1,9):  # savia luminosa
    for y in range(16):
        if (y+x)%5!=0: rgb[y,x]=np.array(CY[2])*(0.7+0.3*np.sin(y*0.7))
rgb[3,1]=CY[4]; rgb[11,9]=CY[4]
T["resonant_log"]=img(rgb)
# --- tronco: tapa
rgb=np.zeros((16,16,3))
for y in range(16):
    for x in range(16):
        d=max(abs(x-7.5),abs(y-7.5)); dd=np.hypot(x-7.5,y-7.5)
        if d>7: rgb[y,x]=(8,22,34)
        else:
            ring=int(dd)%3
            rgb[y,x]=[(20,70,92),(12,40,58),(16,52,72)][ring]
rgb[7:9,7:9]=CY[3]; T["resonant_log_top"]=img(rgb)
# --- hojas cian / violeta con venas y puntos brillantes
def leaves(pal,seed):
    r=np.random.RandomState(seed); n=mix(vn(seed,4),vn(seed+1,8))
    rgb=ramp(pal,0.15+n*0.7+r.rand(16,16)*0.12); a=np.full((16,16),255,np.uint8)
    for y in range(16):
        for x in range(16):
            if (x+y*2)%7==0 and r.rand()<0.7: rgb[y,x]=np.array(pal[0])
    for _ in range(26): rgb[r.randint(16),r.randint(16)]=pal[3]
    for _ in range(5): rgb[r.randint(16),r.randint(16)]=pal[4]
    holes=r.rand(16,16)<0.12; a[holes]=0
    return img(rgb,a)
T["resonant_leaves"]=leaves(CY,20); T["twilight_leaves"]=leaves(VI,21)
# --- cristal luminoso facetado
rgb=np.zeros((16,16,3)); r=np.random.RandomState(22)
for y in range(16):
    for x in range(16):
        f=((x-y)//4)%3; d=max(abs(x-7.5),abs(y-7.5))/7.5
        base=np.array([CY[2],CY[3],CY[1]][f])*(1.1-0.4*d)
        rgb[y,x]=base*(0.92+0.16*r.rand())
for i in range(16):
    for p in ((i,0),(i,15),(0,i),(15,i)): rgb[p[1],p[0]]=CY[0]
for p in ((5,5),(6,6),(7,7),(8,8),(10,4),(4,10)): rgb[p[1],p[0]]=CY[4]
T["glow_crystal_block"]=img(rgb)
# --- marco del warden con runa
rgb=np.zeros((16,16,3)); r=np.random.RandomState(23)
for y in range(16):
    for x in range(16):
        e=min(x,y,15-x,15-y)
        if e==0: c=np.array(STONE[4])
        elif e==1: c=np.array(STONE[2])
        elif e==2: c=np.array((6,12,20))
        else: c=np.array((10,22,34))*(0.8+0.4*r.rand())
        rgb[y,x]=c
for p in ((1,1),(14,1),(1,14),(14,14)): rgb[p[1],p[0]]=CY[3]
rune=["....##....","...####...","..##..##..",".##.##.##.","##.####.##","##.####.##",".##.##.##.","..##..##..","...####...","....##...."]
for j,row in enumerate(rune):
    for i,ch in enumerate(row):
        if ch=="#": rgb[3+j,3+i]=CY[3] if (i+j)%2 else CY[4]
T["warden_frame"]=img(rgb)
# --- hueso del warden (pilar)
rgb=np.zeros((16,16,3)); r=np.random.RandomState(24)
for y in range(16):
    for x in range(16):
        g=x%8; base=np.array(BONE[2]) if g in (2,3,4) else np.array(BONE[1])
        if g in (0,7): base=np.array(BONE[0])
        rgb[y,x]=base*(0.92+0.16*r.rand())*(1+0.08*np.sin(y*0.6))
for _ in range(6): rgb[r.randint(16),r.randint(16)]=BONE[4]
for _ in range(5): rgb[r.randint(16),r.randint(16)]=CY[1]
T["warden_bone"]=img(rgb)
rgb=np.zeros((16,16,3))
for y in range(16):
    for x in range(16):
        d=np.hypot(x-7.5,y-7.5); rgb[y,x]=[BONE[3],BONE[2],BONE[1],BONE[2]][int(d)%4] if d<7.6 else BONE[0]
rgb[7:9,7:9]=CY[1]; T["warden_bone_top"]=img(rgb)
# --- hongo luminoso
im=np.zeros((16,16,4),np.uint8); r=random.Random(25)
def px(x,y,c): 
    if 0<=x<16 and 0<=y<16: im[y,x]=list(map(int,c))+[255]
for (cx,cy,rad,base) in ((8,5,4,CY),(3,10,2,CY),(13,11,2,VI)):
    for y in range(cy-rad,cy+2):
        for x in range(cx-rad-1,cx+rad+2):
            if ((x-cx)/(rad+0.5))**2+((y-cy)/(rad*0.8))**2<=1 and y<=cy+1:
                t=1-(y-(cy-rad))/(rad*1.6); px(x,y,base[3] if (x*3+y)%5==0 else base[2] if t>0.4 else base[1])
    stem=cy+2
    for y in range(stem,16): px(cx,y,STONE[4]); 
for y in range(2,6): px(7,y,CY[4]) if y==3 else None
T["glowcap"]=Image.fromarray(im)
# --- hebra colgante
im=np.zeros((16,16,4),np.uint8)
for y in range(16):
    px(8,y,STONE[3] if y%4 else CY[1])
    if y in (5,11,14): px(8,y,CY[3]); px(7,y,CY[2]); px(9,y,CY[2])
px(8,15,CY[4]); px(8,7,VI[2]) if False else None
T["dangling_strand"]=Image.fromarray(im)
# --- portal animado (4 frames)
pt=Image.new("RGBA",(16,64)); r=np.random.RandomState(30)
for f in range(4):
    ph=f*np.pi/2
    for y in range(16):
        for x in range(16):
            a=np.sin(x*0.55+ph)+np.sin(y*0.5-ph)+np.sin((x+y)*0.4+ph*0.5)
            v=(a+3)/6; c=np.array(CY[1])*(1-v)+np.array(VI[3])*v*0.9+np.array(CY[3])*(0.25*np.sin((x-y)*0.6+ph)+0.25)
            if r.rand()<0.025: c=np.array(CY[4])
            pt.putpixel((x,f*16+y),tuple(np.clip(c,0,255).astype(int))+(175,))
T["warden_portal"]=pt
for k,v in T.items(): v.save(f"{TEX}/{k}.png")
open(f"{TEX}/warden_portal.png.mcmeta","w").write(json.dumps({"animation":{"frametime":4,"interpolate":True}}))
print("texturas:",len(T))
