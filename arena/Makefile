.PHONY: all build clean

ember = node_modules/ember-cli/bin/ember
bower = node_modules/bower/bin/bower

js_files = $(shell find app config -name "*.js" -o -name "*.hbs")

all: build

node_modules $(ember) $(bower): package.json
	npm install .
	touch $@

vendor: bower.json $(bower)
	$(bower) install --config.interactive=false
	touch $@

test: $(ember) vendor
	$(ember) test

build: dist

dist: $(js_files) node_modules vendor
	$(ember) build --environment=production
	touch $@

clean:
	rm -rf dist tmp/*

clean_all: clean
	rm -rf node_modules/* vendor/* vendor/.done
