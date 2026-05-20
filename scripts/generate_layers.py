"""Generate unit location layers for a variant map SVG.

For each province in the map, places a sample unit (army, fleet, etc.) at the province's centroid in the appropriate
SVG layer. Also generates retreat layers and a titles layer.

Usage:
    python3 scripts/generate_layers.py <variant> [unit_types...]

Arguments:
    variant         Variant name (e.g. classic, impdip.2.5.rc1)
    unit_types      Layer names to generate (default: army fleet)

The script must be run from the repository root.
"""
from __future__ import annotations

import copy
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import shapely
import lxml.etree as etree

from DiploGM.map_parser.vector.vector import Parser
from DiploGM.map_parser.vector.transform import TransGL3
from DiploGM.map_parser.vector.utils import (
    find_svg_element, get_coordinates, get_unit_coordinates, NAMESPACE, SVG_CONFIG_KEY
)
from DiploGM.models.province import Province, ProvinceType

INKSCAPE_LABEL = f"{NAMESPACE.get('inkscape')}label"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("generate_layers")

def generate_layers(parser: Parser, unit_types: list[str]) -> bytes:
    """Using sample SVG elements in the unit and title layers,
    give each province unit locations, retreat locations, and a title label,
    then return the modified SVG as bytes."""
    svg_root = etree.parse(parser.data["file"])
    config = parser.layers

    layer_names = []
    for unit_type in unit_types:
        layer_names.append(unit_type)
        layer_names.append(f"retreat_{unit_type}")
    layer_names.append("titles")

    unit_radius = parser.data[SVG_CONFIG_KEY].get("unit_radius", 20)
    layers = {}
    existing_objects: dict[str, set[str]] = {}

    for layer_name in layer_names:
        if (layer := find_svg_element(svg_root, layer_name, config)) is None:
            if layer_name.startswith("retreat_"):
                logger.info("Layer %s not found in SVG. Duplicating %s layer.",
                            layer_name, layer_name.replace("retreat_", ""))
                layer = _create_retreat_layer(svg_root, layer_name, config, unit_radius)
            else:
                logger.warning("Layer %s not found in SVG, skipping.", layer_name)
                continue
        if len(layer) == 0:
            logger.warning("Layer %s has no sample element, skipping.", layer_name)
            continue
        sample_element = copy.deepcopy(layer[0])
        sample_element.attrib.pop("transform", None)
        layer.attrib.pop("transform", None)
        if layer_name == "titles":
            coordinate = get_coordinates(sample_element)
        else:
            coordinate = get_unit_coordinates(sample_element)
        layers[layer_name] = {"layer": layer, "sample_element": sample_element, "coordinate": coordinate}
        existing_objects[layer_name] = set()
        for element in layer:
            if (label := element.get(INKSCAPE_LABEL)) is not None:
                existing_objects[layer_name].add(label)

    # For each province, add an element to each layer at its centroid
    for province in parser.name_to_province.values():
        for layer_name, layer_info in layers.items():
            _add_element(province, layer_name, layer_info, existing_objects, unit_radius)

    return etree.tostring(svg_root)

def _create_retreat_layer(
    svg_root: etree._ElementTree, layer_name: str, config_data: dict, unit_radius: int
) -> etree._Element:
    """Create a retreat layer by copying the corresponding move layer."""
    move_layer_name = layer_name.replace("retreat_", "")
    move_layer = find_svg_element(svg_root, move_layer_name, config_data)
    if move_layer is None:
        raise ValueError(f"Neither {layer_name} nor {move_layer_name} layers were found in the SVG")
    retreat_layer = copy.deepcopy(move_layer)
    retreat_layer.set("id", config_data.get(layer_name, f"{move_layer_name}_retreat"))
    retreat_layer.set(f"{NAMESPACE.get('inkscape')}label",
                      f"{move_layer_name.capitalize()} Locations (Retreats)")
    retreat_layer.set("transform",
                      f"translate({-unit_radius}, {-unit_radius}) {retreat_layer.get('transform', '')}")
    svg_root.getroot().append(retreat_layer)
    return retreat_layer

def _add_element(province: Province, layer_name: str, layer_info: dict,
                 existing_objects: dict[str, set[str]], unit_radius: int) -> None:
    if province.name in existing_objects.get(layer_name, set()):
        return
    if layer_name.endswith("army") and province.type == ProvinceType.SEA:
        return
    if (layer_name.endswith("fleet") and province.type == ProvinceType.LAND
        and not any(adj.type in {ProvinceType.SEA, ProvinceType.ISLAND} for adj in province.adjacencies.get_all())):
        return

    copied_element = copy.deepcopy(layer_info["sample_element"])
    copied_element.set(INKSCAPE_LABEL, province.name)

    center = shapely.centroid(province.geometry)
    center = complex(center.x, center.y) if center else complex(0)
    distance = center - layer_info["coordinate"]

    if layer_name.startswith("retreat_"):
        distance -= complex(unit_radius, unit_radius)

    if layer_name == "titles":
        for child in list(copied_element):
            copied_element.remove(child)
        copied_element.text = province.name
        copied_element.set("x", str(center.real))
        copied_element.set("y", str(center.imag))
        style = copied_element.get("style", "")
        style = ";".join(p for p in style.split(";") if not p.strip().startswith("text-anchor"))
        style = f"text-anchor:middle;{style}" if style else "text-anchor:middle"
        copied_element.set("style", style)
    else:
        trans = TransGL3().init(x_c=distance.real, y_c=distance.imag)
        copied_element.set("transform", str(trans))
    layer_info["layer"].append(copied_element)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    variant_name = sys.argv[1]
    unit_types = sys.argv[2:] if len(sys.argv) > 2 else ["army", "fleet"]

    logger.info("Parsing variant '%s'", variant_name)
    parser = Parser(variant_name)
    _, adjacencies = parser._read_map()

    for name1, name2 in adjacencies:
        parser.name_to_province[name1].adjacencies.add(parser.name_to_province[name2])
        parser.name_to_province[name2].adjacencies.add(parser.name_to_province[name1])

    logger.info("Generating layers: %s", unit_types)
    result = generate_layers(parser, unit_types)

    svg_path = Path(parser.data["file"])
    output_path = svg_path.with_stem(svg_path.stem + "_layers")
    output_path.write_bytes(result)
    logger.info("Output written to %s", output_path)


if __name__ == "__main__":
    main()
