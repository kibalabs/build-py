import subprocess
import tempfile
import tomllib

import click


def generate_command(part: str, configFilePath: str) -> str:
    with open('pyproject.toml') as file:
        pyproject = tomllib.loads(file.read())
    currentVersion = pyproject['project']['version']
    # NOTE(krishan711): only replace the version line, otherwise pins containing the version string (e.g. 0.1.1 inside ==0.1.11.dev23) get rewritten too
    return f"bump-my-version bump --config-file \"{configFilePath}\" --allow-dirty --current-version \"{currentVersion}\" --search 'version = \"{{current_version}}\"' --replace 'version = \"{{new_version}}\"' --parse '(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)(\\.dev(?P<dev>\\d+))?' --serialize '{{major}}.{{minor}}.{{patch}}.dev{{dev}}' --serialize '{{major}}.{{minor}}.{{patch}}' {part} pyproject.toml"


def bump_version(part: str, count: int) -> None:
    if count == 0:
        print('No version bump required')  # noqa: T201
        return
    # NOTE(krishan711): an empty config file stops bump-my-version (>=1.6.7) also updating project.version in pyproject.toml with its default parse, which appends a second dev part
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml') as configFile:
        configFile.write('[tool.bumpversion]\n')
        configFile.flush()
        # NOTE(krishan711): for dev releases bump the patch first
        if part == 'dev':
            subprocess.check_output(generate_command(part='patch', configFilePath=configFile.name), stderr=subprocess.STDOUT, shell=True)  # noqa: S602
        for _ in range(count):
            subprocess.check_output(generate_command(part=part, configFilePath=configFile.name), stderr=subprocess.STDOUT, shell=True)  # noqa: S602


@click.command()
@click.option('-p', '--part', 'part', required=True, type=str)
@click.option('-c', '--count', 'count', required=False, type=int, default=1)
def run(part: str, count: int) -> None:
    bump_version(part=part, count=count)


if __name__ == '__main__':
    run()
