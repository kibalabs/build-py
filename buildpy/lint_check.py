import json
import os
import subprocess
from typing import Any

import click

from buildpy.util import GitHubAnnotationsReporter
from buildpy.util import Message
from buildpy.util import MessageParser
from buildpy.util import PrettyReporter


class RuffMessageParser(MessageParser):
    def parse_json_messages(self, rawMessages: list[dict[str, Any]]) -> list[Message]:  # type: ignore[explicit-any]
        output: list[Message] = [
            Message(
                path=rawMessage['filename'],
                line=rawMessage['location']['row'],
                column=rawMessage['location']['column'],
                code=rawMessage['code'],
                text=rawMessage['message'],
                level='error',
            )
            for rawMessage in rawMessages
        ]
        return output


@click.command()
@click.argument('targets', nargs=-1)
@click.option('-o', '--output-file', 'outputFilename', required=False, type=str)
@click.option('-f', '--output-format', 'outputFormat', required=False, type=str, default='pretty')
@click.option('-c', '--config-file-path', 'configFilePath', required=False, type=str)
@click.option('-x', '--fix', 'shouldFix', default=False, is_flag=True)
def run(targets: list[str], outputFilename: str, outputFormat: str, configFilePath: str, shouldFix: bool) -> None:
    currentDirectory = os.path.dirname(os.path.realpath(__file__))
    configFilePath = configFilePath or f'{currentDirectory}/pyproject.toml'
    messages: list[Message] = []
    rawMessages = []
    command = f'ruff check --output-format json --config {configFilePath} {"--fix" if shouldFix else ""} {" ".join(targets)}'
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)  # noqa: S602
    except subprocess.CalledProcessError as exception:
        output = exception.output.decode()
        cleanedOutput = '\n'.join([line for line in output.split('\n') if not line.startswith('warning:')])
        rawMessages = json.loads(cleanedOutput)
    ruffMessageParser = RuffMessageParser()
    messages += ruffMessageParser.parse_json_messages(rawMessages=rawMessages)
    command2 = f'ruff format {"--check" if not shouldFix else ""} --config {configFilePath} {" ".join(targets)}'
    try:
        subprocess.check_output(command2, stderr=subprocess.STDOUT, shell=True)  # noqa: S602
    except subprocess.CalledProcessError as exception:
        for line in exception.output.decode().split('\n'):
            if line.startswith('Would reformat: '):
                filePath = line.replace('Would reformat: ', '', 1)
                messages.append(
                    Message(
                        path=filePath,
                        line=0,
                        column=0,
                        code='format',
                        text='File needs to be formatted',
                        level='error',
                    ),
                )
    reporter = GitHubAnnotationsReporter() if outputFormat == 'annotations' else PrettyReporter()
    output = reporter.create_output(messages=messages)
    if outputFilename:
        with open(outputFilename, 'w') as outputFile:
            outputFile.write(output)
    else:
        print(output)  # noqa: T201


if __name__ == '__main__':
    run()
