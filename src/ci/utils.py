import os
import webbrowser


def view_html(
    index_path: str,
    browser: str | None = None,
):
    """View an HTML file using the browser provided by the user.

    Args:
        index_path (str): Path to HTML index.  Usually this file is named index.html.
        browser (str | None, optional): Possible arguments include `Chrome`, `Firefox`, `Safari`.  If no browser is specified it will open using your system's default browser. Defaults to None.
    """

    # Open in a browser and view results
    cwd = os.getcwd()
    url = f"file://{cwd}/{index_path}/index.html"
    webbrowser.get(browser).open(url)
