import os, json
MOD="warden_dimension"; ROOT="/home/claude/warden_dimension/src/main/resources"; A=f"{ROOT}/assets/{MOD}"; D=f"{ROOT}/data/{MOD}"
def wj(p,o):
    os.makedirs(os.path.dirname(p),exist_ok=True); open(p,"w").write(json.dumps(o,indent=2))
m=lambda n:f"{MOD}:block/{n}"
# hojas crepusculares
wj(f"{A}/models/block/twilight_leaves.json",{"parent":"minecraft:block/leaves","textures":{"all":m("twilight_leaves")},"render_type":"minecraft:cutout_mipped"})
wj(f"{A}/blockstates/twilight_leaves.json",{"variants":{"":{"model":m("twilight_leaves")}}}); wj(f"{A}/models/item/twilight_leaves.json",{"parent":m("twilight_leaves")})
# hueso del warden
wj(f"{A}/models/block/warden_bone.json",{"parent":"minecraft:block/cube_column","textures":{"end":m("warden_bone_top"),"side":m("warden_bone")}})
wj(f"{A}/blockstates/warden_bone.json",{"variants":{"axis=y":{"model":m("warden_bone")},"axis=z":{"model":m("warden_bone"),"x":90},"axis=x":{"model":m("warden_bone"),"x":90,"y":90}}})
wj(f"{A}/models/item/warden_bone.json",{"parent":m("warden_bone")})
# hebra colgante
wj(f"{A}/models/block/dangling_strand.json",{"parent":"minecraft:block/cross","textures":{"cross":m("dangling_strand")},"render_type":"minecraft:cutout"})
wj(f"{A}/blockstates/dangling_strand.json",{"variants":{"":{"model":m("dangling_strand")}}})
wj(f"{A}/models/item/dangling_strand.json",{"parent":"minecraft:item/generated","textures":{"layer0":m("dangling_strand")}})
# lang
for f,extra in (("es_es",{"twilight_leaves":"Hojas Crepusculares","warden_bone":"Hueso del Warden","dangling_strand":"Hebra Colgante"}),
                ("es_mx",{"twilight_leaves":"Hojas Crepusculares","warden_bone":"Hueso del Warden","dangling_strand":"Hebra Colgante"}),
                ("en_us",{"twilight_leaves":"Twilight Leaves","warden_bone":"Warden Bone","dangling_strand":"Dangling Strand"})):
    p=f"{A}/lang/{f}.json"; d=json.load(open(p))
    for k,v in extra.items(): d[f"block.{MOD}.{k}"]=v
    wj(p,d)
# loot
for n in ["warden_bone","dangling_strand"]:
    wj(f"{D}/loot_tables/blocks/{n}.json",{"type":"minecraft:block","pools":[{"rolls":1,"entries":[{"type":"minecraft:item","name":f"{MOD}:{n}"}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
wj(f"{D}/loot_tables/blocks/twilight_leaves.json",{"type":"minecraft:block","pools":[
 {"rolls":1,"entries":[{"type":"minecraft:item","name":f"{MOD}:twilight_leaves"}],"conditions":[{"condition":"minecraft:match_tool","predicate":{"items":["minecraft:shears"]}}]},
 {"rolls":1,"entries":[{"type":"minecraft:item","name":"minecraft:stick"}],"conditions":[{"condition":"minecraft:random_chance","chance":0.2}]}]})
# tags (reescribir con los nuevos)
def tag(p,v): wj(f"{ROOT}/data/{p}.json",{"replace":False,"values":v})
tag("minecraft/tags/blocks/mineable/hoe",[f"{MOD}:resonant_leaves",f"{MOD}:twilight_leaves"])
tag("minecraft/tags/blocks/mineable/axe",[f"{MOD}:resonant_log",f"{MOD}:warden_bone"])
tag("minecraft/tags/blocks/logs",[f"{MOD}:resonant_log",f"{MOD}:warden_bone"]); tag("minecraft/tags/items/logs",[f"{MOD}:resonant_log",f"{MOD}:warden_bone"])
tag("minecraft/tags/blocks/leaves",[f"{MOD}:resonant_leaves",f"{MOD}:twilight_leaves"]); tag("minecraft/tags/items/leaves",[f"{MOD}:resonant_leaves",f"{MOD}:twilight_leaves"])
print("assets2 ok")
