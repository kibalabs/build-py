import subprocess
import tomllib

import click

from buildpy.version import bump_version


@click.command()
def run() -> None:
    with open('pyproject.toml', 'rb') as file:
        version = tomllib.load(file)['project']['version']
    tag = f'v{version}'
    # NOTE(krishan711): a version bump is merged before the release workflow tags it, so dev versions only publish once the current version is tagged
    if subprocess.run(['git', 'rev-parse', '--quiet', '--verify', f'refs/tags/{tag}'], capture_output=True, check=False).returncode != 0:  # noqa: S603, S607
        print(f'{tag} is not tagged yet, so this commit is a pending release: not publishing a dev version')  # noqa: T201
        return
    count = int(subprocess.check_output(['git', 'rev-list', '--count', f'{tag}..HEAD'], text=True).strip())  # noqa: S603, S607
    if count == 0:
        print(f'{tag} is this commit, so the release publishes it: not publishing a dev version')  # noqa: T201
        return
    bump_version(part='dev', count=count)
    subprocess.check_call(['uv', 'build'])  # noqa: S607
    subprocess.check_call(['uv', 'publish'])  # noqa: S607


if __name__ == '__main__':
    run()
