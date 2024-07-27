Before I describe my current mod, let me clarify how the provinces in the game are structured. Provinces are the smallest "units" on the map, with each province belonging to a specific nation state. Provinces are then grouped into "Areas", who are part of a broader "Region", which in itself is part of a broader "Superregion", which in itself is finally a part of a "Contintent". 
    
Let us take an example of the province of "Stockholm". Its complete structure would look something like this:

<example_province_structure>
    Continent: europe
    Superregion: europe_superregion
    Region: scandinavia_region
    Area: svealand_area
    Province: 3
</example_province_structure>

As you can see, provinces are represented by unique numbers (integers) in the data files, though they are represented by their names (e.g.: "Stockholm") during gameplay. Let us go through how exactly this is structured in the game files, step-by-step according to the above example structure.

**1. Continents:**
    Continents are defined in the "continent.txt" file (\Europa Universalis IV\map\continent.txt) in the form of a series of variables that contain province id numbers. E.g:
        <continent.txt>
            europe = {
                #Scandinavia
                1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
                1930 1981 1982 1983 1984 1985 2752 4113 4114 4123 4124 4141 4142 4143 4144 4145 4146
                4149 4151 4152 4163 4164 4165 4166
                #Baltic Coast
                32 33 34 35 36 37 38 39 40 41 42 43 767 770 1834 1841 1842 1935
                #Germany
                44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71
                72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 128 129 130 131 132 133 134 165 166 1757
                1758 1759 1760 1761 1762 1763 1769 1770 1771 1772 1775 1857 1858 1863 1867 1868 1869
                1870 1871 1872 1873 1874 1876 1878 1880 1931 2955 2956 2957 2964
                2965 2966 2967 2968 2969 2970 2971 2972 2973 2975 2993 2994 2995 2996 
                4237 4238
                # Germany 1.30
                4707 4708 4709 4710 4711 4712 4713 4714 4715 4716 4717 4718 4741 4742 4743 4744 4745
                4746 4747 4748 4749 4771 4772 4773 4774 4775
            }
            africa = {
                #North Africa
                334 335 336 337 338 339 340 341 342 343 344 345 346 347 348 349 350 351 352 353 354
                355 356 357 358 359 360 361 362 363 365 1751 1793 1794 1795 1882
                2315 2316 2317 2318 2319 2320 2321 2322 2323 2324 2325 2326
                2448 2449 2450 2451 2452 2453 2454 2455 2456 2457 2458 2459 2460
                2461 2462 2463 2464 2465 2466 2467 2468 2469 2470 2471 2472 2473
                2474 2475
                4561 4562 4563 4564 4566 4567 4568 4569
                #Various Islands
                1096 1097 1100 1102 1103
                #Most of Africa
                1110 1111 1112 1113 1114 1115 1116 1117 1118 1119 1120 1121 1122 1123 1124 1125 1126
                1127 1128 1129 1130 1131 1132 1133 1134 1135 1136 1137 1138 1139 1140 1141 1142 1143
                1144 1145 1146 1147 1148 1149 1150 1151 1152 1153 1154 1155 1156 1157 1158 1159 1160
                1161 1162 1163 1164 1165 1166 1167 1169 1170 1171 1172 1173 1174 1175 1176 1177
                1178 1179 1180 1181 1182 1183 1184 1185 1186 1187 1188 1189 1190 1191 1192
                1195 1196 1197 1198 1199 1200 1201 1202 1203 1204 1205 1206 1207 1208 1209 1210 1211
                1212 1213 1214 1215 1216 1217 1218 1219 1220 1221 1222 1223 1224 1225 1226 1227 1228
                1229 1230 1231 1232 1233 1234 1249 1796 1797 1798 1799 1800 1801
            }
        </continent.txt>

**2. Superregions:**
    Superregions are defined in the "superregion.txt" file (\Europa Universalis IV\map\superregion.txt) in the form of a series of variables that contain strings that represent regions. E.g:
        <superregion.txt>
            india_superregion = {
                bengal_region
                hindusthan_region
                west_india_region
                deccan_region
                coromandel_region
            }

            east_indies_superregion = {
                burma_region
                malaya_region
                moluccas_region	
                indonesia_region	
                indo_china_region
            }

            oceania_superregion = {
                oceanea_region
                australia_region
            }
        </superregion.txt>

**3. Regions:**
    Regions are defined in the "region.txt" file (\Europa Universalis IV\map\region.txt) in the form of a series of variables that contain strings that represent areas. E.g:
        <region.txt>
            scandinavia_region = {
                areas = {
                    svealand_area
                    norrland_area
                    gotaland_area
                    skaneland_area
                    jutland_area
                    denmark_area
                    finland_area
                    northern_norway
                    eastern_norway
                    western_norway
                    bothnia_area
                    subarctic_islands_area
                    laponia_area
                    vastra_gotaland_area
                    ostra_svealand_area
                }
            }


            low_countries_region = {
                areas = {
                    wallonia_area
                    flanders_area
                    holland_area
                    frisia_area
                    brabant_area
                    north_brabant_area
                }

            }
        </region.txt>

**4. Areas:**
    Areas are defined in the "area.txt" file (\Europa Universalis IV\map\area.txt) in the form of a series of variables that contain province id numbers (similar to "continent.txt"). E.g:
        <area.txt>
            svealand_area = { #3
                5 8 1985 
            }

            ostra_svealand_area = { #4
                1 4 1930
            }

            norrland_area = { #4
                9 11 18 4114
            }

            finland_area = { #5
                27 28 29 31 4123
            }

            bothnia_area = { #3
                19 4113 4152
            }
        </area.txt>    

**5. Provinces:**
    Provinces are defined in the "positions.txt" file (\Europa Universalis IV\map\positions.txt) in the form of a series of variables that assign numbers (integers) to specific positional values on the map. E.g:
        <positions.txt>
            #Östergötland
            2={
                position={
                    3067.000 1692.500 3052.000 1700.000 3053.000 1700.000 3067.000 1691.000 3053.000 1700.000 3052.500 1702.000 0.000 0.000 
                }
                rotation={
                    -1.134 0.000 0.000 -1.047 0.000 0.000 0.000 
                }
                height={
                    0.000 0.000 1.000 0.000 0.000 0.000 0.000 
                }
            }
            #Kalmar
            3={
                position={
                    3061.000 1667.000 3054.000 1675.000 3041.000 1669.000 3062.000 1672.000 3041.000 1669.000 3058.000 1676.000 0.000 0.000 
                }
                rotation={
                    -1.483 0.000 0.000 -1.658 0.000 0.000 0.000 
                }
                height={
                    0.000 0.000 1.000 0.000 0.000 0.000 0.000 
                }
            }
            #Bergslagen
            4={
                position={
                    3050.000 1742.000 3051.000 1731.000 3050.000 1742.000 3047.000 1758.000 3050.000 1742.000 3052.000 1732.000 0.000 0.000 
                }
                rotation={
                    0.000 0.000 0.000 0.000 0.000 0.000 0.000 
                }
                height={
                    0.000 0.000 1.000 0.000 0.000 0.000 0.000 
                }
            }
        </positions.txt>
    Note here that the names of the provinces are given in the hashtags above each number.

Beyond the positional categories to which every province belongs, as described above, there are two further properties of a province that we need to cover: climate and terrain.

**Climate:**
    Climate is pretty straightforward; it describes what type of climate a province experiences. They are defined in the "climate.txt" file (\Europa Universalis IV\map\climate.txt) in the form of a series of variables that contain province id numbers (similar to "continent.txt"). E.g:
        <climate.txt>
            tropical = {
                    # Southwest Africa
                    1164 1165 1166 1167 1169 1170 1171 1172 1901
                    2948 2949
                    798 1168
                    # North and West Africa
                    1114  1117 1118 1119 1120 1121 1122 1124 1125
                    1126 1136 1137 1138 1139 1140 1141 1143 1144 1145 1146 1147
                    1149 1150 1151 1152 1153 1154 1155 1160 1161 1162 1163 1249
                    # More West Africa
                    2238 2242 2248 2250 2252 2254 2256 2258 2266 2278 2280 2286 2290 2292 2294
                    2241 2249 2253 2255 2257 2267 2281 2283 2285 2289 2291 2293 2295
                    # Africa
                    788 1182 1183 1186 1187 1191 1192 1195 1196 1197 1198 1199 1200 1201 1202 4049
                    # India
                    516 517 526 527 529 530 531 533 534 535 537 539 540 542 543 544 545 546 547 548 549 552 553 561 564 568 570 572 573 574 580
                    1946 1947 2026 2028 2029 2030 2033 2034 2036 2037 2038 2039 2041 2043 2048 2049 2050 2057 2080 2081 2083 2084 2089 2090 2091 2092 2099 2100 4407 4408 4409
                    4410 4413 4415 4416 4417 4418 4419 4425 4427 4429 4430 4431 4432 4433 4439 4441 4442 4443
                    4444 4445 4446 4448 4450 4451 4460 4473 4474 4475 4476 4477 4478
                }
                arid = {
                    # Persia
                    427 432 433 434 435 436 438 447 455 575 576 577 2220 2216 2222 2224 2229 2230 2231 2232 2233 2234 2235 4323 4327 4334 4336 4345

                    # Arabia
                    391 392 393 403 404 394 383 384 385 386 389 402 380 381 2327 2328 2329 2330 2331 2332 2335 2336 2337 2338 2339 2340 2343 2344 2345 2347
                    #New Provinces in Arabia
                    395 397 401 405 407 409 2311 2314 2333 2341 2342
                    4268 4269 4270 4271 4272 4273 4274 4275
                    4277 4278 4283 4284 4285 4287 4288

                    # Wasteland
                    1779 1793 1794 1795 1786 1790 1791 2200 2334
                }
        </climate.txt>

**Terrain:**
    Finally, there are several different types of terrain in Europa Universalis 4 that a province can belong to (e.g.: mountains, farmlands, hills, etc.). Each of these terrains have different properties that impact their utility, such as mountains being easier to defend, farmlands being easier to develop, and so on.

    They are defined in the "terrain.txt" file (\Europa Universalis IV\map\terrain.txt). Unlike the previous text files, the terrain file is more complicated as it also details the specific bonuses and maluses associated with each terrain type, as well as how it is represented on the map. Terrain types are then assigned to province id numbers. E.g:
        <terrain.txt>
            ##################################################################
            ### Terrain Categories
            ###
            ### Terrain types: plains, mountains, hills, desert, artic, forest, jungle, marsh, pti
            ### Types are used by the game to apply certain bonuses/maluses on movement/combat etc.
            ###
            ### Sound types: plains, forest, desert, sea, jungle, mountains

            categories =  {
                pti = {
                    type = pti
                }

                ocean = {
                    color = { 255 255 255 }

                    sound_type = sea
                    is_water = yes

                    movement_cost = 1.0
                }

                inland_ocean = {
                    color = { 0 0 200 }

                    sound_type = sea
                    is_water = yes
                    inland_sea = yes

                    movement_cost = 1.0
                    
                    terrain_override = {
                        1355 1358 1360
                        1361 1362 1363 1364 1365 1366 1367 1368 1369 1370 1371 1393 1394 1395
                        1359 1398 1399 1400
                        1356 1357 1401 1408 1409 1410
                        1348 1347 1345
                        1402 4357 1397 4358
                        1358 1353 1352 1351 1350 1354
                    }
                }	

                glacier = {
                    color = { 235 235 235 }

                    sound_type = desert

                    defence = 1
                    movement_cost = 1.25
                    supply_limit = 2		
                    local_development_cost = 0.5
                    nation_designer_cost_multiplier = 0.75		
                    
                    terrain_override = {		
                        1034 1035 1104 1105 2074 2128 2129 2025 2440 2574
                    }
                }
                farmlands = {
                    color = { 179 255 64 }

                    type = plains
                    sound_type = plains

                    movement_cost = 1.10
                    local_development_cost = -0.05
                    supply_limit = 10
                    allowed_num_of_buildings = 1
                    nation_designer_cost_multiplier = 1.05
                    
                    terrain_override = {
                        104 109 108 1744 1865
                        
                        45 44 1874 113 172 
                        
                        161 2998 160 125
                        
                        506 507 510 522 523 524 532 540 555 556 558 561 563 2026 2044 2045 2047 2060 2063 2075 2095
                        
                        115 117 118 121 1862
                }
            }
        </terrain.txt>
    In the above example, "color" is used to tell the game how a terrain type is supposed to be represented on the game map, "type" and "sound_type" and special variables, "movement_cost", "supply_limit" etc. are used to outline the specific properties of the terrain type and how it impacts the game. Finally, "terrain_override" is the variable that assigns the terrain type to the specified province ID numbers.

In essence, the data structure of provinces could be described using the following SQLModel table:
    class Province(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    continent: str
    super_region: str
    region: str
    area: str
    climate: str
    terrain: str

Now that we've described the data structure of provinces in the game files, let us move on to describing how the user interface for provinces works in the game. In short, when the user clicks on a province, a user interface pops out that contains information about the province, as well as a generic image of the terrain type to which it belongs.

So, for example, a province that has "farmland" terrain would display a generic image of farmland. This image is not unique, but is common for all provinces with "farmland" terrain. And so it is with all other terrain types.

That's where my mod comes in; I want to replace the generic terrain images and give each province a unique image.

As this is a massive undertaking, this requires automating the process with the help of scripts and AI image generation.

The process that I envision is the following:
**1. Data Extraction and Organization:**
    Write a series of functions that extract the relevant province information from the game files (continent.txt, superregion.txt, region.txt, area.txt, positions.txt, climate.txt, terrain.txt) and organize it into a SQLite database using SQLModel.
    
    Work done so far:
        SQLModel classes have been created, outlined in the below db.py module:
            <db.py>
                # Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

                """
                This module provides database functionality for storing and retrieving data.

                It utilizes SQLite and SQLModel for database management.
                """

                import structlog
                from sqlmodel import Field, Relationship, SQLModel, create_engine

                # Initialize logger for this module.
                log = structlog.stdlib.get_logger(__name__)

                # Construct the SQLite URL.
                sqlite_url = "sqlite:///database/SQLite.db"
                engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
                SQLModel.metadata.create_all(engine)


                # =========================================================#
                #                Database Model Definitions                #
                # =========================================================#


                class Continent(SQLModel, table=True):
                    """
                    Represents a continent in EU4.

                    Attributes:
                    ----------
                    - id (int): The primary key of the continent.
                    - name (str): The name of the continent (e.g., "europe").
                    """

                    id: int | None = Field(default=None, primary_key=True)
                    name: str = Field(index=True)

                    # One-to-many relationship with SuperRegion.
                    super_regions: list["SuperRegion"] = Relationship(back_populates="continent")


                class SuperRegion(SQLModel, table=True):
                    """
                    Represents a super-region in EU4.

                    Attributes:
                    ----------
                    - id (int): The primary key of the super-region.
                    - name (str): The name of the super-region (e.g., "europe_superregion").
                    - continent_id (int): Foreign key referencing the continent this super-region belongs to.
                    """

                    id: int | None = Field(default=None, primary_key=True)
                    name: str = Field(index=True)

                    # Foreign key to Continent.
                    continent_id: int | None = Field(default=None, foreign_key="continent.id")
                    # One-to-one relationship with Continent.
                    continent: Continent | None = Relationship(back_populates="super_regions")
                    # One-to-many relationship with Region.
                    regions: list["Region"] = Relationship(back_populates="super_region")


                class Region(SQLModel, table=True):
                    """
                    Represents a region in EU4.

                    Attributes:
                    ----------
                    - id (int): The primary key of the region.
                    - name (str): The name of the region (e.g., "scandinavia_region").
                    - super_region_id (int): Foreign key referencing the super-region this region belongs to.
                    """

                    id: int | None = Field(default=None, primary_key=True)
                    name: str = Field(index=True)  # e.g., "scandinavia_region"

                    # Foreign key to SuperRegion.
                    super_region_id: int | None = Field(default=None, foreign_key="superregion.id")
                    # One-to-one relationship with SuperRegion.
                    super_region: SuperRegion | None = Relationship(back_populates="regions")

                    # One-to-many relationship with Area.
                    areas: list["Area"] = Relationship(back_populates="region")


                class Area(SQLModel, table=True):
                    """
                    Represents an area within a region in EU4.

                    Attributes:
                    ----------
                    - id (int): The primary key of the area.
                    - name (str): The name of the area (e.g., "svealand_area").
                    - region_id (int): Foreign key referencing the region this area belongs to.
                    """

                    id: int | None = Field(default=None, primary_key=True)
                    name: str = Field(index=True)

                    # Foreign key to Region.
                    region_id: int | None = Field(default=None, foreign_key="region.id")
                    # One-to-one relationship with Region.
                    region: Region | None = Relationship(back_populates="areas")

                    # One-to-many relationship with Province
                    provinces: list["Province"] = Relationship(back_populates="area")


                class Climate(SQLModel, table=True):
                    """
                    Represents a climate type in EU4.

                    Attributes:
                    ----------
                    - id (int): The primary key of the climate type.
                    - name (str): The name of the climate type (e.g., "tropical", "arid").
                    """

                    id: int | None = Field(default=None, primary_key=True)
                    name: str = Field(index=True)

                    # One-to-many relationship with Province
                    provinces: list["Province"] = Relationship(back_populates="climate")


                class Terrain(SQLModel, table=True):
                    """
                    Represents a terrain type in EU4.

                    Attributes:
                    ----------
                    - id (int): The primary key of the terrain type.
                    - name (str): The name of the terrain type (e.g., "farmlands", "mountains").
                    """

                    id: int | None = Field(default=None, primary_key=True)
                    name: str = Field(index=True)

                    # One-to-many relationship with Province.
                    provinces: list["Province"] = Relationship(back_populates="terrain")


                class Province(SQLModel, table=True):
                    """
                    Represents a province in EU4.

                    Attributes:
                    ----------
                    - id (int): The primary key of the province (same as the province ID in game files).
                    - name (str): The name of the province (e.g., "Stockholm").
                    - area_id (int): Foreign key referencing the area this province belongs to.
                    - climate_id (int): Foreign key referencing the climate type of this province.
                    - terrain_id (int): Foreign key referencing the terrain type of this province.
                    - image_path (str): The path to the generated image for this province.
                    """

                    id: int = Field(primary_key=True)
                    name: str
                    prompt: str | None = Field(default=None)
                    image_url: str | None = Field(default=None)
                    # ... other image-related fields like generation parameters, etc.

                    # Foreign keys for relationships.
                    area_id: int | None = Field(default=None, foreign_key="area.id")
                    climate_id: int | None = Field(default=None, foreign_key="climate.id")
                    terrain_id: int | None = Field(default=None, foreign_key="terrain.id")

                    # One-to-one relationships.
                    area: Area | None = Relationship(back_populates="provinces")
                    climate: Climate | None = Relationship(back_populates="provinces")
                    terrain: Terrain | None = Relationship(back_populates="provinces")


                # ============================================================#
                #                Database Utility Functions                  #
                # ============================================================#


                def create_database() -> None:
                    """
                    Creates the database tables if they don't exist.

                    Args:
                    ----
                    - None

                    Returns:
                    -------
                    - None
                    """
                    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
                    SQLModel.metadata.create_all(engine)
            </db.py>
    
    Work remaining: Write functions to exctract the data from the game files and upload them according the the database class structure.

**2. Prompt Generation:**
    Use the extracted data to craft detailed prompts with a consistent style that capture the essence of each province. This would include information about:

        Terrain: Emphasize the specific terrain features (hills, forests, mountains, etc)

        Climate: Reflect the climate (lush vegetation for tropical, barren for desert)

    In conjunction, design a function to introduce variety in the prompts to avoid repetitive images.

    Work done so far:
        

**3:**
    Generate images based on these prompts and with a consistent style using the Replicate API.

**4:**
    Optimize the images to reduce size.

**5:**
    Modify the game files to recognize and use the new custom images.

    This involves two steps:
    1. 
        Modifying terrains.txt to add custom terrain for each image, making sure to keep original properties. This can be scripted to simply take the terrain type from the Terrain SQLModel and switch out the name and terrain override. E.g.:
            savannah = {
            color = { 248 199 23  }

            sound_type = plains
            type = plains

            supply_limit = 6
            movement_cost = 1.00
            local_development_cost = 0.15
            nation_designer_cost_multiplier = 0.95	
            
            terrain_override = {
                768 776 1800 2805 2809 2810 2812 2814 2815 2855 2859 2879 2884 2887 
                2893 2895 2897 2908 2909 2910 2918 2923 2925 2926 2939 
            }

        would become:

        savannah_number_768 = {
            color = { 248 199 23  }

            sound_type = plains
            type = plains

            supply_limit = 6
            movement_cost = 1.00
            local_development_cost = 0.15
            nation_designer_cost_multiplier = 0.95	
            
            terrain_override = {
                768
            }
        }

    2.
        recursively search through the game files and use a regex expression to replace "has_terrain" modifiers with an updated list.

**6:**
    Write tests (unit, integration and end-to-end) for all functions