install:
	@ pip install uv
	@ uv sync --all-extras

install-updates:
	@ pip install uv
	@ uv sync --refresh --all-extras

list-outdated: install
	@ pip list -o

lint-check:
	@ uv run lint-check ./buildpy

lint-check-ci:
	@ uv run lint-check ./buildpy --output-file lint-check-results.json --output-format annotations

lint-fix:
	@ uv run isort --sl -l 1000 ./buildpy
	@ uv run lint-check ./buildpy

type-check:
	@ uv run type-check ./buildpy

type-check-ci:
	@ uv run type-check ./buildpy --output-file type-check-results.json --output-format annotations

security-check:
	@ uv run security-check ./buildpy

security-check-ci:
	@ uv run security-check ./buildpy --output-file security-check-results.json --output-format annotations

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

GIT_LAST_TAG=$(shell git describe --tags --abbrev=0)
GIT_COUNT=$(shell git rev-list $(GIT_LAST_TAG)..HEAD --count)
publish-dev:
	@ uv run buildpy/version.py --part dev --count $(GIT_COUNT)
	@ uv build
	@ uv publish

.PHONY: *
