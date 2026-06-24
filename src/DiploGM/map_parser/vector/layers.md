# SVG Layers

Each layer is expected to have a corrosponding Inkscape lavel in the SVG. The bot searches for layers with the names listed below. A variant's `config.json` can also override a layer key if necessary.

## Province Layers

* **Region Colors** (aliases: `Region Fills`, `Provinces`; key: `land_layer`) - Contains fillable regions for each land province. The parser uses the province's fill color to assign initial ownership. If a province's color does not match any defined player or the neutral color, a new NPC country is created, named after its starting province.

* **Island Adjacencies** (aliases: `Hybrid Adjacencies`; key: `island_borders`) - Defines the full area of island provinces for adjacency calculations. Each path should include the entirety of the land and water of the province, up to and including the island ring.

* **Island Fills** (aliases: `Hybrid Fills`; key: `island_fill_layer`) - Fillable regions for the land portion of island provinces. Used entirely for detecting and displaying ownership.

* **Island Rings** (key: `island_ring_layer`) - Ring outlines around island provinces, colored along with island fills.

* **Sea Adjacencies** (aliases: `Sea Provinces`; key: `sea_borders`) - Contains regions for each sea province. Used for adjacency calculations, though sea provinces tend to not be colored in.

## Labels & Markers

* **Titles** (aliases: `Region Names`; key: `province_names`) - Text labels for each province. Used to assign names to provinces when `province_labels` is `false` in the config. Otherwise not strictly necessary.

* **Supply Centers** (aliases: `SC Markers`; key: `supply_center_icons`) - Markers indicating province supply centers, initial supply center ownwership, and home supply centers. Each element should be labeled with its province name.

## Unit Placement Layers

* **Army Locations** (key: `army`) - Contains one element per land/island province indicating where armies should be placed. Only the label and position matter; color is irrelevant. If a province lacks an army location, units default to the province centroid. This layer is cleared during the map render process.

* **Fleet Locations** (key: `fleet`) - Same as Army Locations but for fleets. Coastal provinces with multiple coasts should have separate elements labeled with each coast name.

* **Army Locations (Retreats)** (aliases: `Army Retreat Locations`; key: `retreat_army`) - Locations for retreating armies. Auto-created if missing by copying the `army` layer and translating it up and left.

* **Fleet Locations (Retreats)** (aliases: `Fleet Retreat Locations`; key: `retreat_fleet`) - Locations for retreating fleets. Auto-created if missing by copying the `fleet` layer with the same translation.

## Template & Starting State Layers

* **Symbol Templates** (key: `symbol_templates`)- Contains sub-groups with custom units and markers:
  * **Army / Fleet**: A sub-layer with units for each player. Each element should be labeled with its player name. If provided, these are used instead of the default colored shapes.
  * **Capital**: A capital marker template that can be copied to mark capital supply centers.

* **Units** (key: `starting_units`) - Contains pre-placed units for detecting initial positions. Only loaded when `detect_starting_units: true` in the config. Each unit element should be labeled with its province name. This layer is cleared during the map render process.

## Output Layers

* **Unit Output Layer** (key: `unit_output`) - An empty layer where the mapper places units.

* **Orders Output Layer** (key: `arrow_output`) - An empty layer where order arrows are drawn.

## Display Layers

* **Background** (key: `background`) - Background fills. Elements are recolored when alternate color modes (dark mode, etc.) are applied.

* **Other Fills** (key: `other_fills`) - Miscellaneous fills such as high seas. Recolored during color mode changes.

* **Season Title** (key: `season`) - Text element showing the current season, year, and/or game name. Formatted using the `season_format` string from the config.

* **Power Banners** (key: `power_banners`) - Contains groups for each player's scoreboard banner showing name, SC count, color, and victory conditions. Banners are recolored to match player colors, optionally sorted by SC count, and with text fields filled in dynamically.