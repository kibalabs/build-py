install:
	@ pip install uv
	@ uv sync

install-updates:
	@ pip install uv
	@ uv sync

list-outdated: install
	@ pip list -o

lint-check:
	@ lint-check ./buildpy

lint-check-ci:
	@ lint-check ./buildpy --output-file lint-check-results.json --output-format annotations

lint-fix:
	@ isort --sl -l 1000 ./buildpy
	@ lint-check ./buildpy

type-check:
	@ type-check ./buildpy

type-check-ci:
	@ type-check ./buildpy --output-file type-check-results.json --output-format annotations

security-check:
	@ security-check ./buildpy

security-check-ci:
	@ security-check ./buildpy --output-file security-check-results.json --output-format annotations

build:
	@ uv build

start:
	@ echo "Not Supported"

start-prod:
	@ echo "Not Supported"

test:
	@ echo "Not Supported"

clean:
	@ rm -rf ./.mypy_cache ./__pycache__ ./build ./dist

publish: build
	@ uv publish

GIT_COUNT=$(shell git rev-list $(git describe --tags --abbrev=0)..HEAD --count)
# publish-dev: build
publish-dev:
	echo $(GIT_COUNT)
	uv run buildpy/version.py --part dev --count $(GIT_COUNT)
# @ uv publish

.PHONY: *
