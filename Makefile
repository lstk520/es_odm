# system python interpreter. used only to create virtual environment
PY = python
VENV = ./venv
BIN = $(VENV)/bin
PACKAGE_NAME = es_odm


# colors
BLACK = "\033[30;1m"
RED  =  "\033[31;1m"
GREEN = "\033[32;1m"
YELLOW = "\033[33;1m"
BLUE  = "\033[34;1m"
PURPLE = "\033[35;1m"
CYAN  = "\033[36;1m"
WHITE = "\033[37;1m"
COLOR_END = "\033[0m"


# make it work on windows too
ifeq ($(OS), Windows_NT)
    BIN=$(VENV)/Scripts
    PY=python
endif


.PHONY: build
build: $(VENV)
	# delete dist dir > build package > delete build and egg-info dir
	rm -rf dist && \
	$(BIN)/$(PY) setup.py sdist bdist_wheel && \
	rm -rf build && rm -rf $(PACKAGE_NAME).egg-info
	echo -e $(YELLOW)"build $(PACKAGE_NAME) package done!"$(COLOR_END)


# push package to pypi
.PHONY: push
push: $(VENV)
	rm -rf dist && \
	$(BIN)/$(PY) setup.py sdist bdist_wheel && \
	twine upload dist/* -r pypi && \
	rm -rf build && rm -rf $(PACKAGE_NAME).egg-info && \
	echo -e $(YELLOW)"push $(PACKAGE_NAME) package to pypi done!"$(COLOR_END)


# release to pypi，auto incr version
.PHONY: release
release: $(VENV)
	rm -rf dist && \
	$(BIN)/$(PY) version_inc.py && \
	$(BIN)/$(PY) setup.py sdist bdist_wheel && \
	twine upload dist/* -r pypi && \
	rm -rf build && rm -rf $(PACKAGE_NAME).egg-info && \
	echo -e $(YELLOW)"release $(PACKAGE_NAME) done!"$(COLOR_END)


.PHONY: clean
clean: $(VENV)
	rm -rf build && rm -rf $(PACKAGE_NAME).egg-info && \
	echo -e $(YELLOW)"clean done!"$(COLOR_END)


# clean:
#     rm -rf $(VENV)
#     find . -type f -name *.pyc -delete
#     find . -type d -name __pycache__ -delete
