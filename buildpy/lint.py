import os
import json
import subprocess
import re
from typing import List, Any, Dict

import click
from pylint.lint import Run as run_pylint  # type: ignore[import]
from pylint.reporters import CollectingReporter  # type: ignore[import]

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

    def parse_messages(self, rawMessages: List[str]) -> List[Message]:
        raise NotImplementedError

    def get_messages(self) -> List[Message]:
        output: List[Message] = []
        for rawMessage in self.messages:
            output.append(Message(
                path=os.path.relpath(rawMessage.abspath),
                line=rawMessage.line,
                column=rawMessage.column + 1,
                code=rawMessage.symbol,
                text=rawMessage.msg.strip() or '',
                level=self._get_error_level(pylintLevel=rawMessage.category),
            ))
        return output


class RuffMessageParser(MessageParser):

    def parse_json_messages(self, rawMessages: List[Dict[str, Any]]) -> List[Message]:
        output: List[Message] = []
        for rawMessage in rawMessages:
            output.append(Message(
                path=rawMessage['filename'],
                line=rawMessage['location']['row'],
                column=rawMessage['location']['column'],
                code=rawMessage['code'],
                text=rawMessage['message'],
                level='error',
            ))
        return output


@click.command()
@click.option('-d', '--directory', 'directory', required=False, type=str)
@click.option('-o', '--output-file', 'outputFilename', required=False, type=str)
@click.option('-f', '--output-format', 'outputFormat', required=False, type=str, default='pretty')
@click.option('-c', '--config-file-path', 'configFilePath', required=False, type=str)
@click.option('-n', '--new', 'shouldUseNewVersion', default=False, is_flag=True)
@click.option('-x', '--fix', 'shouldFix', default=False, is_flag=True)
def run(directory: str, outputFilename: str, outputFormat: str, configFilePath: str, shouldUseNewVersion: bool, shouldFix: bool) -> None:
    currentDirectory = os.path.dirname(os.path.realpath(__file__))
    targetDirectory = os.path.abspath(directory or os.getcwd())
    if shouldUseNewVersion:
        # NOTE(krishan711): track ruff called from python: https://github.com/charliermarsh/ruff/issues/659
        # NOTE(krishan711): track ruff pylint coverage: https://github.com/charliermarsh/ruff/issues/970
        # NOTE(krishan711): track ruff bandit coverage: https://github.com/charliermarsh/ruff/issues/1646
        ruffConfigFilePath = configFilePath or f'{currentDirectory}/ruff.toml'
        rawMessages = []
        try:
            subprocess.check_output(f'ruff check --format json --config {ruffConfigFilePath} {"--fix" if shouldFix else ""} {targetDirectory}', stderr=subprocess.STDOUT, shell=True)  # nosec=subprocess_popen_with_shell_equals_true
        except subprocess.CalledProcessError as exception:
            rawMessages = json.loads(exception.output.decode())
        messageParser = RuffMessageParser()
        messages = messageParser.parse_json_messages(rawMessages=rawMessages)
    else:
        pylintConfigFilePath = configFilePath or f'{currentDirectory}/pylintrc'
        messageParser = PylintMessageParser()
        run_pylint([f'--rcfile={pylintConfigFilePath}', f'--jobs=0', targetDirectory], reporter=messageParser, exit=False)
        messages = messageParser.get_messages()
    reporter = GitHubAnnotationsReporter() if outputFormat == 'annotations' else PrettyReporter()
    output = reporter.create_output(messages=messages)
    if outputFilename:
        with open(outputFilename, 'w') as outputFile:
            outputFile.write(output)
    else:
        print(output)

if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
