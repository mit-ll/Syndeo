import os
import sys

# You will need to append paths to sys.path if you want Sphinx to be able to import them.
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../.."))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project: str = "Syndeo"
copyright: str = "2024 Massachusetts Institute of Technology"
author: str = "William Li"
release: str = "0.3"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = [
    "myst_parser",
    "sphinx_design",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

source_suffix: dict = {".rst": "restructuredtext"}

# Setting options
autosummary_generate: bool = True
autosummary_imported_members: bool = True
autosummary_generate_overwrite: bool = True
exclude_patterns: list[str] = []
myst_enable_extensions: list[str] = ["colon_fence"]
templates_path: list[str] = ["_templates"]

# -- CSS Style Sheets --------------------------------------------------------
# https://docs.readthedocs.io/en/stable/guides/adding-custom-css.html

# These folders are copied to the documentation's HTML output
html_static_path: list[str] = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files: list[str] = [
    "css/custom.css",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# fontawesome: https://fontawesome.com/search?o=r&m=free

html_theme: str = "sphinx_book_theme"
html_theme_options: dict = {
    "icon_links": [
        {
            "name": "William Li",
            "url": "https://github.com/destin-v",
            "icon": "fa-regular fa-chess-knight",
            "type": "fontawesome",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/mit-ll/Syndeo",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
        {
            "name": "Executable Books",
            "url": "https://executablebooks.org/",
            "icon": "_static/ebp-logo.png",
            "type": "local",
        },
        {
            "name": "Book Theme",
            "url": "https://sphinx-book-theme.readthedocs.io/en/stable/index.html",
            "icon": "_static/book-theme.svg",
            "type": "local",
        },
    ],
    "logo": {
        # "text": "My awesome documentation",
        "image_light": "_static/logo.svg",
        "image_dark": "_static/logo.svg",
    },
    "repository_url": "https://github.com/mit-ll/Syndeo/",  # repo link
    "use_repository_button": True,
    "use_sidenotes": True,  # allow Edward Tufte style side-nodes
    # "footer_start": [
    #     "copyright",
    #     "sphinx-version",
    # ],
    # "footer_end": ["theme-version"],
}
