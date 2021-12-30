# Dev How To

- Install [direnv](https://direnv.net/docs/installation.html) and make sure path to python and pip bin folders are present in the `PATH` env var
  - on MacOS (with Python 3.9 already installed with `brew install python@3.9`):

  ```console
  brew install direnv
  cd pandemia-covid-streamlit
  echo export PATH="/usr/local/opt/python@3.9/libexec/bin:$PATH" > .envrc
  ```

- Install [pipenv](https://pipenv.pypa.io/en/latest/), activate the environment and install [streamlit](https://docs.streamlit.io/library/get-started/installation):

  ```console
  pip install pipenv
  pipenv shell
  pipenv install streamlit
  ```

- Run the app:

  ```console
  streamlit run streamlit_app.py
  ```

:bulb: To install dependencies from Pipfile.lock, run `pipenv shell` and then `pipenv sync`.

:bulb: In Visual Studio Code, to use the correct python interpreter, run the `>Python: Select Interpreter` VS Code command (`Cmd+Shift+P` on MacOS) and select the one in your virtual environment.
To find out which one needs to be selected, run `pipenv shell` in the terminal and then `which python`.
