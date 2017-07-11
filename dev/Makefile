build: depends
	@echo
	@echo "checking dependencies"
	@echo
	rm -rf vent.iso
	docker build -t vent .
	docker run --rm vent > vent.iso
	rm -rf vendor/tinycore-python2/python2.tar

clean:
	find . -name "*.pyc" -type f -delete
	find . -name "*.tar" -type f -delete
	rm -rf vent.iso

test:
	@echo
	@echo "checking dependencies"
	@echo
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

depends: clean
	@echo
	@echo "checking dependencies"
	@echo
	docker -v
	./scripts/build.sh
.PHONY: build clean depends test
