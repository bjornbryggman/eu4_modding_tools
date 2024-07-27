every province with a custom image must be assigned its own category in the terrain.txt. important to remember to remove a province from its old category if assigned to a new one, also maintain any relevant tags (colors, etc)

we need to generate terrain picture with the same name as the terrain type, and add that to the localization.


it also needs to be added to combat terrain gfx.

also needs to fix missions rewards(e.g.:

#Mission tree rewards
estate_burghers_hydraulic_rights = {
	icon = privilege_dev_cost_desert
	max_absolutism = -10
	conditional_modifier = { trigger = { has_absolutism_reduction_for_estate_privileges = yes } modifier = { max_absolutism = 2 } }
	influence = 0.05
	loyalty = 0.05
	is_valid = {
		has_unlocked_estate_privilege = { estate_privilege = estate_burghers_hydraulic_rights }
	}
	can_select = {
		any_owned_province = {
			OR = {
				has_terrain = desert
					has_terrain = karakorum_j
					has_terrain = urban_palmyra
					has_terrain = urban_suwayda
					has_terrain = 26yumen
					has_terrain = 28dunhuang
					has_terrain = Tsaidam
				has_terrain = coastal_desert
					has_terrain = urban_suakin
					has_terrain = urban_tripolitania
					has_terrain = urban_gaza
					has_terrain = urban_muscat
)

basically, any custom province needs to be grouped into a group (e.g. "mountains", "steppes", and regex applied to gfx files that reference those terrain types. "has_terrain = "). also, pay attention to the "						OR = {".

lastly, localization needs to be added.

from the wiki:
The terrain.txt has multiple functions. It defines what terrain categories there are (i.e. grasslands, forest, etc.) and associates these categories with indexed colors found in terrain.bmp. It does the latter for the trees.bmp as well.

There is a category for every terrain type in game, as well as various special-case categories, such as pti and ocean. You can add and remove categories as you wish, although you must make sure all references else where to removed terrains are cleaned up, otherwise you may run into crashes.

The format for a category is as follows:

name = {
    color = { <rgb> }           # Defines the RGB color to use for showing the terrain in the simple terrain mapmode (optional)
    
    sound_type = <type>         # Defines the ambient sound definition to use for the terrain. Found in sound/all_sounds.asset
    
    is_water = <yes>            # Defines whether this category is treated as sea
    inland_sea = <yes>          # Defines whether this category is treated as an inland sea
    
    type = <type>               # Defines the gameplay type (i.e. plains, which is used for the Nomad shock bonus)
                                # Types: pti, plains, forest, hills, mountains, jungle, marsh, desert
    
    # Used to explicitly make provinces this terrain category. Overrides automatic algorithm.
    terrain_override = {
        <province ids>
    }
    
    # Terrain-only modifiers
    movement_cost = <float>                     # Multiplier to movement time into/out of province with terrain
    defence = <int>                             # Addition to defence roll in combat in this terrain
    nation_designer_cost_multiplier = <float>   # Extra cost multiplier when picked in the Nation Designer
    
    # Province modifiers can be used here as well.
    <province modifiers>
}
Each indexed color in the terrain.bmp can be associated with a terrain category. This is used in the automatic terrain algorithm, saving you from having to use terrain_override.

The format is as follows:

terrain = {
    <name>  = {
        type = <terrain category>
        color = {
            <index>
        }
    }
}
For trees, rather than terrain categories, it is the terrain names defined in terrain = { }. Making the format:

tree = {
    <name>  = {
        terrain = <terrain>
        color = {
            <indexes>
        }
    }
}