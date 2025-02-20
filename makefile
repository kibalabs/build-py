install:
	@ pip install -r requirements.txt

list-outdated: install
	@ pip list -o

lint-check:
	@ lint-check --new *.py ./buildpy

lint-check-ci:
	@ lint-check --new *.py ./buildpy --output-file lint-check-results.json --output-format annotations

lint-fix:
	@ lint-check --new --fix *.py ./buildpy

type-check:
	@ type-check *.py ./buildpy

type-check-ci:
	@ type-check *.py ./buildpy --output-file type-check-results.json --output-format annotations

security-check:
	@ echo "Use lint-check"

security-check-ci:
	@ echo "Use lint-check-ci"

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
