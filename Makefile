build: depends
	@echo
	@echo "checking dependencies"
	@echo
	rm -rf vent.iso
	docker build -t vent .
	docker run --rm vent > vent.iso
	rm -rf vendor/tinycore-python2/python2.tar
	rm -rf vent/core/management/vent-management.tar

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
	pip uninstall -y vent
	pip install .
	py.test -v --cov=. -k 'not vendor' --cov-report term-missing

depends: clean
	@echo
	@echo "checking dependencies"
	@echo
	docker -v
	./scripts/build.sh
.PHONY: build clean depends test
