#!/bin/zsh
python3 docs/build_body.py
python3 docs/build_index.py
cat docs/_FRONTMATTER.md \
    docs/_NOTEBOOKS.md \
    docs/_INDEX.md \
    docs/_ENDMATTER.md \
    >  README.md
echo "README.md updated!" 