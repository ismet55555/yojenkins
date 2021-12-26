# Sphinx Documentation

## Installation

1. Install sphinx itself
    - `pip install sphinx`

2. Set up basic docs file structure
    - `sphinx-quickstart`

4. Install Markdown Parser (Default is RestructuredText)
    - Learn More: https://www.sphinx-doc.org/en/master/usage/markdown.html
    - `pip install --upgrade myst-parser`
    - Add parser to `conf.py`:
        ```
        extensions = ['myst_parser']
        ```

## Setup

1. Select and install sphinx theme:
    - [Sphinx Themes Gallery](https://sphinx-themes.org/)
    - Read the Docs Theme: `pip install sphinx-rtd-theme`
    - Add theme name to `conf.py`:
        ```
        html_theme = 'sphinx_rtd_theme'
        ```

2. TODO

## Compile

1. Compile the docs:
    - Linux / MacOS: `make html`
    - Windows: `./make.bat html`


## Hosting

- GitHub: https://www.docslikecode.com/articles/github-pages-python-sphinx/
- Read the Docs: https://readthedocs.org/
