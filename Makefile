.PHONY: help
help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  build           	  cleans the environment and runs the migrations on the database"
	@echo "  deps                 to install dependencies for local development"
	@echo "  clean                to clean up environment"
	@echo "  lint                 runs linting on all the files using Ruff"
	@echo "  database             Creates the idempotency-key database and runs the migrations"
	@echo "  tests                to run tests"
	@echo "  coverage             to run code coverage"
	@echo "  bundle               Generates a zip file of the pacakge so we can later upload to PyPi"
	@echo "  release_test         Pushes the bundle to test.pypi.org to prove it works and the contents are correct"
	@echo "  release              Pushes the bundle to pypi.org for a proper release"
	@echo "  bump-major           bumps the major version number in respective files so that we can generate a bundle for that version and release it."
	@echo "  bump-minor           bumps the minor version number."
	@echo "  bump-revision        bumps the revision version number."
	@echo "  install-poetry       installs the correct version poetry"
	@echo "  uninstall-poetry     uninstalls poetry if things go wrong."
	@echo "  tree                 Produces and ASCII directory tree to provide AI bots with context of the project."
	@echo "  showoutdatedpackages Ask poetry for a list of top-level packages that can be updated."

.PHONY: build
build: clean deps database

.PHONY: deps
deps:
	poetry env remove 3.9
	poetry env use 3.9
	poetry install

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: clean
clean:
	rm -rf .tox/ .pytest_cache/ dist/ htmlcov/ .coverage coverage.xml db.sqlite3
	find . -type f -name "*.pyc" -delete

.PHONY: database
database:
	psql -lqt | cut -d \| -f 1 | grep -wq idempotency-key || createdb idempotency-key
	poetry run ./manage.py migrate

.PHONY: tests
tests: coverage
	# ensure that `docker compose up` is running to start the redis server before
	# running these tests.
	poetry run tox $(pytest_args)

.PHONY: coverage
coverage: lint
	poetry run py.test --cov=idempotency_key tests/ --cov-report html
	@echo Access the report here:
	@echo file://${PWD}/htmlcov/index.html

.PHONY: bundle
bundle: coverage
	rm -r ./dist/ || true
	poetry build

.PHONY: release-test
release-test:
	poetry run twine upload --repository-url https://test.pypi.org/legacy/dist/django_idempotency_key-1.4.0.tar.gz

.PHONY: release
release: coverage
	poetry run twine upload dist/*

.PHONY: bump-major
bump-major:
	poetry run bump2version major

.PHONY: bump-minor
bump-minor:
	poetry run bump2version minor

.PHONY: bump-patch
bump-patch:
	poetry run bump2version patch

.PHONY: install-poetry
install-poetry:
	curl -sSL https://install.python-poetry.org | python3 -

.PHONY: uninstall-poetry
uninstall-poetry:
	curl -sSL https://install.python-poetry.org | python3 - --uninstall

.PHONY: tree
tree:
	tree -I __pycache__ -I *.pyc 2>/dev/null

.PHONY: showoutdatedpackages
showoutdatedpackages:
	poetry show --outdated -T
