#!/usr/bin/env python
from contextlib import contextmanager
import os.path
import shutil
import sys
import os
from subprocess import call, check_call, CalledProcessError, check_output
from os.path import abspath, dirname
import glob
from wheel.install import WheelFile
import getpass
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


@cli.command(help='Build package')
def build():
    rm_rf('build')
    rm_rf('dist')
    check_call(['python', 'setup.py', '-q', 'bdist_wheel'])


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


@cli.group(help='Documentation helpers')
def docs():
    pass


@docs.command(name='generate', help="Generate documentation")
def docs_generate():
    rm('docs/index.rst')
    rm('docs/modules.rst')
    call(['sphinx-apidoc', '-o', 'docs', abspath(dirname(__file__))])
    check_call(['sphinx-build', '-q', '-b', 'html', 'docs',
                'docs/_build/html'])


@docs.command(name='view', help="View generated documentation")
def viewdocs():
    filepath = os.path.abspath('./docs/_build/html/index.html')
    if not os.path.isfile(filepath):
        print('No documentation found. Run docs command')
        return

    browse_to(filepath)


@cli.command(name='console', help="Run the selected application in an IPython "
             "console. The application is loaded in the variable 'app'.")
@click.argument('application')
@click.option('--user', '-u', required=True, help="User name to run as")
@click.option('--password', '-p', help='Password for user')
def console(application: 'Application to connect to',
            user, password=None):
    import IPython
    import lime_application
    import lime_acl
    import lime_config
    import lime_session
    import yaml

    if not password:
        password = getpass.getpass()

    session = lime_session.create_session(database=application,
                                          username=user,
                                          password=password,
                                          language='en')

    lime_config.load_config('development console', {})
    app = lime_application.get_application(application,
                                           session=session,
                                           acl=lime_acl.AlwaysAllowAcl())

    banner = """\
**** Welcome to the Lime CRM development console ****

The application object for "{appname}" is stored in the variable 'app'.

Current configuration:
{currconfig}

You might add additional configuration at "{configpath}".
    """.format(
        appname=application,
        currconfig=yaml.safe_dump(
            lime_config.config, default_flow_style=False),
        configpath=lime_config.config_file_path('development console'))

    IPython.embed(argv=[], user_ns={'app': app}, banner1=banner)


@cli.command(help="Build wheel and upload to internal pypi server")
@click.option('--force', '-f', default=False, is_flag=True, help="Force")
@click.option('--username', '-u', help='Username for uploading to internal '
              'pypi server')
@click.option('--password', '-p', help='Password')
@click.pass_context
def upload(ctx, username=None, password=None, force=False):
    ctx.invoke(build)

    def package_exists(path):
        parsed_filename = WheelFile(path).parsed_filename
        package, version = parsed_filename.group(2), parsed_filename.group(4)
        p = check_output('devpi list {}=={}'.format(package, version).split())
        exists = True if p else False
        if exists:
            print('Package {}={} already exists.'.format(package, version))
        return exists

    def get_wheel_path():
        dist_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'dist'))
        return next(iter(glob.glob('{}/*.whl'.format(dist_dir))))

    wheel_path = get_wheel_path()
    if force or not package_exists(wheel_path):
        if username:
            if not password:
                password = getpass.getpass()
            check_call(['devpi', 'login', username, '--password', password])

        check_call(['devpi', 'upload', wheel_path])


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


def run_cli():
    try:
        sys.exit(cli())
    except CalledProcessError as e:
        logger.error(e)
        sys.exit(e.returncode)
    except Exception as e:
        logger.error(e)
        sys.exit(-1)


if __name__ == '__main__':
    with cd(ROOT):
        run_cli()
