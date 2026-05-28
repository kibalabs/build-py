import os
import re
import subprocess

import click

from buildpy.util import GitHubAnnotationsReporter
from buildpy.util import Message
from buildpy.util import MessageParser
from buildpy.util import PrettyReporter


class TyMessageParser(MessageParser):
    def parse_messages(self, rawMessages: list[str]) -> list[Message]:
        output: list[Message] = []
        for rawMessage in rawMessages:
            message = rawMessage.strip()
            if not message:
                continue
            match = re.match(r'(.*):(\d+):(\d+): (error|warning|info)\[([^\]]+)\] (.*)', message)
            if match:
                level = match.group(4)
                output.append(
                    Message(
                        path=match.group(1),
                        line=int(match.group(2)),
                        column=int(match.group(3)),
                        code=match.group(5),
                        text=match.group(6).strip(),
                        level='notice' if level == 'info' else level,
                    ),
                )
        return output


class MypyMessageParser(MessageParser):
    def parse_messages(self, rawMessages: list[str]) -> list[Message]:
        output: list[Message] = []
        for rawRawMessage in rawMessages:
            rawMessage = rawRawMessage.strip()
            if len(rawMessage) == 0 or ' note: ' in rawMessage or 'Use "-> None" if function does not return a value' in rawMessage:
                continue
            if 'Error importing plugin "pydantic.mypy":' in rawMessage:
                # NOTE(krishan711): we use pydantic rules but it may not be installed (like in this repo)
                continue
            match1 = re.match(r'(.*):(\d*):(\d*): (.*): (.*) \[(.*)\]', rawMessage)
            match2 = None
            if not match1:
                # match2 = match1 without column number
                match2 = re.match(r'(.*):(\d*): (.*): (.*) \[(.*)\]', rawMessage)
            output.append(
                Message(
                    path=match1.group(1) if match1 else (match2.group(1) if match2 else ''),
                    line=int(match1.group(2)) if match1 else (int(match2.group(2)) if match2 else 0),
                    column=int(match1.group(3)) if match1 else 0,
                    code=match1.group(6) if match1 else (match2.group(5) if match2 else 'unparsed'),
                    text=match1.group(5).strip() if match1 else (match2.group(4).strip() if match2 else rawMessage.strip()),
                    level=match1.group(4) if match1 else (match2.group(3) if match2 else 'error'),
                ),
            )
        return output


@click.command()
@click.argument('targets', nargs=-1)
@click.option('-o', '--output-file', 'outputFilename', required=False, type=str)
@click.option('-f', '--output-format', 'outputFormat', required=False, type=str, default='pretty')
@click.option('-c', '--config-file-path', 'configFilePath', required=False, type=str)
@click.option('--mypy', 'shouldUseMypy', default=False, is_flag=True)
def run(targets: list[str], outputFilename: str, outputFormat: str, configFilePath: str, shouldUseMypy: bool) -> None:
    currentDirectory = os.path.dirname(os.path.realpath(__file__))
    messages: list[str] = []
    if shouldUseMypy:
        mypyConfigFilePath = configFilePath or f'{currentDirectory}/pyproject.toml'
        command = f'mypy {" ".join(targets)} --config-file {mypyConfigFilePath} --no-color-output --hide-error-context --no-pretty --no-error-summary --show-error-codes --show-column-numbers'
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)  # noqa: S602
        except subprocess.CalledProcessError as exception:
            messages = exception.output.decode().split('\n')
        messageParser: MessageParser = MypyMessageParser()
        parsedMessages = messageParser.parse_messages(rawMessages=messages)
    else:
        command = f'ty check --output-format concise {" ".join(targets)}'
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)  # noqa: S602
        except subprocess.CalledProcessError as exception:
            messages = exception.output.decode().split('\n')
        messageParser = TyMessageParser()
        parsedMessages = messageParser.parse_messages(rawMessages=messages)
    reporter = GitHubAnnotationsReporter() if outputFormat == 'annotations' else PrettyReporter()
    output = reporter.create_output(messages=parsedMessages)
    if outputFilename:
        with open(outputFilename, 'w') as outputFile:
            outputFile.write(output)
    else:
        print(output)  # noqa: T201


if __name__ == '__main__':
    run()
