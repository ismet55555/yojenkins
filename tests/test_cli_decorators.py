"""Tests for yojenkins/cli/cli_decorators.py"""

import click

from yojenkins.cli.cli_decorators import debug, format_output, list, profile


def _get_param_names(cmd):
    """Extract parameter names from a Click command."""
    return [p.name for p in cmd.params]


def _get_param_by_name(cmd, name):
    """Find a Click parameter by name."""
    for p in cmd.params:
        if p.name == name:
            return p
    return None


# -- format_output decorator --


class TestFormatOutput:
    def test_adds_pretty_yaml_xml_toml_options(self):
        @click.command()
        @format_output
        def dummy(**kwargs):
            pass

        names = _get_param_names(dummy)
        assert 'pretty' in names
        assert 'yaml' in names
        assert 'xml' in names
        assert 'toml' in names

    def test_options_are_boolean_flags(self):
        @click.command()
        @format_output
        def dummy(**kwargs):
            pass

        for name in ('pretty', 'yaml', 'xml', 'toml'):
            param = _get_param_by_name(dummy, name)
            assert param.is_flag is True
            assert param.default is False

    def test_options_have_short_flags(self):
        @click.command()
        @format_output
        def dummy(**kwargs):
            pass

        expected_opts = {
            'pretty': ['-p', '--pretty'],
            'yaml': ['-y', '--yaml'],
            'xml': ['-x', '--xml'],
            'toml': ['-t', '--toml'],
        }
        for name, expected in expected_opts.items():
            param = _get_param_by_name(dummy, name)
            assert param.opts == expected


# -- debug decorator --


class TestDebug:
    def test_adds_debug_option(self):
        @click.command()
        @debug
        def dummy(**kwargs):
            pass

        names = _get_param_names(dummy)
        assert 'debug' in names

    def test_debug_is_boolean_flag_default_false(self):
        @click.command()
        @debug
        def dummy(**kwargs):
            pass

        param = _get_param_by_name(dummy, 'debug')
        assert param.is_flag is True
        assert param.default is False


# -- profile decorator --


class TestProfile:
    def test_adds_profile_and_token_options(self):
        @click.command()
        @profile
        def dummy(**kwargs):
            pass

        names = _get_param_names(dummy)
        assert 'profile' in names
        assert 'token' in names

    def test_token_reads_envvar(self):
        @click.command()
        @profile
        def dummy(**kwargs):
            pass

        param = _get_param_by_name(dummy, 'token')
        assert param.envvar == 'YOJENKINS_TOKEN'

    def test_profile_and_token_are_string_type(self):
        @click.command()
        @profile
        def dummy(**kwargs):
            pass

        for name in ('profile', 'token'):
            param = _get_param_by_name(dummy, name)
            assert param.type is click.STRING
            assert param.is_flag is False


# -- list decorator --


class TestList:
    def test_adds_list_option(self):
        @click.command()
        @list
        def dummy(**kwargs):
            pass

        names = _get_param_names(dummy)
        assert 'list' in names

    def test_list_is_boolean_flag_with_short_opt(self):
        @click.command()
        @list
        def dummy(**kwargs):
            pass

        param = _get_param_by_name(dummy, 'list')
        assert param.is_flag is True
        assert param.default is False
        assert param.opts == ['-l', '--list']


# -- Integration: decorators compose correctly --


class TestDecoratorComposition:
    def test_all_decorators_combined(self):
        @click.command()
        @debug
        @format_output
        @profile
        @list
        def dummy(**kwargs):
            pass

        names = _get_param_names(dummy)
        expected = {'debug', 'pretty', 'yaml', 'xml', 'toml', 'profile', 'token', 'list'}
        assert expected.issubset(set(names))

    def test_decorated_command_invocable(self, cli_runner):
        @click.command()
        @debug
        @format_output
        @profile
        @list
        def dummy(debug, pretty, yaml, xml, toml, profile, token, list):
            click.echo('ok')

        result = cli_runner.invoke(dummy, [])
        assert result.exit_code == 0
        assert 'ok' in result.output

    def test_decorated_command_passes_flag_values(self, cli_runner):
        @click.command()
        @format_output
        def dummy(pretty, yaml, xml, toml):
            click.echo(f'pretty={pretty} yaml={yaml}')

        result = cli_runner.invoke(dummy, ['--pretty', '--yaml'])
        assert result.exit_code == 0
        assert 'pretty=True' in result.output
        assert 'yaml=True' in result.output
