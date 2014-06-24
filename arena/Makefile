.PHONY: all build clean

ember = node_modules/ember-cli/bin/ember
bower = node_modules/bower/bin/bower

all: build

$(ember): package.json
	npm install .

vendor/.done: bower.json
	$(bower) install --config.interactive=false
	touch $@

test: $(ember) vendor/.done
	$(ember) test

build: dist

dist: app/*.js app/*/*.js config/environment.js $(ember) vendor/.done
	$(ember) build --environment=production

clean:
	rm -rf node_modules/* vendor/*
