# Nox

Nox is the spiritual successor to Tox for running scripts in controlled environments.

* **pytest**: tests the code
* **sphinx**: advance documentation software

The `noxfile.py` provides an example of how to run each of these:

```bash
nox --list              # lists out all the available sessions
nox -rs pytest          # run pytests
nox -rs show_sphinx     # view HTML of sphinx
nox -rs build           # build pytest & documentation
```


For an explanation on how to properly setup multiple versions of Python to run with Nox see [**here**](https://sethmlarson.dev/nox-pyenv-all-python-versions).
