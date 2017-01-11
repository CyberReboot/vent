test:
	@echo
	@echo "checking dependencies"
	@echo
	pip -V
	pip install -r tests/requirements.txt
	py.test -v --cov=. -k 'not vendor' --cov-report term-missing
