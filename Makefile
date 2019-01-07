build: clean

clean:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*,cover" -delete

static_analysis: pep8 xenon

pep8:
	@echo "Running flake8 over codebase"
	flake8 --ignore=E501,W391,F999 --exclude=migrations idempotency-key/

xenon:
	@echo "Running xenon over codebase"
	xenon --max-absolute B --max-modules B --max-average A --exclude test_*.py idempotency-key/\

coverage:
	py.test --cov=idempotency-key tests/

bundle:
	python setup.py sdist

.PHONY: bundle clean coverage database pep8 release release-test static_analysis test virtualenv xenon