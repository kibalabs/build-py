import dataclasses
import json
import os
from collections import defaultdict
from typing import List

from simple_chalk import chalk  # type: ignore


@dataclasses.dataclass
class Message:
    path: str
    line: int
    column: int
    code: str
    text: str
    level: str # (error, warning, notice)


class MessageParser:

    def parse_messages(self, rawMessages: List[str]) -> List[Message]:
        raise NotImplementedError


class KibaReporter:

    def create_output(self, messages: List[Message]) -> str:
        raise NotImplementedError


class GitHubAnnotationsReporter(KibaReporter):

    def create_output(self, messages: List[Message]) -> str:
        annotations = []
        for message in messages:
            annotation = {
                'path': os.path.relpath(message.path) if message.path else '<unknown>',
                'start_line': message.line,
                'end_line': message.line,
                'start_column': message.column,
                'end_column': message.column,
                'message': f'[{message.code}] {message.text}',
                'annotation_level':
                'note' if message.level == 'notice' else ('warning' if message.level == 'warning' else 'failure'),
            }
            annotations.append(annotation)
        return json.dumps(annotations)


class PrettyReporter(KibaReporter):

    @staticmethod
    def get_summary(errorCount: int, warningCount: int) -> str:
        summary = ''
        if errorCount:
            summary += chalk.red(f'{errorCount} errors')
        if warningCount:
            summary = f'{summary} and ' if summary else ''
            summary += chalk.yellow(f'{warningCount} warnings')
        return summary

    def create_output(self, messages: List[Message]) -> str:
        fileMessageMap = defaultdict(list)
        for message in messages:
            fileMessageMap[os.path.relpath(message.path) if message.path else '<unknown>'].append(message)
        totalErrorCount = 0
        totalWarningCount = 0
        outputs = []
        for (filePath, fileMessages) in fileMessageMap.items():
            fileOutputs = []
            for message in fileMessages:
                location = chalk.grey(f'{filePath}:{message.line}:{message.column}')
                color = chalk.white if message.level == 'notice' else (chalk.yellow if message.level == 'warning' else chalk.red)
                fileOutputs.append(f'{location} [{color(message.code)}] {message.text}')
            errorCount = sum(1 for message in fileMessages if message.level == 'error')
            totalErrorCount += errorCount
            warningCount = sum(1 for message in fileMessages if message.level == 'warning')
            totalWarningCount += warningCount
            fileOutputString = '\n'.join(fileOutputs)
            outputs.append(f'{self.get_summary(errorCount, warningCount)} in {filePath}\n{fileOutputString}\n')
        output = '\n'.join(outputs)
        output += f'\nFailed due to {self.get_summary(totalErrorCount, totalWarningCount)}.' if (totalErrorCount or totalWarningCount) else chalk.green('Passed.')
        return output
