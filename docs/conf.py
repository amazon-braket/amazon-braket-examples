"""Sphinx configuration."""
import datetime

# Sphinx configuration below.
project = "amazon-braket-examples"
copyright = "{}, Amazon.com".format(datetime.datetime.now().year)

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "jupyterlite_sphinx",
    "sphinx_design",
    "myst_parser",
    # 'nbsphinx',
]

myst_enable_extensions = ["colon_fence"]

source_suffix = ['.rst', '.md']
master_doc = "index"

autoclass_content = "both"
autodoc_member_order = "bysource"
default_role = "py:obj"

html_static_path = ["_static"]
html_theme = "sphinx_rtd_theme"
html_logo = "_static/aws.png"
html_title = "Amazon Braket Python SDK"
htmlhelp_basename = "{}doc".format(project)

language = "en"

napoleon_use_rtype = False

# jupyterlite_bind_ipynb_suffix = False
jupyterlite_contents = "./contents"