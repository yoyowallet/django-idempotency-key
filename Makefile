build: clean database

clean:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*,cover" -delete

database:
	psql -lqt | cut -d \| -f 1 | grep -wq idempotency-key || createdb idempotency-key
	./manage.py migrate

static_analysis: pep8 xenon

pep8:
	@echo "Running flake8 over codebase"
	flake8 --ignore=E501,W391,F999 --exclude=migrations idempotency-key/

xenon:
	@echo "Running xenon over codebase"
	xenon --max-absolute B --max-modules B --max-average A --exclude test_*.py idempotency-key/\

test: static_analysis coverage
	tox $(pytest_args)

coverage:
	py.test --cov=idempotency_key tests/ --cov-report html
	@echo Access the report here:
	@echo file://${PWD}/htmlcov/index.html

bundle: static_analysis coverage
	python setup.py sdist

release-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/django-idempotency-key-1.0.0.tar.gz

release: static_analysis coverage
	twine upload dist/*

bump-major:
	bump2version major

bump-minor:
	bump2version minor

bump-patch:
	bump2version patch

.PHONY: bump-major bump-minor bump-patch bundle clean coverage database pep8 release release-test static_analysis test virtualenv xenon