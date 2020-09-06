from recommonmark.transform import AutoStructify
from recommonmark.parser import CommonMarkParser

# -- Project information -----------------------------------------------------

project = 'mftool'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = '1.6'

# The master toctree document.
master_doc = 'index'

html_favicon = 'mftool.png'

html_static_path = ['_static']

def setup(app):
    app.add_stylesheet('css/custom.css?v20200905')
    
    
