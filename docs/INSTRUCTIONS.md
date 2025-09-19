
## Instructions for Updating README

You need to update the README if:
- You want to update the README with new information
- You have added new examples
- You want to add specific index terms 
- You have modified existing notebooks substantially in their content

The basic process is to update the ENTRIES.json, verify, and rebuild. This is detailed below. 

### Building the README

From the main directory, simply execute `./docs/build_readme.py`, and commit the updated README file. 

### Adding New Notebooks 

1. Add your notebook to the appropriate location.
2. Create a new json entry in [ENTRIES.json](ENTRIES.json) with the following structure (adding a comma to any previous entries):
```
    notebook_title: {
        "index_abbrv": my_index_abbreviation,
        "index_terms": [index_term_1, index_term_2, etc.],
        "categories" : [category, optional_category],
        "location"   : notebook_location,
        "content"    : notebook_description
    }
```
The following variables are all strings: 
- `notebook_title` : the title of your notebook -  see previous naming convenctions  "Getting Starts with...", "Hello....", etc. 
- `my_index_abbreviation` : an abbreviation of your title -  avoid "of", "the", "with", etc., and see other entries.
- `index_terms` : optional - follow the instructions [in the next section](#adding-index-terms).
- `category, optional_category` : sections your notebook will appear in - see the category keys listed in [build_body.py](build_body.py). 
- `notebook_location` : location of the notebook - directory starts from "examples/...."
- `notebook_description` : displayed summary of your notebook - about 1-3 sentences with what users will learn and see how to run, and has two leading spaces 

3. Once completed, from the main directory, execute `./docs/build_readme.sh`. 
4. Confirm that the added index items in the README are satisfactory, and that your entry is displaying properly. If not, modify the index terms and repeat. 

### <h3 id="adding-index-terms">Adding New Index Terms</h3>

The index is generated searching through terms from [index_terms.json](index_terms.json) and then adding additional user-specified terms from the "index_terms" fields in [ENTRIES.json](ENTRIES.json). If you write a notebook and want a specific index term, simply include the term in the json entry. 

If you feel a common index term has been omitted, add it to [index_terms.json](index_terms.json), rebuild the README, and inspect the index. The entries in [index_terms.json](index_terms.json) corresponds to a disaplyed terms with list of key words that it looks for. If the list is empty, the displayed word will be searched for. 

If in the genearted index, there are too many occurences, or too few, follow the troubleshooting below. 

## Troubleshooting

- There are too many notebooks! 
    - Try populating the json list with terms that are more unique for your topic. 
- I don't see my index term!
    - Consider adding a unique word to your notebook, or use multiple key words. The current frequency requirement is five. 
    - The script also also look up code blocks, so if you use a custom instruction or variable repeatedly, this can work. 
- I don't like how the notebook is abbreviated 
    - Change it!! Or it will not be accepted. 
- My notebook comes up too many times! 
    - Consider shortening text and removing `buzzwords`. 
