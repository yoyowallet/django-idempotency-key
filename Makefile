.PHONY: build
build: clean database

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

.PHONY: test
test: coverage
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
	poetry run twine upload --repository-url https://test.pypi.org/legacy/dist/django_idempotency_key-1.3.0.tar.gz

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
