
## Instructions for Updating README

You should update the README if:
- You want to update it with new information
- You have added new notebooks
- You want to add specific index terms 
- You have modified existing notebooks

The basic process is to update the ENTRIES.json, verify, and assemble. This is detailed below. 

### Building the README

From the main directory, execute `./docs/build_readme.py`. This will rebuild the README as is. Done! 

### Adding New Notebooks 

1. Consider where your notebook should be. Add a description in the appropriate categories to [ENTRIES.json](ENTRIES.json). Note, it is okay to be included in multiple categories - some notebooks cover multiple topics. 
1. Follow the instructions [in the next section](#adding-index-terms) to add index terms. 
1. From the main directory, execute `./docs/build_readme.sh`. 
1. Confirm that the added index items are satisfactory. If not, modify the index terms

### <h3 id="adding-index-terms">Adding New Index Terms</h3>

1. Consider the scope of your term. It should be sufficiently specific that it comes up in the most relevant documents but not too general. 
2. Open [index_terms.json](index_terms.json). In the json, every key is linked to a list. If the list is empty, it will look for references to the key in all notebooks. If it is not empty, it will instead search for items in the list. Add your terms. 
3. From the main directory, execute `python3 ./docs/build_index.py`. 
4. From the same directory, execute `./docs/build_index.sh`. 
5. Confirm that the added index items are satisfactory. If not, repeat this process. 

### Changes to Existing Notebooks

If the text has changed, it is good to regenerate the index. Additionally, if you have modified any of the following files - FRONTMATTER.md, ENDMATTER.md, NOTEBOOKS.md - you need to rerun the build script. 

## Troubleshooting

- There are too many notebooks! 
    - Try populating the json list with terms that are more unique for your topic. 
- I don't see my index term!
    - Consider adding a unique word to your notebook, or use multiple key words. The current frequency requirement is five. 
    - The script also also look up code blocks, so if you use a custom instruction or variable repeatedly, this can work. 
- I don't like how the notebook is abbreviated 
    - Change it!! Or it will not be accepted. 
- My notebook comes up too many times! 
    - Consider shortening text and `buzzwords`. 
