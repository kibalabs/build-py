# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) with some additions:
- For all changes include one of [PATCH | MINOR | MAJOR] with the scope of the change being made.

## [Unreleased]

### Added
- [MINOR] Added `publish-dev`, which publishes a dev version (`X.Y.(Z+1).devN`, where N is the commits since the `vX.Y.Z` tag) with `uv build` and `uv publish`, and skips when the current version isn't tagged yet (a version bump waiting for its release) or when the tag is the current commit
- [MAJOR] Changed version script to use new library
- [MAJOR] Moved all config into pyproject.toml
- [MINOR] Added ruff linting (with --new flag)
- [MINOR] Added pytest running with test-check
- [MINOR] Remove pylint completely
- [MAJOR] Switch type checking to ty by default

### Changed
- [PATCH] Fixed version script appending a second dev part with bump-my-version 1.6.7

### Removed

## [0.1.10] - 2024-08-22

### Changed
- [MAJOR] Changed all commands to accept multiple paths and removed --directory input
- [MINOR] Updated dependencies

## [0.1.9] - 2023-08-22

### Changed
- [MINOR] Updated dependencies

## [0.1.8] - 2023-02-16

### Changed
- [MINOR] Update mypy to 1.0.0
- [PATCH] Fix for github annotations

## [0.1.7] - 2022-11-15

### Changed
- [MINOR] Update mypy config to avoid crash

## [0.1.6] - 2022-11-08

### Added
- [MINOR] Added bandit security checking

### Changed
- [MINOR] Improved parsing mypy results
- [MINOR] Allowed passing in custom config files for mypy and pylint

## [0.1.5] - 2022-07-19

### Changed
- [MINOR] Updated pylint to allow longer names

## [0.1.4] - 2022-01-26

### Added
- [MINOR] Added versioning command
- [MINOR] Added deploying pre-release on push to main

## [0.1.3] - 2021-08-18

### Changed
- [MINOR] Updated pylint config for binascii

## [0.1.2] - 2021-06-09

### Added
- [MINOR] Added deployment to pypi
- [MINOR] Added static files to setup.py

## [0.1.1] - 2021-05-18

### Added
- [MINOR] Added executable scripts

## [0.1.0] - 2021-05-17

### Added
- [MAJOR] Initial Commit
