install:
	@ pip install uv
	@ uv sync --all-extras

install-updates:
	@ pip install uv
	@ uv sync --upgrade --refresh --all-extras

list-outdated: install
	@ pip list -o

lint-check:
	@ uv run lint-check --new ./buildpy

lint-check-ci:
	@ uv run lint-check --new ./buildpy --output-file lint-check-results.json --output-format annotations

lint-fix:
	@ uv run isort --sl -l 1000 ./buildpy
	@ uv run lint-check --new ./buildpy

type-check:
	@ uv run type-check ./buildpy

type-check-ci:
	@ uv run type-check ./buildpy --output-file type-check-results.json --output-format annotations

security-check:
	@ echo "Use lint-check"

security-check-ci:
	@ echo "Use lint-check-ci"

build:
	@ uv build

start:
	@ echo "Not Supported"

start-prod:
	@ echo "Not Supported"

test:
	@ echo "Not Supported"

test-ci:
	@ echo "Not Supported"

clean:
	@ rm -rf ./.mypy_cache ./__pycache__ ./build ./dist

publish: build
	@ uv publish

GIT_LAST_TAG=$(shell git describe --tags --abbrev=0)
GIT_COUNT=$(shell git rev-list $(GIT_LAST_TAG)..HEAD --count)
publish-dev:
	@ uv run buildpy/version.py --part dev --count $(GIT_COUNT)
	@ uv build
	@ uv publish

.PHONY: *
