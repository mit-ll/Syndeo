from dataclasses import dataclass

import nox

from src.ci.utils import view_html


@dataclass
class config:
    """Nox creates a new virtual environment for each individual test.  Thus, it is important for to install all the packages needed for testing.  When using Nox, it will by default grab the current python version available in your environment and run testing with it."""

    # Pytest
    pytest_path_allure_html: str = "docs/source/_static/pytest-allure-html"
    pytest_path_allure_build: str = "docs/source/_static/pytest-allure-build"
    pytest_path_coverage: str = "docs/source/_static/pytest-coverage"
    pytest_path_summary: str = "docs/source/_static/pytest-summary"

    # Documentation
    sphinx_path: str = "docs/build/html"


@nox.session
def pytest(session: nox.Session):
    """Run PyTest coverage.

    Args:
        session (nox.Session): The current Nox session.
    """

    session.run("poetry", "install", "--with=dev", "--sync", "--no-root")
    session.run(
        "pytest",
        "--verbosity=3",
        # -------------- Coverage --------------
        "--cov-config=.nox/.coveragerc",
        "--cov=./",
        f"--cov-report=html:{config.pytest_path_coverage}",
        # -------------- Summary --------------
        f"--html={config.pytest_path_summary}/index.html",
        "--self-contained-html",
        # -------------- Allure --------------
        f"--alluredir={config.pytest_path_allure_build}",
        # -------------- Mem Ray --------------
        "--memray",
    )

    # Allure report generation
    try:
        session.run(
            "allure",
            "generate",
            "--single-file",
            "--clean",
            "--output",
            config.pytest_path_allure_html,
            config.pytest_path_allure_build,
            external=True,
        )
    except Exception:
        print("Allure report failed to generate, have you installed Allure via homebrew?")

    # Cleanup
    session.run("mv", ".coverage", config.pytest_path_coverage, external=True)


@nox.session
def sphinx(session: nox.Session):
    """Generate Sphinx documentation.

    Args:
        session (nox.Session): The current Nox session.
    """
    session.run("poetry", "install", "--with=dev", "--sync", "--no-root")

    # Build Sphinx
    session.run("sphinx-apidoc", "-o", "docs/source/pages/api/src", "src")
    session.run("sphinx-apidoc", "-o", "docs/source/pages/api/tests", "tests")
    session.chdir("docs")
    session.run("make", "clean", external=True)
    session.run("make", "html", external=True)
    session.chdir("../")


@nox.session
def show_pytest(session: nox.Session):
    """Show pytest coverage in HTML.

    Args:
        session (nox.Session): The current Nox session.
    """

    pytest(session)
    view_html(config.pytest_path_summary)
    view_html(config.pytest_path_coverage)
    view_html(config.pytest_path_allure_html)


@nox.session
def show_sphinx(session: nox.Session):
    """Show Sphinx in HTML.

    Args:
        session (nox.Session): The current Nox session.
    """

    sphinx(session)
    view_html(config.sphinx_path)


@nox.session
def build(session: nox.Session):
    """Build all artifacts.

    Args:
        session (nox.Session): The current Nox session.
    """

    # Build external docs
    sphinx(session)
