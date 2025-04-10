import json
import os

import click
import pytest

from buildpy.util import GitHubAnnotationsReporter
from buildpy.util import Message
from buildpy.util import PrettyReporter


@click.command()
@click.argument('targets', nargs=-1)
@click.option('-o', '--output-file', 'outputFilename', required=False, type=str)
@click.option('-f', '--output-format', 'outputFormat', required=False, type=str, default='pretty')
def run(targets: list[str], outputFilename: str, outputFormat: str) -> None:
    parsedMessages: list[Message] = []
    pytestOutputFilename = 'raw_test_results.json'
    if not targets:
        targets = ['tests']
    pytest.main([*list(targets), '-qq', '--json-report', '--no-summary', '--no-header', '--asyncio-mode=auto', '--override-ini=asyncio_default_fixture_loop_scope=function', f'--json-report-file={pytestOutputFilename}'], plugins=[])
    with open(pytestOutputFilename, 'r') as file:
        output = json.loads(file.read())
    os.remove(pytestOutputFilename)
    # print(json.dumps(output))
    # summary = output['summary']
    tests = output['tests']
    for test in tests:
        isFailed = test['outcome'] != 'passed'
        if isFailed:
            # NOTE(krishan711): the setup or teardown may fail too, deal with that?
            isCallFailed = test['call']['outcome'] == 'failed'
            path = ''
            line = 0
            text = 'Failed'
            if isCallFailed:
                crash = test['call'].get('crash', {})
                path = crash.get('path', path)
                line = crash.get('lineno', line)
                text = crash.get('message', text)
            parsedMessages.append(
                Message(
                    path=path,
                    line=line,
                    column=0,
                    code='fail',
                    text=text,
                    level='error',
                ),
            )
    reporter = GitHubAnnotationsReporter() if outputFormat == 'annotations' else PrettyReporter()
    output = reporter.create_output(messages=parsedMessages)
    if outputFilename:
        with open(outputFilename, 'w') as outputFile:
            outputFile.write(output)
    else:
        print(output)  # noqa: T201


if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
