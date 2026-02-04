#!/bin/zsh
set -e
python3 docs/_build_body.py
python3 docs/_build_index.py
cat docs/FRONTMATTER.md \
    docs/_NOTEBOOKS.md \
    docs/_INDEX.md \
    docs/ENDMATTER.md \
    >  README.md
echo "- README.md updated!" 
rm docs/_INDEX.md docs/_NOTEBOOKS.md
echo "- Cleaned up README generation."