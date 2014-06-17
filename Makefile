.PHONY: all test clean pytest embertest

WORKON_HOME ?= env

pyenv = $(WORKON_HOME)/munerator

pip = $(pyenv)/bin/pip
ember = /usr/local/share/npm/bin/ember
pytest = $(pyenv)/bin/py.test
sphinx = $(pyenv)/bin/sphinx

pyapp = $(pyenv)/bin/munerator

all: munerator/static $(pyapp)

# environment

$(pip):
	virtualenv -q $(pyenv)

$(ember):
	npm install -g ember-cli

$(pytest): $(pip)
	pip install -r requirements_dev.txt

$(pyapp): $(pip) setup.py
	pip install -e .

$(sphinx): $(pip)
	pip install -r docs/requirements.txt

# testing

pytest: $(pytest) $(pyapp)
	$(pytest) --pep8 --flakes --cov munerator munerator tests

embertest: $(ember)
	cd arena; $(ember) test

test: embertest pytest

# building/dist

munerator/static: $(ember) arena/app/*/*.js arena/config/environment.js
	cd arena; $(ember) build
	ln -sF ../arena/dist/ munerator/static

wheel: munerator/static setup.py
	python setup.py -v bdist_wheel

docs/_build: $(sphinx) $(pyapp)
	cd docs; make html

docs: docs/_build

clean:
	rm -rf arena/dist munerator/static dist build *.egg-info
	rm -rf $(pyenv)/lib/*/site-packages/munerator* $(pyenv)/bin/munerator
	rm -rf docs/_build
