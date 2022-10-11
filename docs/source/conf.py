# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import pkg_resources

sys.path.insert(0, os.path.abspath("../../partitura"))
# The master toctree document.
master_doc = "index"

# -- Project information -----------------------------------------------------

project = "partitura"
# copyright = '2019, Maarten Grachten'
author = "Maarten Grachten, Carlos Cancino-Chacón, Silvan Peter, Emmanouil Karystinaios, Francesco Foscarin, Thassilo Gadermaier"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "1.1.0" # pkg_resources.get_distribution("partitura").version
# The full version, including alpha/beta/rc tags.
release = "1.1.0"

# # The full version, including alpha/beta/rc tags
# release = pkg_resources.get_distribution("partitura").version
# # release = '0.1.0-pre'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "python"


# -- General configuration ---------------------------------------------------

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    # 'sphinxcontrib.napoleon',
    "sphinx.ext.napoleon",
    'nbsphinx',
    # 'sphinxcontrib.bibtex',  # for bibliographic references
    # 'sphinxcontrib.rsvgconverter',  # for SVG->PDF conversion in LaTeX output
    # 'sphinx_gallery.load_style',  # load CSS for gallery (needs SG >= 0.6)
    # 'sphinx_last_updated_by_git',  #? get "last updated" from Git
    # 'sphinx_codeautolink',  # automatic links from code to documentation
    # 'sphinx.ext.intersphinx',  # links to other Sphinx projects (e.g. NumPy)
]

# These projects are also used for the sphinx_codeautolink extension:
intersphinx_mapping = {
    'IPython': ('https://ipython.readthedocs.io/en/stable/', None),
    'matplotlib': ('https://matplotlib.org/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'python': ('https://docs.python.org/3/', None),
}

# see http://stackoverflow.com/q/12206334/562769
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# only import and set the theme if we're building docs locally
if os.environ.get("READTHEDOCS") != "True":
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
else:
    html_theme = "default"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = "partituradoc"