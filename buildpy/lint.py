import os
from typing import List

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


@click.command()
@click.option('-d', '--directory', 'directory', required=False, type=str)
@click.option('-o', '--output-file', 'outputFilename', required=False, type=str)
@click.option('-f', '--output-format', 'outputFormat', required=False, type=str, default='pretty')
@click.option('-c', '--config-file-path', 'configFilePath', required=False, type=str)
def run(directory: str, outputFilename: str, outputFormat: str, configFilePath: str) -> None:
    currentDirectory = os.path.dirname(os.path.realpath(__file__))
    targetDirectory = os.path.abspath(directory or os.getcwd())
    pylintConfigFilePath = configFilePath or f'{currentDirectory}/pylintrc'
    pylintMessageParser = PylintMessageParser()
    run_pylint([f'--rcfile={pylintConfigFilePath}', targetDirectory], reporter=pylintMessageParser, exit=False)
    reporter = GitHubAnnotationsReporter() if outputFormat == 'annotations' else PrettyReporter()
    output = reporter.create_output(messages=pylintMessageParser.get_messages())
    if outputFilename:
        with open(outputFilename, 'w') as outputFile:
            outputFile.write(output)
    else:
        print(output)

if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
