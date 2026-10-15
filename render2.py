import numpy as np, math, sys
from PIL import Image, ImageFilter
from scipy.spatial import cKDTree
TEX="/home/claude/warden_dimension/src/main/resources/assets/warden_dimension/textures/block"
def load(n): return np.array(Image.open(f"{TEX}/{n}.png").convert("RGBA")).astype(np.float32)
names=["sculk_stone","echo_moss_top","echo_moss_side","resonant_log","resonant_log_top","resonant_leaves","twilight_leaves","glow_crystal_block","sculk_bricks",
       "warden_frame","twilight_sculk_top","twilight_sculk_side","glowcap","warden_bone","warden_bone_top","dangling_strand"]
T={n:load(n) for n in names}
T["warden_portal"]=np.array(Image.open(f"{TEX}/warden_portal.png").convert("RGBA")).astype(np.float32)[16:32]
rr=np.random.RandomState(3)
sk=np.zeros((16,16,4),np.float32); sk[...,:3]=np.array([14,40,56])+rr.randint(-6,8,(16,16,1)); sk[...,3]=255; sk[rr.rand(16,16)<0.18,:3]=[30,170,210]; T["sculk"]=sk
dp=np.zeros((16,16,4),np.float32); dp[...,:3]=np.array([22,26,34])+rr.randint(-5,6,(16,16,1)); dp[...,3]=255; T["deepslate"]=dp
(AIR,STONE,MOSS,TWI,SCULK,BRICK,LOG,LEAF,CRYS,FRAME,PORTAL,CAP,DEEP,TLEAF,BONE,STRAND)=range(16)
SX,SY,SZ=150,80,150
W=np.zeros((SX,SY,SZ),np.uint8); rng=np.random.RandomState(11)
def smooth(a):
    im=Image.fromarray(((a-a.min())/(a.max()-a.min())*255).astype(np.uint8)).resize((SX,SZ),Image.BICUBIC); return np.array(im).astype(np.float32)/255
h=(24+9*smooth(rng.rand(8,8))+3*smooth(rng.rand(20,20))).astype(int)
biome=np.zeros((SX,SZ),int)
for x in range(SX):
    for z in range(SZ):
        biome[x,z]=(0 if x<60 else 1) if z<80 else (2 if x<75 else 3)
px,pz=30,30
for x in range(SX):
    for z in range(SZ):
        d=math.hypot(x-px,z-pz); k=min(1,max(0,(d-5)/14)); k=k*k*(3-2*k); h[x,z]=int(26*(1-k)+h[x,z]*k)
for x in range(SX):
    for z in range(SZ):
        t=h[x,z]
        for y in range(t+1): W[x,y,z]=DEEP if y<t-4 else STONE
        W[x,t,z]=[MOSS,TWI,SCULK,BRICK][biome[x,z]]
def setb(x,y,z,v,over=False):
    if 0<=x<SX and 0<=y<SY and 0<=z<SZ and (W[x,y,z]==AIR or (over and W[x,y,z] in (LEAF,TLEAF,STRAND,CAP))): W[x,y,z]=v
def strand(x,y,z,n):
    for i in range(1,n+1):
        if 0<=y-i and W[x,y-i,z]==AIR: W[x,y-i,z]=STRAND
        else: break
def blob(cx,cy,cz,r,leaf):
    for dx in range(-r,r+1):
        for dy in range(-r,r+1):
            for dz in range(-r,r+1):
                if dx*dx+dy*dy+dz*dz<=r*r+1 and rng.randint(7)!=0: setb(cx+dx,cy+dy,cz+dz,leaf)
def spire(x,z):
    H=rng.randint(14,22); ph=rng.rand()*6.283; ox=round(math.sin(ph)*1.5); oz=round(math.cos(ph)*1.5); y0=h[x,z]+1; cs=[]
    for y in range(H):
        cx=round(math.sin(y*.3+ph)*1.5)-ox; cz=round(math.cos(y*.3+ph)*1.5)-oz; cs.append((cx,cz))
        setb(x+cx,y0+y,z+cz,LOG,True)
        if y>0: setb(x+cx,y0+y-1,z+cz,LOG,True)
        if y<4:
            for dx,dz in((1,0),(-1,0),(0,1),(0,-1)):
                if y<2 or rng.rand()<.5: setb(x+cx+dx,y0+y,z+cz+dz,LOG)
    for t in range(4):
        ty=H-10+t*3
        if ty<5: continue
        rad=6-t; cx,cz=cs[min(ty,H-1)]
        for dx in range(-rad,rad+1):
            for dz in range(-rad,rad+1):
                d=math.hypot(dx,dz)
                if d>rad+.3: continue
                setb(x+cx+dx,y0+ty,z+cz+dz,LEAF)
                if d>rad-2.2: setb(x+cx+dx,y0+ty+1,z+cz+dz,LEAF)
                if d>rad-1.2 and rng.rand()<.33: strand(x+cx+dx,y0+ty,z+cz+dz,rng.randint(2,7))
                elif d<rad-2 and rng.rand()<.07: setb(x+cx+dx,y0+ty-1,z+cz+dz,CRYS)
    cx,cz=cs[-1]
    for i in range(3): setb(x+cx,y0+H+i,z+cz,CRYS)
def weeper(x,z):
    H=rng.randint(8,12); lean=rng.randint(3,6); a=rng.rand()*6.283; y0=h[x,z]+1; top=(x,y0,z)
    for y in range(H):
        k=(y/H)**2; top=(x+round(math.cos(a)*lean*k),y0+y,z+round(math.sin(a)*lean*k)); setb(*top,LOG,True)
        if y>0: setb(top[0],top[1]-1,top[2],LOG,True)
    nb=rng.randint(5,7)
    for i in range(nb):
        b=a+i*6.283/nb+rng.rand()*.4; L=rng.randint(5,8)
        for s in range(1,L+1):
            u=s/L; by=round(math.sin(u*math.pi*.8)*2.5-((u-.6)*6 if u>.6 else 0))
            p=(top[0]+round(math.cos(b)*s),top[1]+by,top[2]+round(math.sin(b)*s))
            if s<=L//2: setb(*p,LOG,True)
            if s>=2: blob(*p,1,TLEAF)
            if s>=L//2 and rng.rand()<.8: strand(p[0],p[1]-1,p[2],rng.randint(3,9))
    blob(top[0],top[1]+1,top[2],2,TLEAF)
def ribs(x,z):
    H=rng.randint(9,13); y0=h[x,z]+1
    for y in range(H): setb(x,y0+y,z,BONE)
    for dx,dz in((1,0),(-1,0),(0,1),(0,-1)): setb(x+dx,y0,z+dz,BONE)
    setb(x,y0+H,z,CRYS); ax=rng.rand()<.5
    for p in range(rng.randint(3,5)):
        yy=H-2-p*2
        if yy<3: break
        rad=6-p//2+rng.randint(0,2); drop=rng.randint(5,7)
        for side in(-1,1):
            for i in range(15):
                th=math.pi*.5*i/14; dx=side*round(rad*math.sin(th)); dy=-round(drop*(1-math.cos(th)))
                px_,pz_=(x+dx,z) if ax else (x,z+dx)
                setb(px_,y0+yy+dy,pz_,BONE)
                if i==14: strand(px_,y0+yy+dy,pz_,rng.randint(2,5))
def cluster(x,z):
    for i in range(rng.randint(4,8)):
        xx=x+(0 if i==0 else rng.randint(-3,4)); zz=z+(0 if i==0 else rng.randint(-3,4))
        if not(0<=xx<SX and 0<=zz<SZ): continue
        hh=rng.randint(9,15) if i==0 else rng.randint(3,9); lx,lz=(rng.rand()-.5)*.7,(rng.rand()-.5)*.7
        for s in range(hh): setb(xx+round(lx*s),h[xx,zz]+1+s,zz+round(lz*s),CRYS)
for _ in range(700):
    x,z=rng.randint(6,SX-6),rng.randint(6,SZ-6)
    if math.hypot(x-px,z-pz)<9: continue
    b=biome[x,z]; r_=rng.rand()
    if b==0 and r_<.07: spire(x,z)
    elif b==1 and r_<.10: weeper(x,z)
    elif b==2 and r_<.05: ribs(x,z)
    elif b==3 and r_<.05: cluster(x,z)
for _ in range(1800):
    x,z=rng.randint(0,SX),rng.randint(0,SZ)
    if W[x,h[x,z]+1,z]==AIR and rng.rand()<.5 and math.hypot(x-px,z-pz)>4: W[x,h[x,z]+1,z]=CAP
by=h[px,pz]+1
for a in range(-1,3):
    for hh in range(-1,4): W[px+a,by+hh,pz]=FRAME if (a in(-1,2) or hh in(-1,3)) else PORTAL
for a in range(-3,5):
    for b in range(-3,4): W[px+a,h[px,pz],pz+b]=BRICK
for lx,lz in((px-3,pz+3),(px+4,pz+3)):
    for y in range(by,by+3): W[lx,y,lz]=BRICK
    W[lx,by+3,lz]=CRYS
texmap={STONE:"sculk_stone",BRICK:"sculk_bricks",LOG:"resonant_log",LEAF:"resonant_leaves",TLEAF:"twilight_leaves",CRYS:"glow_crystal_block",FRAME:"warden_frame",
        CAP:"glowcap",DEEP:"deepslate",SCULK:"sculk",STRAND:"dangling_strand"}
emis={CRYS:1.0,PORTAL:0.9,CAP:0.7,LEAF:0.2,TLEAF:0.18,FRAME:0.25,STRAND:0.55}
em_pos=np.argwhere(np.isin(W,list(emis.keys()))); em_w=np.array([emis[W[tuple(p)]] for p in em_pos]); kd=cKDTree(em_pos+0.5)
def sample(n,u,v):
    a=T[n]; return a[np.clip((v*16).astype(int),0,15),np.clip((u*16).astype(int),0,15)]
def render(cam,look,fogc,tint,neb1,neb2,out,RW=640,RH=360):
    cam=np.array(cam,float); look=np.array(look,float); fwd=look-cam; fwd/=np.linalg.norm(fwd)
    rgt=np.cross(fwd,[0,1,0.]); rgt/=np.linalg.norm(rgt); up=np.cross(rgt,fwd); sc=math.tan(math.radians(70)/2)
    us=(np.arange(RW)+.5)/RW*2-1; vs=1-(np.arange(RH)+.5)/RH*2; U,V=np.meshgrid(us*sc*RW/RH,vs*sc)
    Dv=(fwd[None,None]+U[...,None]*rgt+V[...,None]*up); Dv/=np.linalg.norm(Dv,axis=2,keepdims=True)
    N=RW*RH; D=Dv.reshape(N,3).astype(np.float64); O=np.tile(cam,(N,1)); D[np.abs(D)<1e-9]=1e-9
    vox=np.floor(O).astype(int); step=np.sign(D).astype(int); td=np.abs(1/D); nxt=np.where(step>0,vox+1-O,O-vox)*td
    hit=np.zeros(N,bool); face=np.zeros(N,int); hpos=np.zeros((N,3)); col=np.zeros((N,3)); hd=np.zeros(N)
    alive=np.ones(N,bool); pc=np.zeros((N,3)); pa=np.zeros(N); idx=np.arange(N)
    for it in range(260):
        ax=np.argmin(nxt,axis=1); t=nxt[idx,ax]; nxt[idx,ax]+=td[idx,ax]; vox[idx,ax]+=step[idx,ax]
        inb=(vox[:,0]>=0)&(vox[:,0]<SX)&(vox[:,1]>=0)&(vox[:,1]<SY)&(vox[:,2]>=0)&(vox[:,2]<SZ); alive&=inb
        b=np.zeros(N,int); b[alive]=W[vox[alive,0],vox[alive,1],vox[alive,2]]
        cand=alive&(~hit)&(b!=AIR)
        if cand.any():
            sel=np.where(cand)[0]; hp=O[sel]+D[sel]*t[sel,None]; a_=ax[sel]; st=step[sel,a_]; loc=hp-vox[sel]
            u=np.mod(np.where(a_==0,loc[:,2],loc[:,0]),1.0); v=np.mod(np.where(a_==1,loc[:,2],1-loc[:,1]),1.0); bb=b[sel]; o4=np.zeros((len(sel),4))
            for bid in np.unique(bb):
                m=bb==bid
                if bid in texmap: o4[m]=sample(texmap[bid],u[m],v[m])
                elif bid in(MOSS,TWI):
                    pre="echo_moss" if bid==MOSS else "twilight_sculk"; tp=m&(a_==1)&(st==-1); sd=m&~tp
                    if tp.any(): o4[tp]=sample(pre+"_top",u[tp],v[tp])
                    if sd.any(): o4[sd]=sample(pre+"_side",u[sd],v[sd])
                elif bid==BONE:
                    tp=m&(a_==1); sd=m&~tp
                    if tp.any(): o4[tp]=sample("warden_bone_top",u[tp],v[tp])
                    if sd.any(): o4[sd]=sample("warden_bone",u[sd],v[sd])
                elif bid==PORTAL: o4[m]=sample("warden_portal",u[m],v[m])
            for bid in np.unique(bb):
                m=bb==bid; ii=sel[m]
                if bid==PORTAL:
                    rem=1-pa[ii]; pc[ii]+=o4[m,:3]*(0.55*rem)[:,None]*1.2; pa[ii]+=0.55*rem; continue
                s=o4[m,3]>128; i2=ii[s]; hit[i2]=True; face[i2]=a_[m][s]*2+(st[m][s]>0); hpos[i2]=hp[m][s]; col[i2]=o4[m,:3][s]; hd[i2]=t[i2]
        alive&=~hit
        if not alive.any(): break
    fs=np.array([.80,.80,1.0,.55,.88,.88])[face]
    dist,ind=kd.query(hpos,k=6,distance_upper_bound=9.0); light=np.zeros(N)
    for k in range(6):
        d=dist[:,k]; ok=np.isfinite(d); c=np.zeros(N); c[ok]=em_w[ind[ok,k]]*np.clip(1-d[ok]/9.0,0,1)**2; light+=c
    light=np.clip(light,0,1.1)
    base=col*fs[:,None]*(0.62+0.9*light[:,None]); base*=(0.6+0.5*tint[None,:]*(0.5+0.5*light[:,None]))
    fogc=np.array(fogc,float); fog=1-np.exp(-(np.where(hit,hd,200.)/46.0)**1.5); base=base*(1-fog[:,None])+fogc*fog[:,None]*0.9
    yd=D[:,1]; g=np.clip(yd,0,1); sky=np.tile(fogc*0.9,(N,1))*(1-g[:,None]**0.6)+np.array([2,6,16.])*(g[:,None]**0.6)
    az=np.arctan2(D[:,0],D[:,2]); nb=(np.sin(az*3+yd*9)*.5+.5)*(np.sin(az*5-yd*6+1.3)*.5+.5)*np.clip(yd*2.2,0,1)
    sky+=np.outer(nb**2*.9,neb1)*.5+np.outer((np.sin(az*2.2+yd*4)*.5+.5)**4*np.clip(yd*1.5,0,1),neb2)*.45
    stars=np.random.RandomState(1).rand(N)<.0016; sky[stars&(yd>.05)]+=[200,230,255]
    fin=np.where(hit[:,None],base,sky); pa2=np.clip(pa,0,.8)[:,None]; fin=fin*(1-pa2)+pc
    im=Image.fromarray(np.clip(fin,0,255).reshape(RH,RW,3).astype(np.uint8)).resize((1280,720),Image.NEAREST)
    arr=np.array(im).astype(np.float32); bl=Image.fromarray(np.clip(arr-120,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
    arr=np.clip(arr+np.array(bl).astype(np.float32)*1.1,0,255); yy,xx=np.mgrid[0:720,0:1280]; r=np.sqrt(((xx-640)/760)**2+((yy-360)/460)**2)
    arr*=(1-0.55*np.clip(r-0.35,0,1)**1.6)[...,None]; Image.fromarray(arr.astype(np.uint8)).save(out)
def cam_at(x,z,dy=2.8): return (x,h[int(x),int(z)]+dy,z)
def top_of(blk,bio):
    pts=[p for p in np.argwhere(W==blk) if biome[p[0],p[2]]==bio and 25<p[0]<SX-25 and 20<p[2]<SZ-6]
    return max(pts,key=lambda p:p[1]) if pts else np.array([75,50,100])
rb=top_of(BONE,2); cr=top_of(CRYS,3)
shots={
 "1":dict(cam=(px+4.5,h[px+4,pz-10]+2.6,pz-10.0),look=(px+.5,by+3,pz),fog=(14,70,96),tint=np.array([.55,1,1.1]),n1=[40,190,235],n2=[130,70,230]),
 "2":dict(cam=cam_at(85,22),look=(95,38,52),fog=(46,26,100),tint=np.array([.9,.7,1.2]),n1=[150,90,255],n2=[60,140,235]),
 "3":dict(cam=(rb[0]-4,h[int(rb[0])-4,int(rb[2])-15]+3.2,rb[2]-15.0),look=(rb[0],rb[1]-3,rb[2]),fog=(8,40,60),tint=np.array([.5,.9,1.05]),n1=[20,120,170],n2=[90,50,200]),
 "4":dict(cam=(cr[0]+2,h[int(cr[0])+2,int(cr[2])-17]+3.2,cr[2]-17.0),look=(cr[0],cr[1]-2,cr[2]),fog=(20,80,160),tint=np.array([.55,1,1.2]),n1=[60,170,255],n2=[160,100,255]),
}
for k in sys.argv[1:] or shots:
    s=shots[k]; render(s["cam"],s["look"],s["fog"],s["tint"],s["n1"],s["n2"],f"/home/claude/prev_{k}.png"); print("shot",k)
