import os, json
MOD="warden_dimension"; ROOT="/home/claude/warden_dimension/src/main/resources"; D=f"{ROOT}/data/{MOD}"
def wj(p,o):
    os.makedirs(os.path.dirname(p),exist_ok=True); open(p,"w").write(json.dumps(o,indent=2))
B=lambda n,**p:({"Name":f"{MOD}:{n}","Properties":p} if p else {"Name":f"{MOD}:{n}"})
V=lambda n:{"Name":f"minecraft:{n}"}

# --- terreno mas dramático + superficie con parches
p=f"{D}/worldgen/noise_settings/warden_dimension.json"; ns=json.load(open(p))
d=ns["noise_router"]["final_density"]["argument"]
d["argument2"]["argument1"]["argument1"]=0.78
d["argument2"]["argument2"]["argument2"]["argument1"]=0.17
def blk(s): return {"type":"minecraft:block","result_state":s}
def floor(off=0,add=False,sec=0): return {"type":"minecraft:stone_depth","offset":off,"surface_type":"floor","add_surface_depth":add,"secondary_depth_range":sec}
def patch(lo,hi,state): return {"type":"minecraft:condition","if_true":{"type":"minecraft:noise_threshold","noise":"minecraft:surface","min_threshold":lo,"max_threshold":hi},"then_run":blk(state)}
def biome(b,top,under,patches):
    seq=[{"type":"minecraft:condition","if_true":floor(),"then_run":{"type":"minecraft:sequence","sequence":patches+[blk(top)]}},
         {"type":"minecraft:condition","if_true":floor(0,True,3),"then_run":blk(under)}]
    return {"type":"minecraft:condition","if_true":{"type":"minecraft:biome","biome_is":[f"{MOD}:{b}"]},"then_run":{"type":"minecraft:sequence","sequence":seq}}
DS={"Name":"minecraft:deepslate","Properties":{"axis":"y"}}
ns["surface_rule"]={"type":"minecraft:sequence","sequence":[
 {"type":"minecraft:condition","if_true":{"type":"minecraft:vertical_gradient","random_name":"minecraft:bedrock_floor","true_at_and_below":{"above_bottom":0},"false_at_and_above":{"above_bottom":5}},"then_run":blk(V("bedrock"))},
 biome("resonant_forest",B("echo_moss_block"),B("sculk_stone"),[patch(0.45,1.0,V("sculk")),patch(-1.0,-0.5,B("sculk_stone"))]),
 biome("twilight_marsh",B("twilight_sculk"),B("sculk_stone"),[patch(0.4,1.0,B("echo_moss_block")),patch(-1.0,-0.55,V("sculk"))]),
 biome("abyssal_barrens",V("sculk"),DS,[patch(0.3,1.0,DS),patch(-1.0,-0.45,B("sculk_stone"))]),
 biome("crystal_fields",B("sculk_bricks"),B("sculk_stone"),[patch(0.4,1.0,B("echo_moss_block")),patch(-1.0,-0.5,B("glow_crystal_block"))]),
 blk(DS)]}
wj(p,ns)

# --- features
for n in ("resonant_tree_big","resonant_tree_small"):  # ya no se usan los arboles tipo vanilla
    for k in ("configured_feature","placed_feature"):
        f=f"{D}/worldgen/{k}/{n}.json"
        if os.path.exists(f): os.remove(f)
for n in ("marsh_tree",):
    f=f"{D}/worldgen/placed_feature/{n}.json"
    if os.path.exists(f): os.remove(f)
for n,t in (("spire_tree","spire_tree"),("dusk_weeper_tree","dusk_weeper_tree"),("rib_tree","rib_tree"),("crystal_cluster","crystal_cluster")):
    wj(f"{D}/worldgen/configured_feature/{n}.json",{"type":f"{MOD}:{t}","config":{}})
wj(f"{D}/worldgen/configured_feature/sculk_boulder.json",{"type":"minecraft:forest_rock","config":{"state":B("sculk_stone")}})
def disk(n,top,target):
    wj(f"{D}/worldgen/configured_feature/{n}.json",{"type":"minecraft:disk","config":{
      "state_provider":{"fallback":{"type":"minecraft:simple_state_provider","state":top},"rules":[]},
      "target":{"type":"minecraft:matching_blocks","blocks":target},
      "radius":{"type":"minecraft:uniform","value":{"min_inclusive":2,"max_inclusive":5}},"half_height":1}})
disk("twilight_disk",B("twilight_sculk"),[f"{MOD}:echo_moss_block"])
disk("moss_disk",B("echo_moss_block"),[f"{MOD}:twilight_sculk",f"{MOD}:sculk_bricks"])
disk("sculk_disk",V("sculk"),[f"{MOD}:echo_moss_block","minecraft:deepslate"])
surf=[{"type":"minecraft:in_square"},{"type":"minecraft:heightmap","heightmap":"WORLD_SURFACE_WG"},{"type":"minecraft:biome"}]
def placed(n,f,mods): wj(f"{D}/worldgen/placed_feature/{n}.json",{"feature":f"{MOD}:{f}","placement":mods})
cnt=lambda a,b:{"type":"minecraft:count","count":{"type":"minecraft:uniform","min_inclusive":a,"max_inclusive":b}}
placed("spire_tree","spire_tree",[cnt(2,3)]+surf)
placed("dusk_weeper_tree","dusk_weeper_tree",[cnt(2,4)]+surf)
placed("rib_tree","rib_tree",[cnt(1,2),{"type":"minecraft:rarity_filter","chance":2}]+surf)
placed("crystal_cluster","crystal_cluster",[cnt(2,4)]+surf)
placed("sculk_boulder","sculk_boulder",[{"type":"minecraft:rarity_filter","chance":3}]+surf)
placed("twilight_disk","twilight_disk",[cnt(1,2)]+surf)
placed("moss_disk","moss_disk",[cnt(1,2)]+surf)
placed("sculk_disk","sculk_disk",[cnt(2,3)]+surf)
placed("glowcap_patch","glowcap_patch",[cnt(3,5)]+surf)

# --- biomas
def mk(name,sky,fog,water,foliage,grass,particle,feats,add_snd):
    f=[[] for _ in range(11)]
    for i,l in feats.items(): f[i]=l
    wj(f"{D}/worldgen/biome/{name}.json",{"has_precipitation":False,"temperature":0.5,"downfall":0.0,"effects":{
      "sky_color":sky,"fog_color":fog,"water_color":water,"water_fog_color":fog,"foliage_color":foliage,"grass_color":grass,
      "particle":{"probability":0.025,"options":{"type":particle}},
      "mood_sound":{"sound":"minecraft:ambient.soul_sand_valley.mood","tick_delay":6000,"block_search_extent":8,"offset":2.0},
      "additions_sound":{"sound":add_snd,"tick_chance":0.004},
      "ambient_sound":"minecraft:ambient.soul_sand_valley.loop"},
      "carvers":{},"features":f,"spawners":{k:[] for k in ["monster","creature","ambient","axolotls","underground_water_creature","water_creature","water_ambient","misc"]},"spawn_costs":{}})
mk("resonant_forest",0x0A3A52,0x0E5C78,0x1BB5D6,0x1AD3E8,0x18B9D0,"minecraft:sculk_soul",
   {2:[f"{MOD}:sculk_boulder",f"{MOD}:twilight_disk"],9:[f"{MOD}:spire_tree",f"{MOD}:glowcap_patch"]},"minecraft:block.sculk_sensor.clicking")
mk("twilight_marsh",0x1E1048,0x3A1E78,0x7E4FE0,0x9A6CFF,0x7A4ED0,"minecraft:warped_spore",
   {2:[f"{MOD}:moss_disk"],9:[f"{MOD}:dusk_weeper_tree",f"{MOD}:glowcap_patch"]},"minecraft:block.sculk_catalyst.bloom")
mk("abyssal_barrens",0x04121E,0x07263A,0x0F6A8A,0x0F8CA0,0x0F6E86,"minecraft:sculk_soul",
   {2:[f"{MOD}:sculk_boulder",f"{MOD}:sculk_disk"],9:["minecraft:sculk_patch_deep_dark",f"{MOD}:rib_tree",f"{MOD}:glowcap_patch"]},"minecraft:block.sculk_shrieker.shriek")
mk("crystal_fields",0x0C2A5A,0x1458A0,0x3FD2FF,0x6FE8FF,0x4ADCF5,"minecraft:end_rod",
   {2:[f"{MOD}:moss_disk"],9:[f"{MOD}:crystal_cluster",f"{MOD}:glowcap_patch"]},"minecraft:block.amethyst_block.chime")
print("data2 ok")
