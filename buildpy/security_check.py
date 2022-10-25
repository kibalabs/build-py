import os
import subprocess
from typing import List

import click

from buildpy.util import GitHubAnnotationsReporter
from buildpy.util import Message
from buildpy.util import MessageParser
from buildpy.util import PrettyReporter

# TODO(krishan711): remove this once test_name is enabled https://github.com/PyCQA/bandit/issues/962
BANDIT_CODES = {
    'B101': 'assert_used',
    'B102': 'exec_used',
    'B103': 'set_bad_file_permissions',
    'B104': 'hardcoded_bind_all_interfaces',
    'B105': 'hardcoded_password_string',
    'B106': 'hardcoded_password_funcarg',
    'B107': 'hardcoded_password_default',
    'B108': 'hardcoded_tmp_directory',
    'B110': 'try_except_pass',
    'B112': 'try_except_continue',
    'B201': 'flask_debug_true',
    'B301': 'pickle',
    'B302': 'marshal',
    'B303': 'md5',
    'B304': 'ciphers',
    'B305': 'cipher_modes',
    'B306': 'mktemp_q',
    'B307': 'eval',
    'B308': 'mark_safe',
    'B309': 'httpsconnection',
    'B310': 'urllib_urlopen',
    'B311': 'random',
    'B312': 'telnetlib',
    'B313': 'xml_bad_cElementTree',
    'B314': 'xml_bad_ElementTree',
    'B315': 'xml_bad_expatreader',
    'B316': 'xml_bad_expatbuilder',
    'B317': 'xml_bad_sax',
    'B318': 'xml_bad_minidom',
    'B319': 'xml_bad_pulldom',
    'B320': 'xml_bad_etree',
    'B321': 'ftplib',
    'B323': 'unverified_context',
    'B324': 'hashlib_insecure_functions',
    'B325': 'tempnam',
    'B401': 'import_telnetlib',
    'B402': 'import_ftplib',
    'B403': 'import_pickle',
    'B404': 'import_subprocess',
    'B405': 'import_xml_etree',
    'B406': 'import_xml_sax',
    'B407': 'import_xml_expat',
    'B408': 'import_xml_minidom',
    'B409': 'import_xml_pulldom',
    'B410': 'import_lxml',
    'B411': 'import_xmlrpclib',
    'B412': 'import_httpoxy',
    'B413': 'import_pycrypto',
    'B415': 'import_pyghmi',
    'B501': 'request_with_no_cert_validation',
    'B502': 'ssl_with_bad_version',
    'B503': 'ssl_with_bad_defaults',
    'B504': 'ssl_with_no_version',
    'B505': 'weak_cryptographic_key',
    'B506': 'yaml_load',
    'B507': 'ssh_no_host_key_verification',
    'B508': 'snmp_insecure_version',
    'B509': 'snmp_weak_cryptography',
    'B601': 'paramiko_calls',
    'B602': 'subprocess_popen_with_shell_equals_true',
    'B603': 'subprocess_without_shell_equals_true',
    'B604': 'any_other_function_with_shell_equals_true',
    'B605': 'start_process_with_a_shell',
    'B606': 'start_process_with_no_shell',
    'B607': 'start_process_with_partial_path',
    'B608': 'hardcoded_sql_expressions',
    'B609': 'linux_commands_wildcard_injection',
    'B610': 'django_extra_used',
    'B611': 'django_rawsql_used',
    'B701': 'jinja2_autoescape_false',
    'B702': 'use_of_mako_templates',
    'B703': 'django_mark_safe',
}

class BanditMessageParser(MessageParser):

    @staticmethod
    def _get_error_level(banditLevel: str) -> str:
        banditLevel = banditLevel.lower()
        if banditLevel == 'low':
            return 'notice'
        if banditLevel == 'warning':
            return 'warning'
        return 'error'

    def parse_messages(self, rawMessages: List[str]) -> List[Message]:
        output: List[Message] = []
        for rawMessage in rawMessages:
            rawMessage = rawMessage.strip()
            if len(rawMessage) == 0 or rawMessage.startswith('filename,test_name,'):
                continue
            rawMessageParts = rawMessage.split('\t')
            if len(rawMessageParts) == 1:
                continue
            if rawMessageParts[0] == '[tester]':
                output.append(Message(
                    path='',
                    line=0,
                    column=0,
                    code='tester',
                    text=rawMessageParts[2],
                    level=self._get_error_level(banditLevel=rawMessageParts[1]),
                ))
            else:
                output.append(Message(
                    path=rawMessageParts[0],
                    line=int(rawMessageParts[1]),
                    column=int(rawMessageParts[2]),
                    code=BANDIT_CODES[rawMessageParts[3]],
                    text=rawMessageParts[4],
                    level=self._get_error_level(banditLevel=rawMessageParts[5]),
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
    messages = []
    banditConfigFilePath = configFilePath or f'{currentDirectory}/bandit.yaml'
    # TODO(krishan711): use test_name here once enabled https://github.com/PyCQA/bandit/issues/962
    messageTemplate = '{abspath}\t{line}\t{col}\t{test_id}\t{msg}\t{severity}'
    try:
        subprocess.check_output(f'bandit --configfile {banditConfigFilePath} --silent --severity-level medium --confidence-level medium --format custom --msg-template \"{messageTemplate}\" --recursive {targetDirectory}', stderr=subprocess.STDOUT, shell=True)  # nosec=subprocess_popen_with_shell_equals_true
    except subprocess.CalledProcessError as exception:
        messages = exception.output.decode().split('\n')
    messageParser = BanditMessageParser()
    parsedMessages = messageParser.parse_messages(rawMessages=messages)
    reporter = GitHubAnnotationsReporter() if outputFormat == 'annotations' else PrettyReporter()
    output = reporter.create_output(messages=parsedMessages)
    if outputFilename:
        with open(outputFilename, 'w') as outputFile:
            outputFile.write(output)
    else:
        print(output)

if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
