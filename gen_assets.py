import os, json, random
from PIL import Image
import numpy as np

MOD = "warden_dimension"
ROOT = "/home/claude/warden_dimension/src/main/resources"
TEX = f"{ROOT}/assets/{MOD}/textures/block"
os.makedirs(TEX, exist_ok=True)

def clamp(v): return max(0, min(255, int(v)))
def shade(c, f): return tuple(clamp(x*f) for x in c)
def noise_tex(base, var, seed, specks=None, spk_p=0.0):
    r = random.Random(seed)
    im = Image.new("RGBA", (16,16))
    for y in range(16):
        for x in range(16):
            f = 1 + r.uniform(-var, var)
            c = shade(base, f)
            if specks and r.random() < spk_p: c = r.choice(specks)
            im.putpixel((x,y), c+(255,))
    return im

# paleta sculk azul/cian (referencia de la imagen)
DEEP   = (14, 30, 44)
STONE  = (22, 48, 66)
CYAN   = (26, 190, 214)
CYAN_L = (120, 240, 255)
TEAL   = (16, 110, 130)
VIOLET = (96, 56, 170)
VIOLET_L = (170, 120, 255)

tex = {}
# sculk_stone
t = noise_tex(STONE, 0.18, 1, [DEEP, (30,64,86), (18,40,56)], 0.25); tex["sculk_stone"] = t
# echo_moss: top, side, bottom
tex["echo_moss_top"] = noise_tex((20,150,170), 0.22, 2, [CYAN, TEAL, CYAN_L], 0.18)
side = tex["sculk_stone"].copy(); r = random.Random(3)
for x in range(16):
    h = 3 + r.randint(0,3)
    for y in range(h):
        side.putpixel((x,y), shade((20,150,170), 1+r.uniform(-.2,.2))+(255,))
tex["echo_moss_side"] = side
# resonant log
top = Image.new("RGBA",(16,16)); sd = Image.new("RGBA",(16,16)); r = random.Random(4)
for y in range(16):
    for x in range(16):
        d = max(abs(x-7.5), abs(y-7.5))
        ring = (int(d) % 3 == 0)
        top.putpixel((x,y), (shade((24,120,140),1.2) if ring else shade((12,44,60),1+r.uniform(-.15,.15)))+(255,) if d<7 else shade((10,26,38),1)+(255,))
        base = (12,34,48) if x%4 else (8,22,32)
        c = shade(base,1+r.uniform(-.2,.2))
        if r.random()<0.06: c = CYAN
        sd.putpixel((x,y), c+(255,))
tex["resonant_log_top"]=top; tex["resonant_log"]=sd
# leaves (translucent holes)
im = Image.new("RGBA",(16,16)); r = random.Random(5)
for y in range(16):
    for x in range(16):
        if r.random()<0.18: im.putpixel((x,y),(0,0,0,0)); continue
        c = r.choice([CYAN,(20,160,190),TEAL,CYAN_L,(30,200,225)]) if r.random()<0.9 else VIOLET_L
        im.putpixel((x,y), shade(c,1+r.uniform(-.1,.1))+(255,))
tex["resonant_leaves"]=im
# glow crystal
im = Image.new("RGBA",(16,16)); r = random.Random(6)
for y in range(16):
    for x in range(16):
        g = 0.65+0.35*abs(((x+y)%8)-4)/4
        c = shade(CYAN_L if ((x*3+y*5)%11<3) else CYAN, g*(1+r.uniform(-.06,.06)))
        im.putpixel((x,y), c+(255,))
for i in range(16):
    for p in ((i,0),(i,15),(0,i),(15,i)): im.putpixel(p, shade(TEAL,0.9)+(255,))
tex["glow_crystal_block"]=im
# sculk bricks
im = Image.new("RGBA",(16,16)); r = random.Random(7)
for y in range(16):
    for x in range(16):
        mortar = (y%8==0) or ((x+(4 if (y//8)%2 else 0))%8==0)
        c = shade((8,20,30),1) if mortar else shade((28,62,84),1+r.uniform(-.12,.12))
        if not mortar and r.random()<0.05: c = TEAL
        im.putpixel((x,y), c+(255,))
tex["sculk_bricks"]=im
# warden frame (marco ancestral)
im = Image.new("RGBA",(16,16)); r = random.Random(8)
for y in range(16):
    for x in range(16):
        edge = x in (0,15) or y in (0,15)
        c = shade((10,22,34),1+r.uniform(-.1,.1)) if not edge else shade((30,70,96),1+r.uniform(-.1,.1))
        im.putpixel((x,y), c+(255,))
glyph = [(7,3),(8,3),(6,4),(9,4),(5,5),(10,5),(5,6),(10,6),(7,7),(8,7),(7,8),(8,8),(5,9),(10,9),(5,10),(10,10),(6,11),(9,11),(7,12),(8,12)]
for p in glyph: im.putpixel(p, CYAN_L+(255,))
tex["warden_frame"]=im
# portal (animado, 2 frames horizontales no; usamos tira vertical 16x32)
pt = Image.new("RGBA",(16,64)); r = np.random.RandomState(9)
for f in range(4):
    for y in range(16):
        for x in range(16):
            v = 0.5+0.5*np.sin((x*0.9+y*0.6)+f*1.57)+0.25*np.sin(y*1.3-f*1.57)
            c = np.array(CYAN)*(0.5+0.5*v)+np.array(VIOLET)*(0.4*(1-v))
            c = np.clip(c,0,255).astype(int)
            pt.putpixel((x,f*16+y),(int(c[0]),int(c[1]),int(c[2]),170))
tex["warden_portal"]=pt
# twilight sculk (violeta)
tex["twilight_sculk_top"]=noise_tex((70,40,130),0.22,10,[VIOLET,VIOLET_L,(40,24,86)],0.18)
sd = tex["sculk_stone"].copy(); r=random.Random(11)
for x in range(16):
    for y in range(3+r.randint(0,3)): sd.putpixel((x,y), shade((70,40,130),1+r.uniform(-.2,.2))+(255,))
tex["twilight_sculk_side"]=sd
# glowcap (planta cruzada)
im = Image.new("RGBA",(16,16),(0,0,0,0)); r = random.Random(12)
for y in range(6,16):
    for x in (7,8): im.putpixel((x,y), shade(TEAL,1+r.uniform(-.1,.1))+(255,))
for (cx,cy,rad) in ((8,5,4),(3,9,2),(13,10,2)):
    for y in range(16):
        for x in range(16):
            if (x-cx)**2+(y-cy)**2 <= rad*rad and y<=cy+1:
                im.putpixel((x,y), shade(CYAN_L if (x+y)%3==0 else CYAN,1+r.uniform(-.08,.08))+(255,))
tex["glowcap"]=im

for k,v in tex.items(): v.save(f"{TEX}/{k}.png")
open(f"{TEX}/warden_portal.png.mcmeta","w").write(json.dumps({"animation":{"frametime":3,"interpolate":True}}))

def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path,"w").write(json.dumps(obj, indent=2))

A = f"{ROOT}/assets/{MOD}"
D = f"{ROOT}/data/{MOD}"
def m(n): return f"{MOD}:block/{n}"
def blockitem(n): wj(f"{A}/models/item/{n}.json", {"parent": m(n)})

# cubos simples
for n in ["sculk_stone","glow_crystal_block","sculk_bricks","warden_frame"]:
    wj(f"{A}/models/block/{n}.json", {"parent":"minecraft:block/cube_all","textures":{"all":m(n)}})
    wj(f"{A}/blockstates/{n}.json", {"variants":{"":{"model":m(n)}}}); blockitem(n)
for n,top,side in [("echo_moss_block","echo_moss_top","echo_moss_side"),("twilight_sculk","twilight_sculk_top","twilight_sculk_side")]:
    wj(f"{A}/models/block/{n}.json", {"parent":"minecraft:block/cube_bottom_top","textures":{"top":m(top),"side":m(side),"bottom":m("sculk_stone")}})
    wj(f"{A}/blockstates/{n}.json", {"variants":{"":{"model":m(n)}}}); blockitem(n)
# log
wj(f"{A}/models/block/resonant_log.json", {"parent":"minecraft:block/cube_column","textures":{"end":m("resonant_log_top"),"side":m("resonant_log")}})
wj(f"{A}/blockstates/resonant_log.json", {"variants":{"axis=y":{"model":m("resonant_log")},"axis=z":{"model":m("resonant_log"),"x":90},"axis=x":{"model":m("resonant_log"),"x":90,"y":90}}}); blockitem("resonant_log")
# hojas
wj(f"{A}/models/block/resonant_leaves.json", {"parent":"minecraft:block/leaves","textures":{"all":m("resonant_leaves")},"render_type":"minecraft:cutout_mipped"})
wj(f"{A}/blockstates/resonant_leaves.json", {"variants":{"":{"model":m("resonant_leaves")}}}); blockitem("resonant_leaves")
# glowcap
wj(f"{A}/models/block/glowcap.json", {"parent":"minecraft:block/cross","textures":{"cross":m("glowcap")},"render_type":"minecraft:cutout"})
wj(f"{A}/blockstates/glowcap.json", {"variants":{"":{"model":m("glowcap")}}})
wj(f"{A}/models/item/glowcap.json", {"parent":"minecraft:item/generated","textures":{"layer0":m("glowcap")}})
# portal
for ax,name in (("x","warden_portal_ns"),("z","warden_portal_ew")):
    pass
wj(f"{A}/models/block/warden_portal_x.json", {"textures":{"particle":m("warden_portal"),"portal":m("warden_portal")},"render_type":"minecraft:translucent",
    "elements":[{"from":[0,0,6],"to":[16,16,10],"faces":{"north":{"uv":[0,0,16,16],"texture":"#portal"},"south":{"uv":[0,0,16,16],"texture":"#portal"}}}]})
wj(f"{A}/models/block/warden_portal_z.json", {"textures":{"particle":m("warden_portal"),"portal":m("warden_portal")},"render_type":"minecraft:translucent",
    "elements":[{"from":[6,0,0],"to":[10,16,16],"faces":{"east":{"uv":[0,0,16,16],"texture":"#portal"},"west":{"uv":[0,0,16,16],"texture":"#portal"}}}]})
wj(f"{A}/blockstates/warden_portal.json", {"variants":{"axis=x":{"model":m("warden_portal_x")},"axis=z":{"model":m("warden_portal_z")}}})

# lang
names = {"sculk_stone":"Piedra Sculk","echo_moss_block":"Bloque de Musgo Eco","twilight_sculk":"Sculk Crepuscular","resonant_log":"Tronco Resonante",
 "resonant_leaves":"Hojas Resonantes","glow_crystal_block":"Bloque de Cristal Luminoso","sculk_bricks":"Ladrillos de Sculk","warden_frame":"Marco del Warden",
 "warden_portal":"Portal del Warden","glowcap":"Hongo Luminoso"}
lang = {f"block.{MOD}.{k}":v for k,v in names.items()}
lang[f"itemGroup.{MOD}"] = "Dimensión Warden"
wj(f"{A}/lang/es_es.json", lang); wj(f"{A}/lang/es_mx.json", lang)
en = {"sculk_stone":"Sculk Stone","echo_moss_block":"Echo Moss Block","twilight_sculk":"Twilight Sculk","resonant_log":"Resonant Log","resonant_leaves":"Resonant Leaves",
 "glow_crystal_block":"Glow Crystal Block","sculk_bricks":"Sculk Bricks","warden_frame":"Warden Frame","warden_portal":"Warden Portal","glowcap":"Glowcap"}
l2 = {f"block.{MOD}.{k}":v for k,v in en.items()}; l2[f"itemGroup.{MOD}"]="Warden Dimension"
wj(f"{A}/lang/en_us.json", l2)

# loot tables (todos se sueltan a sí mismos salvo portal)
for n in ["sculk_stone","echo_moss_block","twilight_sculk","resonant_log","glow_crystal_block","sculk_bricks","warden_frame","glowcap"]:
    wj(f"{D}/loot_tables/blocks/{n}.json", {"type":"minecraft:block","pools":[{"rolls":1,"entries":[{"type":"minecraft:item","name":f"{MOD}:{n}"}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
wj(f"{D}/loot_tables/blocks/resonant_leaves.json", {"type":"minecraft:block","pools":[
 {"rolls":1,"entries":[{"type":"minecraft:item","name":f"{MOD}:resonant_leaves"}],"conditions":[{"condition":"minecraft:match_tool","predicate":{"items":["minecraft:shears"]}}]},
 {"rolls":1,"entries":[{"type":"minecraft:item","name":"minecraft:stick"}],"conditions":[{"condition":"minecraft:random_chance","chance":0.2}]}]})

# tags
def tag(path, values): wj(f"{ROOT}/data/{path}.json", {"replace":False,"values":values})
tag("minecraft/tags/blocks/mineable/pickaxe",[f"{MOD}:{n}" for n in ["sculk_stone","echo_moss_block","twilight_sculk","glow_crystal_block","sculk_bricks","warden_frame"]])
tag("minecraft/tags/blocks/mineable/axe",[f"{MOD}:resonant_log"])
tag("minecraft/tags/blocks/mineable/hoe",[f"{MOD}:resonant_leaves"])
tag("minecraft/tags/blocks/logs",[f"{MOD}:resonant_log"]); tag("minecraft/tags/items/logs",[f"{MOD}:resonant_log"])
tag("minecraft/tags/blocks/leaves",[f"{MOD}:resonant_leaves"]); tag("minecraft/tags/items/leaves",[f"{MOD}:resonant_leaves"])
tag("minecraft/tags/blocks/needs_stone_tool",[f"{MOD}:sculk_stone",f"{MOD}:sculk_bricks",f"{MOD}:glow_crystal_block"])
tag("minecraft/tags/blocks/needs_diamond_tool",[f"{MOD}:warden_frame"])
tag("minecraft/tags/blocks/sculk_replaceable",[f"{MOD}:sculk_stone",f"{MOD}:echo_moss_block",f"{MOD}:twilight_sculk"])

# recetas
wj(f"{D}/recipes/sculk_stone.json", {"type":"minecraft:crafting_shapeless","ingredients":[{"item":"minecraft:deepslate"},{"item":"minecraft:deepslate"},{"item":"minecraft:deepslate"},{"item":"minecraft:deepslate"},{"item":"minecraft:sculk"}],"result":{"item":f"{MOD}:sculk_stone","count":4}})
wj(f"{D}/recipes/sculk_bricks.json", {"type":"minecraft:crafting_shaped","pattern":["SS","SS"],"key":{"S":{"item":f"{MOD}:sculk_stone"}},"result":{"item":f"{MOD}:sculk_bricks","count":4}})
wj(f"{D}/recipes/warden_frame.json", {"type":"minecraft:crafting_shaped","pattern":["BOB","BEB","BBB"],"key":{"B":{"item":f"{MOD}:sculk_bricks"},"O":{"item":"minecraft:crying_obsidian"},"E":{"item":"minecraft:echo_shard"}},"result":{"item":f"{MOD}:warden_frame","count":2}})
wj(f"{D}/recipes/glow_crystal_block.json", {"type":"minecraft:crafting_shaped","pattern":["AA","AA"],"key":{"A":{"item":"minecraft:amethyst_shard"}},"result":{"item":f"{MOD}:glow_crystal_block","count":1}})
print("assets ok", len(tex))
