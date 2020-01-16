"""
Author:  PH01L
Email:   phoil@osrsbox.com
Website: https://www.osrsbox.com

Description:
Program to invoke item database generation process.

Copyright (c) 2020, PH01L

###############################################################################
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
"""
import json
import logging
import argparse
from pathlib import Path

import config
from builders.items import build_item

# Configure logging
log_file_path = Path(Path(__file__).stem+".log")
if log_file_path.exists():
    log_file_path.unlink()
log_file_path.touch()
logging.basicConfig(filename=Path(__file__).stem+".log",
                    level=logging.DEBUG)
logging.info(">>> Starting builders/items/builder.py...")


def main(export: bool = False):
    # Load the current database contents
    items_compltete_file_path = Path(config.DOCS_PATH / "items-complete.json")
    with open(items_compltete_file_path) as f:
        all_db_items = json.load(f)

    # Load the item wikitext file
    wiki_text_file_path = Path(config.DATA_WIKI_PATH / "page-text-items.json")
    with open(wiki_text_file_path) as f:
        all_wikitext_raw = json.load(f)

    # Temp loading of item ID -> wikitext
    processed_wikitextfile_path = Path(config.DATA_WIKI_PATH / "processed-wikitext-items.json")
    with open(processed_wikitextfile_path) as f:
        all_wikitext_processed = json.load(f)

    # Load the invalid items file
    invalid_items_file_path = Path(config.DATA_ITEMS_PATH / "invalid-items.json")
    with open(invalid_items_file_path) as f:
        invalid_items_data = json.load(f)

    # Load buy limit data
    buy_limits_file_path = Path(config.DATA_ITEMS_PATH / "ge-limits-names.json")
    with open(buy_limits_file_path) as f:
        buy_limits_data = json.load(f)

    # Load skill requirement data
    skill_requirements_file_path = Path(config.DATA_ITEMS_PATH / "skill-requirements.json")
    with open(skill_requirements_file_path) as f:
        skill_requirements_data = json.load(f)

    # Load weapon_type data
    weapon_type_file_path = Path(config.DATA_ITEMS_PATH / "weapon-types.json")
    with open(weapon_type_file_path) as f:
        weapon_types_data = json.load(f)

    # Load stances data
    weapon_stance_file_path = Path(config.DATA_ITEMS_PATH / "weapon-stances.json")
    with open(weapon_stance_file_path) as f:
        weapon_stances_data = json.load(f)

    # Load the raw OSRS cache item data
    # This is the final data load, and used as baseline data for database population
    all_item_cache_data_path = Path(config.DATA_ITEMS_PATH / "items-cache-data.json")
    with open(all_item_cache_data_path) as f:
        all_item_cache_data = json.load(f)

    # Load schema data
    schema_file_path = Path(config.DATA_SCHEMAS_PATH / "schema-items.json")
    with open(schema_file_path) as f:
        schema_data = json.load(f)

    # Initialize a list of known items
    known_items = list()

    # Start processing every item!
    for item_id in all_item_cache_data:
        # Toggle to start, stop at a specific item ID
        # if int(item_id) < 24300:
        #     continue

        # Initialize the BuildItem class, used for all items
        builder = build_item.BuildItem(item_id=item_id,
                                       all_item_cache_data=all_item_cache_data,
                                       all_wikitext_processed=all_wikitext_processed,
                                       all_wikitext_raw=all_wikitext_raw,
                                       all_db_items=all_db_items,
                                       buy_limits_data=buy_limits_data,
                                       skill_requirements_data=skill_requirements_data,
                                       weapon_types_data=weapon_types_data,
                                       weapon_stances_data=weapon_stances_data,
                                       invalid_items_data=invalid_items_data,
                                       known_items=known_items,
                                       schema_data=schema_data,
                                       export=export)

        preprocessing_status = builder.preprocessing()
        if preprocessing_status["status"]:
            builder.populate_item()
            known_item = builder.check_duplicate_item()
            known_items.append(known_item)
            builder.generate_item_object()
            builder.compare_new_vs_old_item()
            builder.export_item_to_json()
            builder.validate_item()
        else:
            builder.populate_from_cache_data()
            builder.populate_non_wiki_item()
            known_item = builder.check_duplicate_item()
            known_items.append(known_item)
            builder.generate_item_object()
            builder.compare_new_vs_old_item()
            builder.export_item_to_json()
            builder.validate_item()

    # Done processing, rejoice!
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build item database.")
    parser.add_argument('--export',
                        default=False,
                        required=False,
                        help='A boolean of whether to export data.')
    args = parser.parse_args()

    export = args.export
    main(export)
