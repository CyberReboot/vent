build: clean
	@echo
	@echo "checking dependencies"
	@echo
	env
	docker version
	pip -V
	pip install -r tests/requirements.txt
	python setup.py install

clean:
	rm -rf .cache
	rm -rf .coverage
	rm -rf .vent
	rm -rf vent.egg-info
	rm -rf vent.iso
	rm -rf dist
	rm -rf build
	rm -rf plugins
	rm -rf core
	pip uninstall -y vent || true

test: build
	py.test -v --cov=. -k 'not vendor' --cov-report term-missing

.PHONY: build test
