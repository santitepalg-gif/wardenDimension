import numpy as np, math, os, random
from PIL import Image, ImageFilter, ImageDraw, ImageFont
TEX="/home/claude/warden_dimension/src/main/resources/assets/warden_dimension/textures/block"
def load(n):
    return np.array(Image.open(f"{TEX}/{n}.png").convert("RGBA")).astype(np.float32)
T={n:load(n) for n in ["sculk_stone","echo_moss_top","echo_moss_side","resonant_log","resonant_log_top","resonant_leaves","glow_crystal_block","sculk_bricks","warden_frame","twilight_sculk_top","twilight_sculk_side","glowcap"]}
portal_f=np.array(Image.open(f"{TEX}/warden_portal.png").convert("RGBA")).astype(np.float32)[16:32]
T["warden_portal"]=portal_f
vanilla_sculk=np.zeros((16,16,4),np.float32); rr=np.random.RandomState(3)
vanilla_sculk[...,:3]=np.array([14,40,56])+rr.randint(-6,8,(16,16,1)); vanilla_sculk[...,3]=255
vanilla_sculk[rr.rand(16,16)<0.18,:3]=[30,170,210]
T["sculk"]=vanilla_sculk
deep=np.zeros((16,16,4),np.float32); deep[...,:3]=np.array([22,26,34])+rr.randint(-5,6,(16,16,1)); deep[...,3]=255; T["deepslate"]=deep

# ids
AIR,STONE,MOSS,TWI,SCULK,BRICK,LOG,LEAF,CRYS,FRAME,PORTAL,CAP,DEEP=range(13)
SX,SY,SZ=110,70,110
W=np.zeros((SX,SY,SZ),np.uint8)
rng=np.random.RandomState(7)
def smooth(a,k):
    from PIL import Image
    im=Image.fromarray(((a-a.min())/(a.max()-a.min())*255).astype(np.uint8)).resize((SX,SZ),Image.BICUBIC)
    return np.array(im).astype(np.float32)/255
n1=smooth(rng.rand(9,9),0); n2=smooth(rng.rand(18,18),0)
h=(22+16*n1+6*n2).astype(int)
# biomas por zona: bosque (centro/izq), marsh (derecha), crystal (fondo)
biome=np.zeros((SX,SZ),int)
for x in range(SX):
    for z in range(SZ):
        if x>72: biome[x,z]=1
        if z>82: biome[x,z]=2
        if x<18 and z>60: biome[x,z]=3
# plataforma del portal (zona plana cerca de cámara)
px,pz=40,26
for x in range(SX):
    for z in range(SZ):
        d=math.hypot(x-px,z-pz)
        d2=math.hypot(x-(px+4),z-(pz-8))
        k=min(1.0,max(0.0,(d2-6)/22.0)); k=k*k*(3-2*k)
        h[x,z]=int(26*(1-k)+h[x,z]*k)
        if d<9: h[x,z]=int(h[x,z]*(d/9)**2+ (26)*(1-(d/9)**2))
for x in range(SX):
    for z in range(SZ):
        top=h[x,z]
        for y in range(top+1):
            W[x,y,z]=DEEP if y<top-4 else STONE
        b=biome[x,z]
        W[x,top,z]={0:MOSS,1:TWI,2:BRICK,3:SCULK}[b]
        if b==3: 
            for y in range(top-3,top): W[x,y,z]=DEEP
def setb(x,y,z,v,only_air=True):
    if 0<=x<SX and 0<=y<SY and 0<=z<SZ and (not only_air or W[x,y,z]==AIR): W[x,y,z]=v
def tree(x,z,hh,big):
    y0=h[x,z]+1
    for y in range(y0,y0+hh): setb(x,y,z,LOG)
    r=4 if big else 3
    for dy in range(-2,3):
        rad=r-abs(dy)//1 if big else r-abs(dy)
        for dx in range(-rad,rad+1):
            for dz in range(-rad,rad+1):
                if dx*dx+dz*dz<=rad*rad+1 and rng.rand()>0.12: setb(x+dx,y0+hh+dy,z+dz,LEAF)
    # cristales colgando
    for _ in range(3):
        dx,dz=rng.randint(-r,r+1),rng.randint(-r,r+1)
        if W[x+dx,y0+hh-3,z+dz]==AIR and W[x+dx,y0+hh-2,z+dz]==LEAF: W[x+dx,y0+hh-3,z+dz]=CRYS
for _ in range(300):
    x,z=rng.randint(4,SX-4),rng.randint(4,SZ-4)
    if math.hypot(x-px,z-pz)<11 or abs(x-40)<3 and z<40: continue
    b=biome[x,z]
    if b==0 and rng.rand()<0.35: tree(x,z,rng.randint(6,11),rng.rand()<0.5)
    elif b==1 and rng.rand()<0.12: tree(x,z,rng.randint(4,6),False)
for _ in range(700):
    x,z=rng.randint(0,SX),rng.randint(0,SZ)
    if W[x,h[x,z]+1,z]==AIR and biome[x,z]in(0,1,2) and rng.rand()<0.45 and math.hypot(x-px,z-pz)>5: W[x,h[x,z]+1,z]=CAP
for _ in range(60):  # espigas de cristal
    x,z=rng.randint(0,SX),rng.randint(60,SZ)
    if biome[x,z]==2:
        for y in range(h[x,z]+1,h[x,z]+1+rng.randint(3,10)): setb(x,y,z,CRYS)
# portal + marco (eje X) en px,pz
by=h[px,pz]+1
for a in range(-1,3):
    for hh in range(-1,4):
        border=a in(-1,2) or hh in(-1,3)
        W[px+a,by+hh,pz]=FRAME if border else PORTAL
for a in range(-3,5):
    for b in range(-3,4): W[px+a,h[px,pz],pz+b]=BRICK
# farolas de cristal junto al portal
for (lx,lz) in ((px-3,pz+3),(px+4,pz+3)):
    for y in range(by,by+3): W[lx,y,lz]=BRICK
    W[lx,by+3,lz]=CRYS
# camara
cam=np.array([px+4.5,h[px+4,pz-10]+2.6,pz-10.0])
look=np.array([px+0.5,by+2.8,pz])
fwd=look-cam; fwd/=np.linalg.norm(fwd)
up0=np.array([0,1,0.]); rgt=np.cross(fwd,up0); rgt/=np.linalg.norm(rgt); up=np.cross(rgt,fwd)
RW,RH=640,360
fov=math.radians(70); sc=math.tan(fov/2)
us=(np.arange(RW)+0.5)/RW*2-1; vs=1-(np.arange(RH)+0.5)/RH*2
U,V=np.meshgrid(us*sc*(RW/RH),vs*sc)
dirs=fwd[None,None]+U[...,None]*rgt+V[...,None]*up
dirs/= np.linalg.norm(dirs,axis=2,keepdims=True)
N=RW*RH; D=dirs.reshape(N,3).astype(np.float64); O=np.tile(cam,(N,1))
D[np.abs(D)<1e-9]=1e-9
vox=np.floor(O).astype(int); step=np.sign(D).astype(int)
tdelta=np.abs(1/D); nxt=np.where(step>0,vox+1-O,O-vox)*tdelta
t=np.zeros(N); hit=np.zeros(N,bool); hid=np.zeros(N,int); face=np.zeros(N,int); hpos=np.zeros((N,3))
col=np.zeros((N,3)); alpha_acc=np.zeros(N); 
alive=np.ones(N,bool); glow=np.zeros((N,3))
# translucidos (portal) acumulan
port_col=np.zeros((N,3)); port_a=np.zeros(N)
texmap={STONE:"sculk_stone",BRICK:"sculk_bricks",LOG:"resonant_log",LEAF:"resonant_leaves",CRYS:"glow_crystal_block",FRAME:"warden_frame",CAP:"glowcap",DEEP:"deepslate",SCULK:"sculk"}
def sample(name,u,v):
    a=T[name]; iu=np.clip((u*16).astype(int),0,15); iv=np.clip((v*16).astype(int),0,15); return a[iv,iu]
emis={CRYS:1.0,PORTAL:0.9,CAP:0.7,LEAF:0.18,FRAME:0.25}
for it in range(220):
    axis=np.argmin(nxt,axis=1)
    idx=np.arange(N)
    t=nxt[idx,axis]
    nxt[idx,axis]+=tdelta[idx,axis]
    vox[idx,axis]+=step[idx,axis]
    inb=(vox[:,0]>=0)&(vox[:,0]<SX)&(vox[:,1]>=0)&(vox[:,1]<SY)&(vox[:,2]>=0)&(vox[:,2]<SZ)
    alive&=inb
    b=np.zeros(N,int); b[alive]=W[vox[alive,0],vox[alive,1],vox[alive,2]]
    cand=alive&(~hit)&(b!=AIR)
    if not cand.any(): 
        if not (alive&~hit).any(): break
        continue
    hp=O[cand]+D[cand]*t[cand,None]
    ax=axis[cand]; st=step[cand,ax_idx] if False else step[cand][np.arange(cand.sum()),ax]
    loc=hp-vox[cand]
    # coordenadas uv segun eje de la cara
    u=np.where(ax==0,loc[:,2],loc[:,0]); v=np.where(ax==1,loc[:,2],1-loc[:,1])
    u=np.mod(u,1.0); v=np.mod(v,1.0)
    bb=b[cand]; out=np.zeros((cand.sum(),4))
    for bid in np.unique(bb):
        m=bb==bid
        if bid in texmap: out[m]=sample(texmap[bid],u[m],v[m])
        elif bid==MOSS or bid==TWI:
            pre="echo_moss" if bid==MOSS else "twilight_sculk"
            topm=m&(ax==1)&(st==-1)
            sidem=m&~topm
            if topm.any(): out[topm]=sample(pre+"_top",u[topm],v[topm])
            if sidem.any(): out[sidem]=sample(pre+"_side",u[sidem],v[sidem])
        elif bid==PORTAL:
            out[m]=sample("warden_portal",u[m],v[m])
    sel=np.where(cand)[0]
    for k in range(len(sel)):
        pass
    A=out[:,3]/255.0
    # portal/hojas con alpha
    ids=sel
    for bid in np.unique(bb):
        m=bb==bid; ii=ids[m]
        if bid==PORTAL:
            a=0.55
            rem=1-port_a[ii]
            port_col[ii]+=out[m,:3]*(a*rem)[:,None]*1.2; port_a[ii]+=a*rem
            continue
        solid=out[m,3]>128
        ii_s=ii[solid]
        hit[ii_s]=True; hid[ii_s]=bid; face[ii_s]=ax[m][solid]*2+(st[m][solid]>0)
        hpos[ii_s]=hp[m][solid]
        col[ii_s]=out[m,:3][solid]
        alpha_acc[ii_s]=t[ii_s]
    if hit[alive].all() if alive.any() else True: break
    # rayos que ya golpearon dejan de avanzar
    alive&=~hit
# iluminacion: caras
shade_f=np.array([0.78,0.78,1.0,0.5,0.86,0.86])  # por axis*2+dir (x+,x-,y+,y-,z+,z-) aprox
fa=face.copy(); 
fshade=np.array([0.80,0.80,1.0,0.55,0.88,0.88])[fa]
# luz de bloques emisivos: grilla de emisores
em_pos=np.argwhere((W==CRYS)|(W==PORTAL)|(W==CAP)|(W==FRAME))
em_w=np.array([emis[W[tuple(p)]] for p in em_pos])
from scipy.spatial import cKDTree
tree_k=cKDTree(em_pos+0.5)
hp_all=hpos
dist,ind=tree_k.query(hp_all,k=6,distance_upper_bound=9.0)
light=np.zeros(N)
for k in range(6):
    d=dist[:,k]; ok=np.isfinite(d)
    contrib=np.zeros(N); contrib[ok]=em_w[ind[ok,k]]*np.clip(1-d[ok]/9.0,0,1)**2
    light+=contrib
light=np.clip(light,0,1.1)
amb=0.62
base=col*fshade[:,None]*(amb+0.9*light[:,None]) 
# tinte azul-cian de la luz
tint=np.array([0.55,1.0,1.1])
base=base*(0.6+0.5*tint[None,:]*(0.5+0.5*light[:,None]))
# niebla por distancia
fogc=np.array([14,70,96.0])
tdist=np.where(hit,alpha_acc,200.0)
fog=1-np.exp(-(tdist/46.0)**1.5)
base=base*(1-fog[:,None])+fogc*fog[:,None]*0.9
# cielo para rayos sin impacto
ydir=D[:,1]
skyc=np.zeros((N,3))
g=np.clip(ydir,0,1)
skyc[:]=fogc*0.9
skyc=skyc*(1-g[:,None]**0.6)+np.array([2,6,16.])*(g[:,None]**0.6)
# nebulosas / estrellas
az=np.arctan2(D[:,0],D[:,2])
neb=(np.sin(az*3+ydir*9)*0.5+0.5)*(np.sin(az*5-ydir*6+1.3)*0.5+0.5)*np.clip(ydir*2.2,0,1)
skyc+=np.outer(neb**2*0.9,[40,190,235])*0.5+np.outer((np.sin(az*2.2+ydir*4)*0.5+0.5)**4*np.clip(ydir*1.5,0,1),[130,70,230])*0.45
srng=np.random.RandomState(1); stars=srng.rand(N)<0.0016
skyc[stars&(ydir>0.05)]+=[200,230,255]
final=np.where(hit[:,None],base,skyc)
# portal por encima
pa=np.clip(port_a,0,0.8)[:,None]
final=final*(1-pa)+port_col*1.0
img=np.clip(final,0,255).reshape(RH,RW,3).astype(np.uint8)
im=Image.fromarray(img)
# bloom
big=im.resize((1280,720),Image.NEAREST)
arr=np.array(big).astype(np.float32)
bright=np.clip(arr-120,0,255)
bl=Image.fromarray(bright.astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
arr=np.clip(arr+np.array(bl).astype(np.float32)*1.1,0,255)
# vineta
yy,xx=np.mgrid[0:720,0:1280]; r=np.sqrt(((xx-640)/760)**2+((yy-360)/460)**2)
arr*= (1-0.55*np.clip(r-0.35,0,1)**1.6)[...,None]
out=Image.fromarray(arr.astype(np.uint8))
d=ImageDraw.Draw(out)
out.save("/home/claude/preview_dimension.png")
print("ok")
