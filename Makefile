.PHONY: all test clean clean_all pytest embertest

WORKON_HOME ?= env
VIRTUAL_ENV ?= $(WORKON_HOME)/munerator

pyenv = $(VIRTUAL_ENV)

pip = $(pyenv)/bin/pip
pytest = $(pyenv)/bin/py.test
sphinx = $(pyenv)/bin/sphinx

pyapp = $(pyenv)/bin/munerator

all: munerator/static $(pyapp)

# environment

$(pip):
	virtualenv -q $(pyenv)

requirements_dev.txt.done: $(pip) requirements_dev.txt
	pip install -r requirements_dev.txt
	touch $@

$(pytest): requirements_dev.txt.done

$(pyapp): $(pip) setup.py
	pip install -e .

$(sphinx): $(pip)
	pip install -r docs/requirements.txt

arena/.done: 
	cd arena; make
	touch $@

# testing

pytest: $(pytest) $(pyapp)
	$(pytest) --pep8 --flakes --cov munerator munerator tests $(args)

jstest:
	cd arena; make test

test: jstest pytest

install: $(pip) setup.py munerator/static
	pip install .

# building/dist

munerator/static:
	rm -r $@ || true
	mkdir -p $@
	cd arena; make build
	cp -R arena/dist/* $@

wheel: munerator/static setup.py
	python setup.py -v bdist_wheel

upload: clean test munerator/static setup.py
	python setup.py sdist upload

docs/_build: $(sphinx) $(pyapp)
	cd docs; make html

livehtml: $(sphinx)
	(sleep 1; open http://localhost:8000) &
	cd docs; make livehtml

clean:
	rm -rf arena/dist munerator/static dist build *.egg-info
	rm -rf $(pyenv)/lib/*/site-packages/munerator* $(pyenv)/bin/munerator
	rm -rf docs/_build

clean_pyenv:
	rm -rf $(pyenv) requirements_dev.txt.done

clean_all: clean clean_pyenv
	rm -rf arena/node_modules/ arena/vendor/*
