import os, json
MOD="warden_dimension"; ROOT="/home/claude/warden_dimension/src/main/resources"; D=f"{ROOT}/data/{MOD}"
def wj(p,o):
    os.makedirs(os.path.dirname(p),exist_ok=True); open(p,"w").write(json.dumps(o,indent=2))
B=lambda n,**p:({"Name":f"{MOD}:{n}","Properties":p} if p else {"Name":f"{MOD}:{n}"})

wj(f"{D}/dimension_type/warden_dimension.json", {
 "ultrawarm":False,"natural":False,"coordinate_scale":1.0,"has_skylight":True,"has_ceiling":False,"ambient_light":0.1,
 "fixed_time":18000,"piglin_safe":False,"bed_works":True,"respawn_anchor_works":False,"has_raids":False,"logical_height":384,
 "min_y":-64,"height":384,"infiniburn":"#minecraft:infiniburn_overworld","effects":"minecraft:overworld",
 "monster_spawn_light_level":{"type":"minecraft:uniform","value":{"min_inclusive":0,"max_inclusive":7}},"monster_spawn_block_light_limit":0})

def n(name,xz): return {"type":"minecraft:noise","noise":f"minecraft:{name}","xz_scale":xz,"y_scale":0.0}
def mul(a,b): return {"type":"minecraft:mul","argument1":a,"argument2":b}
def add(a,b): return {"type":"minecraft:add","argument1":a,"argument2":b}
density = {"type":"minecraft:interpolated","argument":add(
  {"type":"minecraft:y_clamped_gradient","from_y":-64,"to_y":256,"from_value":1.5,"to_value":-1.5},
  add(mul(0.6, n("erosion",2.0)), add(mul(0.1, n("surface",1.0)), mul(0.1,{"type":"minecraft:noise","noise":"minecraft:jagged","xz_scale":1.0,"y_scale":0.4}))))}

def biome_is(b): return {"type":"minecraft:biome","biome_is":[f"{MOD}:{b}"]}
def top(b,top_block,under):
    return {"type":"minecraft:condition","if_true":biome_is(b),"then_run":{"type":"minecraft:sequence","sequence":[
      {"type":"minecraft:condition","if_true":{"type":"minecraft:stone_depth","offset":0,"surface_type":"floor","add_surface_depth":False,"secondary_depth_range":0},"then_run":{"type":"minecraft:block","result_state":top_block}},
      {"type":"minecraft:condition","if_true":{"type":"minecraft:stone_depth","offset":0,"surface_type":"floor","add_surface_depth":True,"secondary_depth_range":3},"then_run":{"type":"minecraft:block","result_state":under}}]}}
surface={"type":"minecraft:sequence","sequence":[
 {"type":"minecraft:condition","if_true":{"type":"minecraft:vertical_gradient","random_name":"minecraft:bedrock_floor","true_at_and_below":{"above_bottom":0},"false_at_and_above":{"above_bottom":5}},"then_run":{"type":"minecraft:block","result_state":{"Name":"minecraft:bedrock"}}},
 top("resonant_forest",B("echo_moss_block"),B("sculk_stone")),
 top("twilight_marsh",B("twilight_sculk"),B("sculk_stone")),
 top("abyssal_barrens",{"Name":"minecraft:sculk"},{"Name":"minecraft:deepslate","Properties":{"axis":"y"}}),
 top("crystal_fields",B("sculk_bricks"),B("sculk_stone")),
 {"type":"minecraft:block","result_state":{"Name":"minecraft:deepslate","Properties":{"axis":"y"}}}]}

wj(f"{D}/worldgen/noise_settings/warden_dimension.json", {
 "sea_level":-64,"disable_mob_generation":True,"aquifers_enabled":False,"ore_veins_enabled":False,"legacy_random_source":False,
 "default_block":{"Name":"minecraft:deepslate","Properties":{"axis":"y"}},"default_fluid":{"Name":"minecraft:air"},
 "noise":{"min_y":-64,"height":384,"size_horizontal":1,"size_vertical":2},
 "noise_router":{"barrier":0.0,"fluid_level_floodedness":0.0,"fluid_level_spread":0.0,"lava":0.0,
   "temperature":n("temperature",0.4),"vegetation":n("vegetation",0.4),"continents":n("continentalness",0.3),"erosion":n("erosion",0.3),
   "depth":0.0,"ridges":n("ridge",0.3),"initial_density_without_jaggedness":0.0,"final_density":density,"vein_toggle":0.0,"vein_ridged":0.0,"vein_gap":0.0},
 "spawn_target":[],"surface_rule":surface})

def pt(b,t,h): return {"biome":f"{MOD}:{b}","parameters":{"temperature":t,"humidity":h,"continentalness":0.0,"erosion":0.0,"weirdness":0.0,"depth":0.0,"offset":0.0}}
wj(f"{D}/dimension/warden_dimension.json", {"type":f"{MOD}:warden_dimension","generator":{"type":"minecraft:noise","settings":f"{MOD}:warden_dimension",
  "biome_source":{"type":"minecraft:multi_noise","biomes":[pt("resonant_forest",0.0,0.5),pt("twilight_marsh",0.6,-0.2),pt("abyssal_barrens",-0.6,-0.4),pt("crystal_fields",0.5,0.8)]}}})

# ---------- features ----------
def tree(name, trunk_h, fancy):
    cfg={"ignore_vines":True,"force_dirt":False,"minimum_size":{"type":"minecraft:two_layers_feature_size","limit":1,"lower_size":0,"upper_size":1},
     "dirt_provider":{"type":"minecraft:simple_state_provider","state":B("sculk_stone")},
     "trunk_provider":{"type":"minecraft:simple_state_provider","state":B("resonant_log",axis="y")},
     "foliage_provider":{"type":"minecraft:simple_state_provider","state":B("resonant_leaves")},
     "trunk_placer":{"type":"minecraft:fancy_trunk_placer","base_height":trunk_h,"height_rand_a":8,"height_rand_b":0} if fancy else {"type":"minecraft:straight_trunk_placer","base_height":trunk_h,"height_rand_a":2,"height_rand_b":1},
     "foliage_placer":{"type":"minecraft:fancy_foliage_placer","radius":4,"offset":4,"height":4} if fancy else {"type":"minecraft:blob_foliage_placer","radius":3,"offset":0,"height":3},
     "decorators":[{"type":"minecraft:attached_to_leaves","probability":0.25,"exclusion_radius_xz":1,"exclusion_radius_y":0,"required_empty_blocks":1,
        "block_provider":{"type":"minecraft:simple_state_provider","state":B("glow_crystal_block")},"directions":["down"]}]}
    wj(f"{D}/worldgen/configured_feature/{name}.json",{"type":"minecraft:tree","config":cfg})
tree("resonant_tree_big",7,True); tree("resonant_tree_small",4,False)

def patch(name, entries, floor, tries=96):
    wj(f"{D}/worldgen/configured_feature/{name}.json",{"type":"minecraft:random_patch","config":{"tries":tries,"xz_spread":7,"y_spread":3,"feature":{
      "feature":{"type":"minecraft:simple_block","config":{"to_place":{"type":"minecraft:weighted_state_provider","entries":entries}}},
      "placement":[{"type":"minecraft:block_predicate_filter","predicate":{"type":"minecraft:all_of","predicates":[
         {"type":"minecraft:matching_blocks","blocks":"minecraft:air"},
         {"type":"minecraft:matching_blocks","offset":[0,-1,0],"blocks":floor}]}}]}}})
patch("glowcap_patch",[{"weight":4,"data":B("glowcap")},{"weight":1,"data":{"Name":"minecraft:moss_carpet"}}],[f"{MOD}:echo_moss_block",f"{MOD}:twilight_sculk"])

wj(f"{D}/worldgen/configured_feature/crystal_spike.json",{"type":"minecraft:block_column","config":{"direction":"up","allowed_placement":{"type":"minecraft:matching_blocks","blocks":"minecraft:air"},"prioritize_tip":False,
  "layers":[{"height":{"type":"minecraft:uniform","min_inclusive":3,"max_inclusive":9},"provider":{"type":"minecraft:simple_state_provider","state":B("glow_crystal_block")}}]}})

def placed(name, feat, mods): wj(f"{D}/worldgen/placed_feature/{name}.json",{"feature":f"{MOD}:{feat}","placement":mods})
surf=[{"type":"minecraft:in_square"},{"type":"minecraft:heightmap","heightmap":"WORLD_SURFACE_WG"},{"type":"minecraft:biome"}]
placed("resonant_tree_big","resonant_tree_big",[{"type":"minecraft:count","count":{"type":"minecraft:uniform","min_inclusive":2,"max_inclusive":4}}]+surf)
placed("resonant_tree_small","resonant_tree_small",[{"type":"minecraft:count","count":{"type":"minecraft:uniform","min_inclusive":3,"max_inclusive":6}}]+surf)
placed("glowcap_patch","glowcap_patch",[{"type":"minecraft:count","count":3}]+surf)
placed("crystal_spike","crystal_spike",[{"type":"minecraft:count","count":{"type":"minecraft:uniform","min_inclusive":1,"max_inclusive":3}}]+surf)
placed("marsh_tree","resonant_tree_small",[{"type":"minecraft:count","count":1}]+surf)

# ---------- biomas ----------
def biome(name, sky, fog, water, foliage, grass, particle, features9, extra=None):
    feats=[[] for _ in range(11)]; feats[9]=features9
    if extra: feats[extra[0]]=extra[1]
    wj(f"{D}/worldgen/biome/{name}.json",{"has_precipitation":False,"temperature":0.5,"downfall":0.0,
      "effects":{"sky_color":sky,"fog_color":fog,"water_color":water,"water_fog_color":fog,"foliage_color":foliage,"grass_color":grass,
        "particle":{"probability":0.02,"options":{"type":particle}},
        "mood_sound":{"sound":"minecraft:ambient.soul_sand_valley.mood","tick_delay":6000,"block_search_extent":8,"offset":2.0},
        "ambient_sound":"minecraft:ambient.soul_sand_valley.loop"},
      "carvers":{},"features":feats,"spawners":{k:[] for k in ["monster","creature","ambient","axolotls","underground_water_creature","water_creature","water_ambient","misc"]},"spawn_costs":{}})
# colores (decimal): cian/azul sculk de la referencia
biome("resonant_forest", 0x0A3A52, 0x0E5C78, 0x1BB5D6, 0x1AD3E8, 0x18B9D0, "minecraft:sculk_soul",
      [f"{MOD}:resonant_tree_big",f"{MOD}:resonant_tree_small",f"{MOD}:glowcap_patch"])
biome("twilight_marsh", 0x1E1048, 0x3A1E78, 0x7E4FE0, 0x9A6CFF, 0x7A4ED0, "minecraft:warped_spore",
      [f"{MOD}:marsh_tree",f"{MOD}:glowcap_patch"])
biome("abyssal_barrens", 0x04121E, 0x07263A, 0x0F6A8A, 0x0F8CA0, 0x0F6E86, "minecraft:sculk_charge_pop" if False else "minecraft:sculk_soul",
      ["minecraft:sculk_patch_deep_dark",f"{MOD}:glowcap_patch"])
biome("crystal_fields", 0x0C2A5A, 0x1458A0, 0x3FD2FF, 0x6FE8FF, 0x4ADCF5, "minecraft:end_rod",
      [f"{MOD}:crystal_spike",f"{MOD}:glowcap_patch"])

# ---------- metadatos ----------
wj(f"{ROOT}/pack.mcmeta",{"pack":{"description":"Dimensión Warden","pack_format":15}})
os.makedirs(f"{ROOT}/META-INF",exist_ok=True)
open(f"{ROOT}/META-INF/mods.toml","w").write('''modLoader="javafml"
loaderVersion="[47,)"
license="All Rights Reserved"

[[mods]]
modId="warden_dimension"
version="1.0.0"
displayName="Dimensión Warden"
description=\'\'\'Dimensión del Warden con portal propio (marco del Warden + fragmento de eco), 4 biomas y bloques nuevos de color sculk.\'\'\'

[[dependencies.warden_dimension]]
modId="forge"
mandatory=true
versionRange="[47,)"
ordering="NONE"
side="BOTH"

[[dependencies.warden_dimension]]
modId="minecraft"
mandatory=true
versionRange="[1.20.1,1.21)"
ordering="NONE"
side="BOTH"
''')
print("data ok")
