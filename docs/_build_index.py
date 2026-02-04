#!/usr/bin/env python3

import json
import os
from collections import defaultdict


def extract_notebook_content(notebook_path : str):
    """Extract text content (code and markdown) from a Jupyter notebook (notebook path)"""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        content = []
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'markdown':
                content.extend(cell.get('source', []))
            elif cell.get('cell_type') == 'code':
                content.extend(line.strip() for line in cell.get('source', []))
        
        return ' '.join(content)
    except Exception as e:
        print(f"Error processing {notebook_path}: {e}")
        return ""

def find_terms_in_notebooks(
        notebook_titles : list[str], 
        notebook_contents : list[str], 
        min_frequency = 5, ):
    """ Load list of terms and locate them in the notebook data """

    with open("docs/index_terms.json", 'r') as fp:
        terms = json.load(fp)

    terms_to_notebooks = defaultdict(list)
    
    for title, content in zip(notebook_titles, notebook_contents):
        for index_term,search in terms.items(): # iterate over differnent search terms
            if len(search)==0:
                search = [index_term]
            freq = [content.lower().count(term.lower()) for term in search] 
            if max(freq) >= min_frequency:
                terms_to_notebooks[index_term].append(title)
    return terms_to_notebooks

def generate_index_section(terms_to_loc, loc_to_key):
    markdown  = "## <a name=\"index\">Index</a> \n"
    markdown += " |  Terms  | Notebooks  | \n | -- | -- | \n"
    sorted_terms = sorted(terms_to_loc)
    used_keys = set()

    for term in sorted_terms:
        locations = terms_to_loc[term]
        print(f'......adding term: {term}')
        markdown += f" | {term:10} |  "
        for loc in locations:
            key = loc_to_key[loc]
            markdown += f"[{key}](#{key}), "
            if key not in used_keys:
                markdown = markdown[:-2] + f"<a name=\"index_{key}\"></a>, "
                used_keys.add(key)
        markdown = markdown[:-2] + "| <br>\n"    
    return markdown

def main(dry_run: bool = False):
    """
    build the index 

    below we use the following variables:
        - index_abbrv/key - the shorthand form of the notebook title 
        - loc/locations - where the notebook is 
        - terms - keywords or index terms 
    """
    if not os.path.isdir("docs"):
        raise RuntimeError("running script from the wrong directory")
    
    with open("docs/ENTRIES.json", "r") as fp:
        entries : dict = json.load(fp)

    loc_to_key = {v["location"]:v["index_abbrv"] for v in entries.values()}
    print("...extracting notebook content...")
    notebook_locations, notebook_contents = [],[]
    for properties in entries.values():
        notebook_locations.append(properties["location"])
        notebook_contents.append(extract_notebook_content(properties['location']))

    index_path = "docs/_INDEX.md"
    # Group terms into categories
    print("...finding terms in notebooks")
    terms_to_loc : dict[str,list] = find_terms_in_notebooks(notebook_locations, notebook_contents)
    # check if there were additional index terms specified in the entries 
    for properties in entries.values():
        for index_term in properties["index_terms"]:
            if index_term in terms_to_loc:
                if properties["location"] not in terms_to_loc[index_term]:
                    terms_to_loc[index_term].append(properties["location"])
            else:
                terms_to_loc[index_term] = [properties["location"]]

    print("...generating the index")
    index_section = generate_index_section(terms_to_loc, loc_to_key)

    # Update INDEX
    if not dry_run:
        with open(index_path, "w") as f:
            f.write(index_section)
        print("docs/_INDEX.md updated!")
    return index_section

if __name__ == "__main__":
    main()
