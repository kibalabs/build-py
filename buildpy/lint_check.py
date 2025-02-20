import json
import os
import subprocess
from typing import Any

import click
from pylint.lint import Run as run_pylint  # noqa: N813
from pylint.reporters import CollectingReporter

from buildpy.util import GitHubAnnotationsReporter
from buildpy.util import Message
from buildpy.util import MessageParser
from buildpy.util import PrettyReporter


class PylintMessageParser(CollectingReporter, MessageParser):
    @staticmethod
    def _get_error_level(pylintLevel: str) -> str:
        pylintLevel = pylintLevel.lower()
        if pylintLevel == 'info':
            return 'notice'
        if pylintLevel == 'warning':
            return 'warning'
        return 'error'

    def parse_messages(self, rawMessages: list[str]) -> list[Message]:
        raise NotImplementedError

    def get_messages(self) -> list[Message]:
        output: list[Message] = [
            Message(
                path=os.path.relpath(rawMessage.abspath),
                line=rawMessage.line,
                column=rawMessage.column + 1,
                code=rawMessage.symbol,
                text=rawMessage.msg.strip() or '',
                level=self._get_error_level(pylintLevel=rawMessage.category),
            )
            for rawMessage in self.messages
        ]
        return output


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
@click.option('-n', '--new', 'shouldUseNewVersion', default=False, is_flag=True)
@click.option('-x', '--fix', 'shouldFix', default=False, is_flag=True)
def run(targets: list[str], outputFilename: str, outputFormat: str, configFilePath: str, shouldUseNewVersion: bool, shouldFix: bool) -> None:
    currentDirectory = os.path.dirname(os.path.realpath(__file__))
    configFilePath = configFilePath or f'{currentDirectory}/pyproject.toml'
    messages: list[Message] = []
    if shouldUseNewVersion:
        # NOTE(krishan711): track ruff called from python: https://github.com/charliermarsh/ruff/issues/659
        # NOTE(krishan711): track ruff pylint coverage: https://github.com/charliermarsh/ruff/issues/970
        rawMessages = []
        command = f'ruff check --output-format json --config {configFilePath} {"--fix" if shouldFix else ""} {" ".join(targets)}'
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)  # noqa: S602
        except subprocess.CalledProcessError as exception:
            rawMessages = json.loads(exception.output.decode())
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
    else:
        pylintMessageParser = PylintMessageParser()
        run_pylint([f'--rcfile={configFilePath}', '--jobs=0', *targets], reporter=pylintMessageParser, exit=False)
        messages += pylintMessageParser.get_messages()
    reporter = GitHubAnnotationsReporter() if outputFormat == 'annotations' else PrettyReporter()
    output = reporter.create_output(messages=messages)
    if outputFilename:
        with open(outputFilename, 'w') as outputFile:
            outputFile.write(output)
    else:
        print(output)  # noqa: T201


if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
