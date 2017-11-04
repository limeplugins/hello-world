#!/usr/bin/env python
from contextlib import contextmanager
import os.path
import shutil
import sys
import os
from subprocess import call, check_call
from os.path import abspath, dirname
import logging
import click


logger = logging.getLogger(__name__)
ROOT = os.path.abspath(os.path.dirname(__file__))


@click.group(context_settings={'help_option_names': ['--help', '-h']})
@click.option(
    '--loglevel', default='INFO',
    type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']))
def cli(loglevel):
    _setup_logger(loglevel)


@cli.group(help='Run tests', invoke_without_command=True)
@click.pass_context
def test(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(flake)
        ctx.invoke(test_unit)


@test.command(name='unit', help="Run unit tests")
def test_unit():
    ret = call('py.test', shell=True)
    if ret > 0 and not ret == 5:
        raise Exception('Tests failed!')


@test.command(name='coverage', help="Run unit tests and get a coverage report")
def test_coverage():
    rm('.coverage')
    rm_rf('.htmlcov')
    check_call(['coverage', 'run', '-m', 'py.test'])
    check_call('coverage report -m'.split())
    check_call('coverage html -d .htmlcov -i'.split())
    browse_to('.htmlcov/index.html')


@test.command(help="Check for PEP8 violations")
def flake():
    check_call(['flake8', abspath(dirname(__file__))])


def rm(path):
    if os.path.isfile(path):
        os.remove(path)


def rm_rf(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


@contextmanager
def cd(path):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def browse_to(filepath):
    filepath = os.path.abspath(filepath)

    if sys.platform.startswith('darwin'):
        call('open', filepath)
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        call('xgd-open', filepath)


def _setup_logger(level):
    global_log = logging.getLogger()
    global_log.setLevel(getattr(logging, level))
    global_log.addHandler(logging.StreamHandler(sys.stdout))


if __name__ == '__main__':
    with cd(ROOT):
        sys.exit(cli())
