from recommonmark.transform import AutoStructify
from recommonmark.parser import CommonMarkParser

# -- Project information -----------------------------------------------------

project = 'mftool'

# The master toctree document.
master_doc = 'index'

html_favicon = 'mftool.png'

html_static_path = ['_static']

def setup(app):
    app.add_stylesheet('css/custom.css')
