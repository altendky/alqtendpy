$PYTHON --version
$PYTHON -m pip --version
$PYTHON -m pip install -q --user --ignore-installed --upgrade virtualenv
$PYTHON -m virtualenv -p $PYTHON venv
venv/bin/python --version
venv/bin/python -m pip install -r requirements.test
venv/bin/python -m pip freeze
