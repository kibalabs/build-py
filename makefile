install:
	@ pip install -r requirements.txt

list-outdated: install
	@ pip list -o

lint-check:
	@ lint --directory ./buildpy

lint-check-ci:
	@ lint --directory ./buildpy --output-file lint-check-results.json --output-format annotations

lint-fix:
	@ isort --sl -l 1000 ./buildpy
	@ lint --directory ./buildpy

type-check:
	@ type-check --directory ./buildpy

type-check-ci:
	@ type-check --directory ./buildpy --output-file type-check-results.json --output-format annotations

security-check:
	@ security-check --directory ./buildpy

security-check-ci:
	@ security-check --directory ./buildpy --output-file security-check-results.json --output-format annotations

build:
	@ echo "Not Supported"

start:
	@ echo "Not Supported"

start-prod:
	@ echo "Not Supported"

test:
	@ echo "Not Supported"

clean:
	@ rm -rf ./.mypy_cache ./__pycache__ ./build ./dist

.PHONY: *
