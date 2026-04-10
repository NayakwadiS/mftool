from recommonmark.transform import AutoStructify
from recommonmark.parser import CommonMarkParser

# -- Project information -----------------------------------------------------

project = 'mftool'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = '3.2'

# The master toctree document.
master_doc = 'index'

html_favicon = 'mftool.png'

html_static_path = ['_static']

def setup(app):
    app.add_css_file('css/custom.css?v20260410')
