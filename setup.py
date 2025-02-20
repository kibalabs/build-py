import os

from setuptools import find_packages  # type: ignore[import-untyped]
from setuptools import setup

SETUP_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

REQUIREMENTS = []
with open(os.path.join(SETUP_DIRECTORY, 'requirements.txt'), 'r') as REQUIREMENTS_FILE:
    for requirement in REQUIREMENTS_FILE.read().splitlines():
        if requirement:
            REQUIREMENTS.append(requirement)

setup(
    name='kiba-build',
    version='0.1.10',
    description='Kiba Labs\' python building and testing utilities',
    url='https://github.com/kibalabs/build-py',
    packages=find_packages(exclude=['tests*']),
    python_requires='~=3.7',
    install_requires=REQUIREMENTS,
    tests_require=[],
    package_data={
        'buildpy': [
            'py.typed',
            'pyproject.toml',
        ]
    },
    include_package_data=True,
    test_suite='tests',
    extras_require={
    },
    entry_points='''
        [console_scripts]
        lint-check=buildpy.lint_check:run
        type-check=buildpy.type_check:run
        security-check=buildpy.security_check:run
        version=buildpy.version:run
    ''',
)
