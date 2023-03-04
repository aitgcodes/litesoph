# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import datetime

import os
import sys
#sys.path.insert(0, os.path.abspath('../../test/'))
assert sys.version_info >= (3, 6)
sys.path.append('.')


# -- Project information -----------------------------------------------------
master_doc = 'index'
project = 'LITESOPH'
copyright = f'{datetime.date.today().year}, LITESOPH members and team'
#author = 'Jaberuddin Ahammad'

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "myst_parser",
    'sphinx.ext.extlinks',
    'sphinx.ext.mathjax',
]
#intersphinx_mapping = {
#    "rtd": ("https://docs.readthedocs.io/en/stable/", None),
 #   "python": ("https://docs.python.org/3/", None),
  #  "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
#}
nitpick_ignore = [('py:class', 'gpaw.calculator.GPAW'),
                  ('py:class', 'gpaw.spinorbit.BZWaveFunctions'),
                  ('py:class', 'GPAW'),
                  ('py:class', 'Atoms'),
                  ('py:class', 'np.ndarray'),
                  ('py:class', 'ase.spectrum.dosdata.GridDOSData'),
                  ('py:class', 'ase.atoms.Atoms'),
                  ('py:class', 'gpaw.point_groups.group.PointGroup'),
                  ('py:class', 'UniformGridFunctions'),
                  ('py:class', 'DomainType'),
                  ('py:class', 'Path'),
                  ('py:class', 'Vector'),
                  ('py:class', 'ArrayLike1D'),
                  ('py:class', 'ArrayLike2D'),
                  ('py:class', 'Array1D'),
                  ('py:class', 'Array2D'),
                  ('py:class', 'Array3D'),
                  ('py:class', 'MPIComm'),
                  ('py:class', 'DomainType'),
                  ('py:class', 'IO')]

#intersphinx_disabled_domains = ["std"]
extlinks = {
    'doi': ('https://doi.org/%s', 'doi: %s'),
    'arxiv': ('https://arxiv.org/abs/%s', 'arXiv: %s'),
    'mr': ('https://gitlab.com/gpaw/gpaw/-/merge_requests/%s', 'MR: !%s'),
    'xkcd': ('https://xkcd.com/%s', 'XKCD: %s')}

spelling_word_list_filename = 'words.txt'
spelling_show_suggestions = True
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['build']
pygments_style = 'sphinx'
autoclass_content = 'both'
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'restructuredtext',
    '.md': 'markdown',
}
# -- Options for EPUB output
epub_show_urls = "footnote"
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]



# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
#html_style = 'gpaw.css'
#html_title = 'GPAW'
#html_favicon = 'static/gpaw_favicon.ico'
#html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


#################################
# Used the default or others in math form.
default_role = 'math'

autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'
html_last_updated_fmt = '%a, %d %b %Y %H:%M:%S'

mathjax3_config = {
    'tex': {
        'macros': {
            'br': '{\\mathbf r}',
            'bk': '{\\mathbf k}',
            'bG': '{\\mathbf G}'}}}

####################################


