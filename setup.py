import os
from setuptools import find_packages
from setuptools import setup

setupDirectory = os.path.dirname(os.path.realpath(__file__))

requirements = []
with open(os.path.join(setupDirectory, 'requirements.txt'), 'r') as requirementsFile:
    for requirement in requirementsFile.read().splitlines():
        if requirement:
            requirements.append(requirement)

setup(
    name='kiba-build',
    version='0.1.4',
    description='Kiba Labs\' python building and testing utilities',
    url='https://github.com/kibalabs/build-py',
    packages=find_packages(exclude=['tests*']),
    python_requires='~=3.7',
    install_requires=requirements,
    tests_require=[],
    package_data={
        'buildpy': [
            'py.typed',
            'pylintrc',
            'mypy.ini',
        ]
    },
    include_package_data=True,
    test_suite='tests',
    extras_require={
    },
    entry_points='''
        [console_scripts]
        lint=buildpy.lint:run
        type-check=buildpy.type_check:run
        version=buildpy.version:run
    ''',
)
