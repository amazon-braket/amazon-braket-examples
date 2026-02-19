#!/usr/bin/env python3

import json
import os


def main(dry_run: bool = False):
    if not os.path.isdir("docs"):
        raise RuntimeError("running script from the wrong directory")

    with open("docs/categories.json", 'r') as fp:
        categories : dict = json.load(fp)

    with open("docs/ENTRIES.json", 'r') as fp:
        # first, check that all categories are used 
        entries : dict = json.load(fp)

    check_category = set()
    category_to_notebooks = {k:[] for k in categories}
    
    print("...reconstructing notebooks from entries.json")
    for title, properties in entries.items():
        for new_item in properties['categories']:
            check_category.add(new_item)
            category_to_notebooks[new_item].append(title)
    diff = check_category.difference(set(categories.keys())).union(set(categories.keys()).difference(check_category))
    assert len(diff)==0, diff

    main_body = ""
    assigned_key = set()
    for category,title in categories.items():
        main_body+= "\n---\n\n"
        main_body+= f"## <a name=\"{category}\">{title}</a>\n\n"
        for notebook in category_to_notebooks[category]:
            location = entries[notebook]["location"]
            text     = entries[notebook]["content"]
            key      = entries[notebook]["index_abbrv"]
            main_body+= f"-  [**{notebook}**]({location}) [({key})](#index_{key})\n\n"
            if key not in assigned_key:
                main_body = main_body[:-2] + f"<a name=\"{key}\"></a>\n\n"
                assigned_key.add(key)
            if not text[:2] == "  ":
                raise ValueError("Please format your notebook entry with two leading spaces.")
            main_body+= f"{text}\n\n"
    

    if not dry_run:
        with open("docs/_NOTEBOOKS.md",'w') as fp:
            fp.write(main_body)
        print("docs/_NOTEBOOK.md updated!")
    return main_body

if __name__ == "__main__":
    main()
