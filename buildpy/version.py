import subprocess

import click


def generate_command(part: str) -> str:
    return f"bump2version --allow-dirty --current-version \"$(python setup.py --version)\" --parse '(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)(\\.dev(?P<dev>\\d+))?' --serialize '{{major}}.{{minor}}.{{patch}}.dev{{dev}}' --serialize '{{major}}.{{minor}}.{{patch}}' {part} setup.py"

@click.command()
@click.option('-p', '--part', 'part', required=True, type=str)
@click.option('-c', '--count', 'count', required=False, type=int, default=1)
def run(part: str, count: int) -> None:
    # NOTE(krishan711): for dev releases bump the patch first
    if part == 'dev':
        subprocess.check_output(generate_command(part='patch'), stderr=subprocess.STDOUT, shell=True)  # nosec=subprocess_popen_with_shell_equals_true
    for _ in range(count):
        subprocess.check_output(generate_command(part=part), stderr=subprocess.STDOUT, shell=True)  # nosec=subprocess_popen_with_shell_equals_true

if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
