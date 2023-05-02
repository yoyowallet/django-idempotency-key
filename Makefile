build: clean database

clean:
	rm -rf .tox/ .pytest_cache/ dist/ htmlcov/ .coverage coverage.xml db.sqlite3
	find . -type f -name "*.pyc" -delete

database:
	psql -lqt | cut -d \| -f 1 | grep -wq idempotency-key || createdb idempotency-key
	poetry run ./manage.py migrate

static_analysis: pep8 xenon black

black:
	@echo "Running black over codebase"
	black .

pep8:
	@echo "Running flake8 over codebase"
	flake8 --ignore=E501,W391,F999 --exclude=migrations idempotency_key/

xenon:
	@echo "Running xenon over codebase"
	poetry run xenon --max-absolute C --max-modules B --max-average A --exclude test_*.py idempotency_key/

test: static_analysis coverage
	poetry run tox $(pytest_args)

coverage:
	poetry run py.test --cov=idempotency_key tests/ --cov-report html
	@echo Access the report here:
	@echo file://${PWD}/htmlcov/index.html

bundle: static_analysis coverage
	rm -r ./dist/ || true
	poetry build

release-test:
	poetry run twine upload --repository-url https://test.pypi.org/legacy/ dist/django_idempotency_key-1.3.0.tar.gz

release: static_analysis coverage
	poetry run twine upload dist/*

bump-major:
	poetry run bump2version major

bump-minor:
	poetry run bump2version minor

bump-patch:
	poetry run bump2version patch

.PHONY: install-poetry
install-poetry:
	curl -sSL https://install.python-poetry.org | python3 -

.PHONY: uninstall-poetry
uninstall-poetry:
	curl -sSL https://install.python-poetry.org | python3 - --uninstall

.PHONY: bump-major bump-minor bump-patch bundle clean coverage database pep8 black
.PHONY: release release-test static_analysis test virtualenv xenon
.PHONY: install-poetry uninstall-poetry
