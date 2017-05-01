test:
	@echo
	@echo "checking dependencies"
	@echo
	docker version
	pip -V
	pip install -r tests/requirements.txt
	rm -rf .cache
	rm -rf .coverage
	rm -rf .vent
	rm -rf vent.egg-info
	rm -rf vent.iso
	rm -rf dist
	rm -rf build
	rm -rf plugins
	rm -rf core
	py.test -v --cov=. -k 'not vendor' --cov-report term-missing
.PHONY: test
