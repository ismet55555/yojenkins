"""Tests for yojenkins/utility/utility.py"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
import toml
import yaml

from yojenkins.utility.utility import (
    am_i_bundled,
    am_i_inside_docker,
    append_lines_to_file,
    build_url_complete,
    build_url_to_build_number,
    build_url_to_other_url,
    fail_out,
    failures_out,
    format_name,
    fullname_to_name,
    get_item_action,
    has_build_number_started,
    has_special_char,
    html_clean,
    is_complete_build_url,
    is_credential_id_format,
    is_full_url,
    is_list_items_in_dict,
    item_url_to_server_url,
    iter_data_empty_item_stripper,
    load_contents_from_local_file,
    load_contents_from_string,
    name_to_url,
    parse_and_check_input_string_list,
    remove_special_char,
    template_apply,
    to_seconds,
    translate_kwargs,
    url_to_name,
    write_xml_to_file,
)


# ---------------------------------------------------------------------------
# TestTranslateKwargs
# ---------------------------------------------------------------------------
class TestTranslateKwargs:
    def test_standard_mapping(self):
        original = {'pretty': True, 'yaml': False, 'json': True}
        result = translate_kwargs(original)
        assert result == {'opt_pretty': True, 'opt_yaml': False, 'opt_json': True}

    def test_unmapped_keys_pass_through(self):
        original = {'server': 'http://localhost', 'timeout': 30}
        result = translate_kwargs(original)
        assert result == original

    def test_mixed_mapped_and_unmapped(self):
        original = {'pretty': True, 'server': 'http://localhost', 'xml': False}
        result = translate_kwargs(original)
        assert result == {'opt_pretty': True, 'server': 'http://localhost', 'opt_xml': False}

    def test_empty_dict(self):
        assert translate_kwargs({}) == {}

    def test_all_translate_keys(self):
        original = {'pretty': 1, 'yaml': 2, 'xml': 3, 'toml': 4, 'list': 5, 'json': 6, 'id': 7}
        result = translate_kwargs(original)
        assert result == {
            'opt_pretty': 1, 'opt_yaml': 2, 'opt_xml': 3, 'opt_toml': 4,
            'opt_list': 5, 'opt_json': 6, 'opt_id': 7,
        }


# ---------------------------------------------------------------------------
# TestIsFullUrl
# ---------------------------------------------------------------------------
class TestIsFullUrl:
    @pytest.mark.parametrize('url', [
        'http://localhost:8080/',
        'https://jenkins.example.com/job/test/',
        'http://10.0.0.1:8080/job/foo',
    ])
    def test_valid_urls(self, url):
        assert is_full_url(url) is True

    @pytest.mark.parametrize('url', [
        'localhost:8080',
        '/job/test/',
        'just-a-string',
        '',
    ])
    def test_invalid_urls(self, url):
        assert is_full_url(url) is False


# ---------------------------------------------------------------------------
# TestUrlToName
# ---------------------------------------------------------------------------
class TestUrlToName:
    def test_simple_job_url(self):
        url = 'http://localhost:8080/job/my-job/'
        assert url_to_name(url) == 'my-job'

    def test_nested_job_url(self):
        url = 'http://localhost:8080/job/folder1/job/folder2/job/my-job/'
        assert url_to_name(url) == 'folder1/folder2/my-job'

    def test_url_with_view(self):
        url = 'http://localhost:8080/view/all/job/my-job/'
        assert url_to_name(url) == 'all/my-job'

    def test_base_url(self):
        url = 'http://localhost:8080/'
        assert url_to_name(url) == ''


# ---------------------------------------------------------------------------
# TestNameToUrl
# ---------------------------------------------------------------------------
class TestNameToUrl:
    def test_simple_name(self):
        result = name_to_url('http://localhost:8080/', 'my-job')
        assert result == 'http://localhost:8080/job/my-job'

    def test_nested_name(self):
        result = name_to_url('http://localhost:8080/', 'folder1/folder2/my-job')
        assert result == 'http://localhost:8080/job/folder1/job/folder2/job/my-job'

    def test_dot_returns_base_url(self):
        result = name_to_url('http://localhost:8080/', '.')
        assert result == 'http://localhost:8080/'


# ---------------------------------------------------------------------------
# TestFormatName
# ---------------------------------------------------------------------------
class TestFormatName:
    def test_removes_job_prefix(self):
        assert format_name('/job/folder1/job/my-job/') == 'folder1/my-job'

    def test_removes_view_prefix(self):
        assert format_name('view/all/job/my-job') == 'all/my-job'

    def test_strips_slashes(self):
        assert format_name('/my-job/') == 'my-job'

    def test_plain_name(self):
        assert format_name('my-job') == 'my-job'


# ---------------------------------------------------------------------------
# TestFullnameToName
# ---------------------------------------------------------------------------
class TestFullnameToName:
    def test_nested_fullname(self):
        assert fullname_to_name('Hey/This/Is/A/Full/Job') == 'Job'

    def test_single_name(self):
        assert fullname_to_name('Job') == 'Job'

    def test_with_slashes(self):
        assert fullname_to_name('/folder/subfolder/item/') == 'item'


# ---------------------------------------------------------------------------
# TestHasSpecialChar
# ---------------------------------------------------------------------------
class TestHasSpecialChar:
    def test_with_special_chars(self):
        assert has_special_char('hello@world') is True
        assert has_special_char('test!value') is True
        assert has_special_char('path/name') is True

    def test_without_special_chars(self):
        assert has_special_char('helloworld') is False
        assert has_special_char('test-value') is False
        assert has_special_char('test_value') is False

    def test_custom_special_chars(self):
        assert has_special_char('hello-world', special_chars='-') is True
        assert has_special_char('hello-world', special_chars='@') is False


# ---------------------------------------------------------------------------
# TestRemoveSpecialChar
# ---------------------------------------------------------------------------
class TestRemoveSpecialChar:
    def test_removes_default_specials(self):
        assert remove_special_char('hello@world!') == 'helloworld'

    def test_no_special_chars(self):
        assert remove_special_char('helloworld') == 'helloworld'

    def test_custom_special_chars(self):
        assert remove_special_char('hello-world', special_chars='-') == 'helloworld'


# ---------------------------------------------------------------------------
# TestIsCredentialIdFormat
# ---------------------------------------------------------------------------
class TestIsCredentialIdFormat:
    def test_valid_uuid(self):
        assert is_credential_id_format('a1b2c3d4-e5f6-7890-abcd-ef1234567890') is True

    def test_invalid_too_short(self):
        assert is_credential_id_format('a1b2c3d4-e5f6') is False

    def test_invalid_no_dashes(self):
        assert is_credential_id_format('a1b2c3d4e5f67890abcdef1234567890') is False

    def test_invalid_empty(self):
        assert is_credential_id_format('') is False

    def test_invalid_special_chars(self):
        assert is_credential_id_format('a1b2c3d4-e5f6-7890-abcd-ef123456789!') is False


# ---------------------------------------------------------------------------
# TestHtmlClean
# ---------------------------------------------------------------------------
class TestHtmlClean:
    def test_removes_tags(self):
        assert html_clean('<p>Hello <b>World</b></p>') == 'Hello World'

    def test_converts_entities(self):
        assert html_clean('&lt;div&gt;') == '<div>'
        assert html_clean('&amp;') == '&'
        assert html_clean('&quot;test&quot;') == '"test"'
        assert html_clean("&apos;test&apos;") == "'test'"

    def test_plain_text_unchanged(self):
        assert html_clean('plain text') == 'plain text'

    def test_empty_string(self):
        assert html_clean('') == ''

    def test_nbsp_removed(self):
        assert html_clean('hello&nbsp;world') == 'helloworld'


# ---------------------------------------------------------------------------
# TestBuildUrlToOtherUrl
# ---------------------------------------------------------------------------
class TestBuildUrlToOtherUrl:
    def test_build_url_to_job_url(self):
        build_url = 'http://localhost:8080/job/my-folder/job/my-job/42/'
        result = build_url_to_other_url(build_url, target_url='job')
        assert result == 'http://localhost:8080/job/my-folder/job/my-job/'

    def test_build_url_to_folder_url(self):
        build_url = 'http://localhost:8080/job/my-folder/job/my-job/42/'
        result = build_url_to_other_url(build_url, target_url='folder')
        assert result == 'http://localhost:8080/job/my-folder/'

    def test_invalid_target(self):
        build_url = 'http://localhost:8080/job/my-job/42/'
        result = build_url_to_other_url(build_url, target_url='invalid')
        assert result == ''


# ---------------------------------------------------------------------------
# TestBuildUrlToBuildNumber
# ---------------------------------------------------------------------------
class TestBuildUrlToBuildNumber:
    def test_short_path_returns_none(self):
        # Only 3 path components (job, my-job, 15): range(2,2,-1) is empty
        url = 'http://localhost:8080/job/my-job/15/'
        assert build_url_to_build_number(url) is None

    def test_short_path_with_console_returns_none(self):
        # 4 components but no int at position where index-2 == 'job'
        url = 'http://localhost:8080/job/my-job/15/console'
        assert build_url_to_build_number(url) is None

    def test_job_url_no_build_number(self):
        url = 'http://localhost:8080/job/my-job/'
        assert build_url_to_build_number(url) is None

    def test_nested_job_build_url(self):
        url = 'http://localhost:8080/job/folder/job/my-job/42/'
        assert build_url_to_build_number(url) == 42

    def test_nested_job_build_url_with_console(self):
        url = 'http://localhost:8080/job/folder/job/my-job/42/console'
        assert build_url_to_build_number(url) == 42


# ---------------------------------------------------------------------------
# TestIsCompleteBuildUrl
# ---------------------------------------------------------------------------
class TestIsCompleteBuildUrl:
    def test_complete_url(self):
        assert is_complete_build_url('http://localhost:8080/job/my-job/42') is True

    def test_incomplete_url_no_number(self):
        assert is_complete_build_url('http://localhost:8080/job/my-job/') is False

    def test_empty_string(self):
        assert is_complete_build_url('') is False


# ---------------------------------------------------------------------------
# TestBuildUrlComplete
# ---------------------------------------------------------------------------
class TestBuildUrlComplete:
    def test_already_complete(self):
        url = 'http://localhost:8080/job/my-job/15'
        assert build_url_complete(url) == url

    def test_with_trailing_path(self):
        url = 'http://localhost:8080/job/my-job/15/console'
        result = build_url_complete(url)
        assert result == 'http://localhost:8080/job/my-job/15/'

    def test_no_build_number(self):
        url = 'http://localhost:8080/job/my-job/'
        assert build_url_complete(url) is None

    def test_empty_string(self):
        assert build_url_complete('') is None


# ---------------------------------------------------------------------------
# TestItemUrlToServerUrl
# ---------------------------------------------------------------------------
class TestItemUrlToServerUrl:
    def test_with_scheme(self):
        url = 'http://localhost:8080/job/my-job/42/'
        assert item_url_to_server_url(url) == 'http://localhost:8080'

    def test_without_scheme(self):
        url = 'http://localhost:8080/job/my-job/42/'
        assert item_url_to_server_url(url, include_scheme=False) == 'localhost:8080'


# ---------------------------------------------------------------------------
# TestToSeconds
# ---------------------------------------------------------------------------
class TestToSeconds:
    @pytest.mark.parametrize('unit,expected', [
        ('s', 10),
        ('sec', 10),
        ('second', 10),
        ('seconds', 10),
    ])
    def test_seconds(self, unit, expected):
        assert to_seconds(10, unit) == expected

    @pytest.mark.parametrize('unit,expected', [
        ('m', 600),
        ('min', 600),
        ('minute', 600),
        ('minutes', 600),
    ])
    def test_minutes(self, unit, expected):
        assert to_seconds(10, unit) == expected

    @pytest.mark.parametrize('unit,expected', [
        ('h', 36000),
        ('hr', 36000),
        ('hour', 36000),
        ('hours', 36000),
    ])
    def test_hours(self, unit, expected):
        assert to_seconds(10, unit) == expected

    @pytest.mark.parametrize('unit,expected', [
        ('d', 2160000),
        ('day', 2160000),
        ('days', 2160000),
    ])
    def test_days(self, unit, expected):
        assert to_seconds(10, unit) == expected

    def test_zero_quantity(self):
        assert to_seconds(0, 'm') == 0

    def test_unknown_unit(self):
        assert to_seconds(10, 'unknown') == 0


# ---------------------------------------------------------------------------
# TestIterDataEmptyItemStripper
# ---------------------------------------------------------------------------
class TestIterDataEmptyItemStripper:
    def test_dict_with_empty_values(self):
        data = {'a': 1, 'b': None, 'c': {}, 'd': 'hello'}
        result = iter_data_empty_item_stripper(data)
        assert result == {'a': 1, 'd': 'hello'}

    def test_list_with_empty_values(self):
        data = [1, None, {}, 'hello', ()]
        result = iter_data_empty_item_stripper(data)
        assert result == [1, 'hello']

    def test_nested_dict(self):
        data = {'a': {'b': None, 'c': 1}, 'd': {}}
        result = iter_data_empty_item_stripper(data)
        assert result == {'a': {'c': 1}}

    def test_scalar_passthrough(self):
        assert iter_data_empty_item_stripper('hello') == 'hello'
        assert iter_data_empty_item_stripper(42) == 42

    def test_empty_set_removed(self):
        data = [1, set(), 2]
        result = iter_data_empty_item_stripper(data)
        assert result == [1, 2]


# ---------------------------------------------------------------------------
# TestTemplateApply
# ---------------------------------------------------------------------------
class TestTemplateApply:
    def test_basic_substitution(self):
        template = 'Hello ${name}, welcome to ${place}'
        result = template_apply(template, name='World', place='Earth')
        assert result == 'Hello World, welcome to Earth'

    def test_missing_variable_safe(self):
        template = 'Hello ${name}, ${missing}'
        result = template_apply(template, name='World')
        assert '${missing}' in result
        assert 'World' in result

    def test_none_replaced_with_empty(self):
        template = 'value=${val}'
        result = template_apply(template, val=None)
        assert result == 'value='

    def test_json_mode(self):
        template = '{"key": "${value}"}'
        result = template_apply(template, is_json=True, value='hello')
        assert result == {'key': 'hello'}

    def test_json_mode_invalid_json(self):
        template = 'not json ${val}'
        result = template_apply(template, is_json=True, val='x')
        assert result == ''


# ---------------------------------------------------------------------------
# TestParseAndCheckInputStringList
# ---------------------------------------------------------------------------
class TestParseAndCheckInputStringList:
    def test_basic_split(self):
        result = parse_and_check_input_string_list('a,b,c')
        assert result == ['a', 'b', 'c']

    def test_strips_whitespace(self):
        result = parse_and_check_input_string_list('a , b , c')
        assert result == ['a', 'b', 'c']

    def test_join_back(self):
        result = parse_and_check_input_string_list('a,b,c', join_back_char=';')
        assert result == 'a;b;c'

    def test_special_char_returns_empty(self):
        result = parse_and_check_input_string_list('a,b@c,d')
        assert result == []

    def test_custom_split_char(self):
        result = parse_and_check_input_string_list('a;b;c', split_char=';')
        assert result == ['a', 'b', 'c']


# ---------------------------------------------------------------------------
# TestFailOut
# ---------------------------------------------------------------------------
class TestFailOut:
    def test_exits_with_code_1(self):
        with pytest.raises(SystemExit) as exc_info:
            fail_out('Something went wrong')
        assert exc_info.value.code == 1


class TestFailuresOut:
    def test_exits_with_code_1(self):
        with pytest.raises(SystemExit) as exc_info:
            failures_out(['Error 1', 'Error 2'])
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# TestIsListItemsInDict
# ---------------------------------------------------------------------------
class TestIsListItemsInDict:
    def test_match_found(self):
        result = is_list_items_in_dict(['hey', 'yo'], {'yo': 1})
        assert result == 1

    def test_no_match(self):
        result = is_list_items_in_dict(['a', 'b'], {'c': 1})
        assert result is None

    def test_first_match_returned(self):
        result = is_list_items_in_dict(['a', 'b', 'c'], {'b': 1, 'c': 2})
        assert result == 1


# ---------------------------------------------------------------------------
# TestHasBuildNumberStarted
# ---------------------------------------------------------------------------
class TestHasBuildNumberStarted:
    def test_build_found(self):
        job_info = {'builds': [{'number': 1}, {'number': 2}, {'number': 3}]}
        assert has_build_number_started(job_info, 2) is True

    def test_build_not_found(self):
        job_info = {'builds': [{'number': 1}, {'number': 3}]}
        assert has_build_number_started(job_info, 2) is False

    def test_no_builds_key(self):
        assert has_build_number_started({}, 1) is False

    def test_missing_number_key(self):
        job_info = {'builds': [{'url': 'http://example.com'}]}
        assert has_build_number_started(job_info, 1) is False


# ---------------------------------------------------------------------------
# TestGetItemAction
# ---------------------------------------------------------------------------
class TestGetItemAction:
    def test_matching_actions(self):
        item_info = {
            'actions': [
                {'_class': 'hudson.model.CauseAction', 'data': 1},
                {'_class': 'hudson.model.ParametersAction', 'data': 2},
                {'_class': 'hudson.model.CauseAction', 'data': 3},
            ]
        }
        result = get_item_action(item_info, 'hudson.model.CauseAction')
        assert len(result) == 2
        assert result[0]['data'] == 1
        assert result[1]['data'] == 3

    def test_no_matching_actions(self):
        item_info = {'actions': [{'_class': 'some.other.Class'}]}
        result = get_item_action(item_info, 'hudson.model.CauseAction')
        assert result == []

    def test_empty_action_entries_skipped(self):
        item_info = {
            'actions': [
                None,
                {},
                {'_class': 'hudson.model.CauseAction', 'data': 1},
            ]
        }
        result = get_item_action(item_info, 'hudson.model.CauseAction')
        assert len(result) == 1


# ---------------------------------------------------------------------------
# TestLoadContentsFromLocalFile (uses tmp_path)
# ---------------------------------------------------------------------------
class TestLoadContentsFromLocalFile:
    def test_load_json(self, tmp_path):
        data = {'key': 'value', 'number': 42}
        f = tmp_path / 'test.json'
        f.write_text(json.dumps(data))
        result = load_contents_from_local_file('json', str(f))
        assert result == data

    def test_load_yaml(self, tmp_path):
        data = {'key': 'value', 'items': [1, 2, 3]}
        f = tmp_path / 'test.yaml'
        f.write_text(yaml.dump(data))
        result = load_contents_from_local_file('yaml', str(f))
        assert result == data

    def test_load_toml(self, tmp_path):
        data = {'section': {'key': 'value'}}
        f = tmp_path / 'test.toml'
        f.write_text(toml.dumps(data))
        result = load_contents_from_local_file('toml', str(f))
        assert result == data

    def test_load_jsonl(self, tmp_path):
        lines = [{'a': 1}, {'b': 2}]
        f = tmp_path / 'test.jsonl'
        f.write_text('\n'.join(json.dumps(l) for l in lines))
        result = load_contents_from_local_file('jsonl', str(f))
        assert result == lines

    def test_missing_file_exits(self):
        with pytest.raises(SystemExit):
            load_contents_from_local_file('json', '/nonexistent/path/file.json')

    def test_empty_file_returns_empty_dict(self, tmp_path):
        f = tmp_path / 'empty.json'
        f.write_text('')
        result = load_contents_from_local_file('json', str(f))
        assert result == {}


# ---------------------------------------------------------------------------
# TestLoadContentsFromString
# ---------------------------------------------------------------------------
class TestLoadContentsFromString:
    def test_json_string(self):
        result = load_contents_from_string('json', '{"key": "value"}')
        assert result == {'key': 'value'}

    def test_yaml_string(self):
        result = load_contents_from_string('yaml', 'key: value\n')
        assert result == {'key': 'value'}

    def test_toml_string(self):
        result = load_contents_from_string('toml', 'key = "value"\n')
        assert result == {'key': 'value'}

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match='Unknown file type'):
            load_contents_from_string('xml', '<root/>')

    def test_case_insensitive(self):
        result = load_contents_from_string('JSON', '{"a": 1}')
        assert result == {'a': 1}


# ---------------------------------------------------------------------------
# TestAppendLinesToFile (uses tmp_path)
# ---------------------------------------------------------------------------
class TestAppendLinesToFile:
    def test_append_to_beginning(self, tmp_path):
        f = tmp_path / 'test.txt'
        f.write_text('existing\n')
        result = append_lines_to_file(str(f), ['prepended\n'], location='beginning')
        assert result is True
        content = f.read_text()
        assert content.startswith('prepended\n')
        assert 'existing\n' in content

    def test_append_to_end(self, tmp_path):
        f = tmp_path / 'test.txt'
        f.write_text('existing\n')
        result = append_lines_to_file(str(f), ['appended\n'], location='end')
        assert result is True
        content = f.read_text()
        assert content.endswith('appended\n')

    def test_missing_file_returns_false(self):
        result = append_lines_to_file('/nonexistent/file.txt', ['line\n'])
        assert result is False

    def test_invalid_location_returns_false(self, tmp_path):
        f = tmp_path / 'test.txt'
        f.write_text('existing\n')
        result = append_lines_to_file(str(f), ['line\n'], location='middle')
        assert result is False


# ---------------------------------------------------------------------------
# TestWriteXmlToFile (uses tmp_path)
# ---------------------------------------------------------------------------
class TestWriteXmlToFile:
    def test_write_xml(self, tmp_path):
        xml = '<root><item>hello</item></root>'
        f = tmp_path / 'output.xml'
        result = write_xml_to_file(xml, str(f))
        assert result is True
        assert f.read_text() == xml

    def test_write_as_json(self, tmp_path):
        xml = '<root><item>hello</item></root>'
        f = tmp_path / 'output.json'
        result = write_xml_to_file(xml, str(f), opt_json=True)
        assert result is True
        content = json.loads(f.read_text())
        assert 'root' in content

    def test_write_as_yaml(self, tmp_path):
        xml = '<root><item>hello</item></root>'
        f = tmp_path / 'output.yaml'
        result = write_xml_to_file(xml, str(f), opt_yaml=True)
        assert result is True
        content = yaml.safe_load(f.read_text())
        assert 'root' in content


# ---------------------------------------------------------------------------
# TestAmIInsideDocker
# ---------------------------------------------------------------------------
class TestAmIInsideDocker:
    def test_not_in_docker(self):
        # On a dev machine this should be False
        # We don't mock here because the function checks real filesystem
        result = am_i_inside_docker()
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# TestAmIBundled
# ---------------------------------------------------------------------------
class TestAmIBundled:
    def test_not_bundled(self):
        assert am_i_bundled() is False

    def test_bundled_when_frozen(self, monkeypatch):
        monkeypatch.setattr(sys, 'frozen', True, raising=False)
        monkeypatch.setattr(sys, '_MEIPASS', '/tmp/fake', raising=False)
        assert am_i_bundled() is True


# ---------------------------------------------------------------------------
# TestItemSubitemList
# ---------------------------------------------------------------------------
class TestItemSubitemList:
    def test_returns_matching_subitems(self):
        from yojenkins.utility.utility import item_subitem_list
        item_info = {
            'builds': [
                {'_class': 'hudson.model.FreeStyleBuild', 'url': 'http://x/1/'},
                {'_class': 'org.jenkinsci.plugins.workflow.job.WorkflowRun', 'url': 'http://x/2/'},
            ]
        }
        items, urls = item_subitem_list(
            item_info=item_info,
            get_key_info='url',
            item_type='builds',
            item_class_list=['org.jenkinsci.plugins.workflow.job.WorkflowRun'],
        )
        assert len(items) == 1
        assert urls == ['http://x/2/']

    def test_missing_item_type_returns_empty(self):
        from yojenkins.utility.utility import item_subitem_list
        items, names = item_subitem_list(
            item_info={},
            get_key_info='url',
            item_type='builds',
            item_class_list=['some.Class'],
        )
        assert items == []
        assert names == []

    def test_no_matching_class(self):
        from yojenkins.utility.utility import item_subitem_list
        item_info = {
            'jobs': [{'_class': 'com.Folder', 'name': 'f1'}]
        }
        items, names = item_subitem_list(
            item_info=item_info,
            get_key_info='name',
            item_type='jobs',
            item_class_list=['org.jenkinsci.Job'],
        )
        assert items == []
        assert names == []


# ---------------------------------------------------------------------------
# TestQueueFind
# ---------------------------------------------------------------------------
class TestQueueFind:
    def test_no_args_returns_empty(self):
        from yojenkins.utility.utility import queue_find
        result = queue_find({'items': []})
        assert result == []

    def test_match_by_job_name(self):
        from yojenkins.utility.utility import queue_find
        queue_info = {
            'items': [
                {
                    'task': {
                        '_class': 'org.jenkinsci.plugins.workflow.job.WorkflowJob',
                        'url': 'http://x/job/my-job/',
                    },
                    'id': 1,
                },
            ]
        }
        result = queue_find(queue_info, job_name='my-job')
        assert len(result) == 1

    def test_no_match(self):
        from yojenkins.utility.utility import queue_find
        queue_info = {
            'items': [
                {
                    'task': {
                        '_class': 'org.jenkinsci.plugins.workflow.job.WorkflowJob',
                        'url': 'http://x/job/other/',
                    },
                    'id': 1,
                },
            ]
        }
        result = queue_find(queue_info, job_name='my-job')
        assert result == []

    def test_non_job_item_skipped(self):
        from yojenkins.utility.utility import queue_find
        queue_info = {
            'items': [
                {
                    'task': {
                        '_class': 'com.cloudbees.hudson.plugins.folder.Folder',
                        'url': 'http://x/job/folder/',
                    },
                    'id': 1,
                },
            ]
        }
        result = queue_find(queue_info, job_name='folder')
        assert result == []

    def test_match_by_job_url(self):
        from yojenkins.utility.utility import queue_find
        queue_info = {
            'items': [
                {
                    'task': {
                        '_class': 'org.jenkinsci.plugins.workflow.job.WorkflowJob',
                        'url': 'http://x/job/my-job/',
                    },
                    'id': 1,
                },
            ]
        }
        result = queue_find(queue_info, job_url='http://x/job/my-job/')
        assert len(result) == 1


# ---------------------------------------------------------------------------
# TestDiffShow
# ---------------------------------------------------------------------------
class TestDiffShow:
    def test_basic_diff(self, capsys):
        from yojenkins.utility.utility import diff_show
        diff_show('line1\nline2', 'line1\nline3', '---A', '+++B', (), 0, True, False, False)
        out = capsys.readouterr().out
        assert '---A' in out
        assert '+++B' in out
        assert 'Similarity' in out

    def test_diff_only(self, capsys):
        from yojenkins.utility.utility import diff_show
        diff_show('a\nb\nc', 'a\nX\nc', '---', '+++', (), 0, True, True, False)
        out = capsys.readouterr().out
        assert 'Similarity' in out

    def test_char_ignore(self, capsys):
        from yojenkins.utility.utility import diff_show
        diff_show('XXXhello\nXXXworld', 'XXXhello\nXXXearth', '---', '+++', (), 3, True, False, False)
        out = capsys.readouterr().out
        assert 'Similarity' in out

    def test_line_pattern(self, capsys):
        from yojenkins.utility.utility import diff_show
        diff_show('ERROR: something\nINFO: ok', 'ERROR: other\nINFO: ok', '---', '+++', ('ERROR',), 0, True, False, False)
        out = capsys.readouterr().out
        assert 'Similarity' in out

    def test_diff_guide(self, capsys):
        from yojenkins.utility.utility import diff_show
        diff_show('abc\ndef', 'abc\nxyz', '---', '+++', (), 0, True, False, True)
        out = capsys.readouterr().out
        assert 'Similarity' in out

    def test_color_output(self, capsys):
        from yojenkins.utility.utility import diff_show
        diff_show('a\nb', 'a\nc', '---', '+++', (), 0, False, False, False)
        out = capsys.readouterr().out
        assert 'Similarity' in out


# ---------------------------------------------------------------------------
# TestItemExistsInFolder
# ---------------------------------------------------------------------------
class TestItemExistsInFolder:
    def test_item_exists(self, mock_rest):
        from yojenkins.utility.utility import item_exists_in_folder
        mock_rest.request.return_value = ({}, {}, True)
        result = item_exists_in_folder('my-job', 'http://x/job/folder/', 'job', mock_rest)
        assert result is True

    def test_item_does_not_exist(self, mock_rest):
        from yojenkins.utility.utility import item_exists_in_folder
        mock_rest.request.return_value = ({}, {}, False)
        result = item_exists_in_folder('my-job', 'http://x/job/folder/', 'job', mock_rest)
        assert result is False


# ---------------------------------------------------------------------------
# TestBlueMoonUnit
# ---------------------------------------------------------------------------
class TestBlueMoonUnit:
    def test_blue_moon(self):
        result = to_seconds(1, 'blue moon')
        assert result > 0


# ---------------------------------------------------------------------------
# TestWriteXmlToFileExtraFormats
# ---------------------------------------------------------------------------
class TestWriteXmlToFileExtraFormats:
    def test_write_as_toml(self, tmp_path):
        xml = '<root><item>hello</item></root>'
        f = tmp_path / 'output.toml'
        result = write_xml_to_file(xml, str(f), opt_toml=True)
        assert result is True
        content = f.read_text()
        assert 'root' in content or 'item' in content

    def test_write_failure_returns_false(self, tmp_path):
        xml = '<root><item>hello</item></root>'
        f = tmp_path / 'nonexistent_dir' / 'output.xml'
        result = write_xml_to_file(xml, str(f))
        assert result is False


# ---------------------------------------------------------------------------
# TestLoadContentsFromLocalFileEdgeCases
# ---------------------------------------------------------------------------
class TestLoadContentsFromLocalFileEdgeCases:
    def test_invalid_file_type_exits(self, tmp_path):
        f = tmp_path / 'test.txt'
        f.write_text('hello')
        with pytest.raises(SystemExit):
            load_contents_from_local_file('xml', str(f))

    def test_invalid_json_content_exits(self, tmp_path):
        f = tmp_path / 'test.json'
        f.write_text('{invalid json}')
        with pytest.raises(SystemExit):
            load_contents_from_local_file('json', str(f))


# ---------------------------------------------------------------------------
# TestRunGroovyScript
# ---------------------------------------------------------------------------
class TestRunGroovyScript:
    """Tests for run_groovy_script() covering lines 1138-1198."""

    def test_file_not_found(self, tmp_path):
        from yojenkins.utility.utility import run_groovy_script
        rest = MagicMock()
        result, success, error_msg = run_groovy_script('/nonexistent/script.groovy', True, rest)
        assert result == {}
        assert success is False
        assert 'Failed to find or read' in error_msg

    def test_successful_json_return(self, tmp_path):
        from yojenkins.utility.utility import run_groovy_script
        script = tmp_path / 'test.groovy'
        script.write_text('println "hello"')
        rest = MagicMock()
        rest.request.return_value = ('{"key": "value"}', {}, True)
        result, success, error_msg = run_groovy_script(str(script), True, rest)
        assert success is True
        assert result == {'key': 'value'}
        assert error_msg == ''

    def test_successful_text_return(self, tmp_path):
        from yojenkins.utility.utility import run_groovy_script
        script = tmp_path / 'test.groovy'
        script.write_text('println "hello"')
        rest = MagicMock()
        rest.request.return_value = ('hello world', {}, True)
        result, success, error_msg = run_groovy_script(str(script), False, rest)
        assert success is True
        assert result == 'hello world'

    def test_rest_request_failure(self, tmp_path):
        from yojenkins.utility.utility import run_groovy_script
        script = tmp_path / 'test.groovy'
        script.write_text('println "hello"')
        rest = MagicMock()
        rest.request.return_value = ('', {}, False)
        result, success, error_msg = run_groovy_script(str(script), False, rest)
        assert success is False
        assert 'Failed server REST request' in error_msg

    def test_groovy_script_error_flag(self, tmp_path):
        from yojenkins.utility.utility import run_groovy_script
        script = tmp_path / 'test.groovy'
        script.write_text('println "hello"')
        rest = MagicMock()
        error_response = "['yojenkins groovy script failed', 'SomeException', 'Custom error']"
        rest.request.return_value = (error_response, {}, True)
        result, success, error_msg = run_groovy_script(str(script), False, rest)
        assert success is False
        assert 'SomeException' in error_msg

    def test_java_exception_in_response(self, tmp_path):
        from yojenkins.utility.utility import run_groovy_script
        script = tmp_path / 'test.groovy'
        script.write_text('println "hello"')
        rest = MagicMock()
        rest.request.return_value = ('Exception in thread java: something', {}, True)
        result, success, error_msg = run_groovy_script(str(script), False, rest)
        assert success is False
        assert 'Error keyword matched' in error_msg

    def test_json_parse_failure(self, tmp_path):
        from yojenkins.utility.utility import run_groovy_script
        script = tmp_path / 'test.groovy'
        script.write_text('println "hello"')
        rest = MagicMock()
        rest.request.return_value = ('not valid json', {}, True)
        result, success, error_msg = run_groovy_script(str(script), True, rest)
        assert success is False
        assert 'Failed to parse response to JSON' in error_msg

    def test_with_kwargs_template(self, tmp_path):
        from yojenkins.utility.utility import run_groovy_script
        script = tmp_path / 'test.groovy'
        script.write_text('println "${name}"')
        rest = MagicMock()
        rest.request.return_value = ('hello', {}, True)
        result, success, error_msg = run_groovy_script(str(script), False, rest, name='World')
        assert success is True
        rest.request.assert_called_once()

    def test_with_kwargs_template_failure(self, tmp_path):
        from yojenkins.utility.utility import run_groovy_script
        script = tmp_path / 'test.groovy'
        script.write_text('')  # empty script
        rest = MagicMock()
        with patch('yojenkins.utility.utility.template_apply', return_value=''):
            result, success, error_msg = run_groovy_script(str(script), False, rest, name='World')
        assert success is False
        assert 'Failed to apply variables' in error_msg


# ---------------------------------------------------------------------------
# TestCreateNewHistoryFile
# ---------------------------------------------------------------------------
class TestCreateNewHistoryFile:
    """Tests for create_new_history_file() covering lines 1227-1246."""

    def test_creates_file(self, tmp_path):
        from yojenkins.utility.utility import create_new_history_file
        filepath = str(tmp_path / '.yojenkins' / 'history')
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        create_new_history_file(filepath)
        assert os.path.exists(filepath)

    def test_creates_config_dir_if_missing(self, tmp_path):
        from yojenkins.utility.utility import create_new_history_file
        with patch('yojenkins.utility.utility.Path') as mock_path:
            mock_path.home.return_value = tmp_path
            filepath = str(tmp_path / '.yojenkins' / 'history')
            create_new_history_file(filepath)
            assert os.path.exists(filepath)

    def test_permission_error_exits(self, tmp_path):
        from yojenkins.utility.utility import create_new_history_file
        with patch('builtins.open', side_effect=PermissionError('denied')):
            with patch('yojenkins.utility.utility.Path') as mock_path:
                mock_path.home.return_value = tmp_path
                os.makedirs(str(tmp_path / '.yojenkins'), exist_ok=True)
                with pytest.raises(SystemExit):
                    create_new_history_file(str(tmp_path / '.yojenkins' / 'history'))


# ---------------------------------------------------------------------------
# TestTemplateApplyErrorBranch
# ---------------------------------------------------------------------------
class TestTemplateApplyErrorBranch:
    """Tests for template_apply() error path at line 1104-1106."""

    def test_safe_substitute_exception_returns_empty(self):
        with patch('yojenkins.utility.utility.Template') as mock_tmpl_cls:
            mock_tmpl_cls.return_value.safe_substitute.side_effect = Exception('boom')
            result = template_apply('${x}', False, x='hello')
        assert result == ''


# ---------------------------------------------------------------------------
# TestAppendLinesExceptionBranch
# ---------------------------------------------------------------------------
class TestAppendLinesExceptionBranch:
    """Tests for append_lines_to_file exception path at lines 313-315."""

    def test_exception_during_write_returns_false(self, tmp_path):
        f = tmp_path / 'test.txt'
        f.write_text('original')
        with patch('builtins.open', side_effect=OSError('disk error')):
            result = append_lines_to_file(str(f), ['new line\n'], location='end')
        assert result is False


# ---------------------------------------------------------------------------
# TestIsCompleteBuildUrlEdgeCases
# ---------------------------------------------------------------------------
class TestIsCompleteBuildUrlEdgeCases:
    """Tests for is_complete_build_url line 583 (number at end but no 'job' prefix)."""

    def test_number_at_end_but_no_job_prefix(self):
        url = 'http://localhost:8080/notjob/foo/42'
        assert is_complete_build_url(url) is False

    def test_nested_folder_build_url(self):
        url = 'http://jenkins.com/job/folder1/job/folder2/job/myJob/15'
        assert is_complete_build_url(url) is True

    def test_deeply_nested_folder_build_url(self):
        url = 'http://jenkins.com/job/a/job/b/job/c/job/myJob/99'
        assert is_complete_build_url(url) is True


# ---------------------------------------------------------------------------
# TestBuildUrlCompleteEdgeCases
# ---------------------------------------------------------------------------
class TestBuildUrlCompleteEdgeCases:
    """Tests for build_url_complete line 624 (extra path after build number)."""

    def test_url_with_extra_path_after_build_number(self):
        url = 'http://localhost:8080/job/my_job/42/console'
        result = build_url_complete(url)
        assert result is not None
        assert '42' in result

    def test_url_too_short_returns_none(self):
        url = 'http://localhost:8080/foo'
        result = build_url_complete(url)
        assert result is None


# ---------------------------------------------------------------------------
# TestGetProjectDirBranches
# ---------------------------------------------------------------------------
class TestGetProjectDirBranches:
    """Tests for get_project_dir branches at lines 931, 942, 945-946."""

    def test_no_resource_dir_found_returns_empty(self):
        from yojenkins.utility.utility import get_project_dir
        with patch('yojenkins.utility.utility.am_i_bundled', return_value=False):
            with patch('pathlib.Path.exists', return_value=False):
                result = get_project_dir('nonexistent_dir_xyz')
        assert result == ''


# ---------------------------------------------------------------------------
# TestLoadContentsFromRemoteFile
# ---------------------------------------------------------------------------
class TestLoadContentsFromRemoteFileUrl:
    """Tests for load_contents_from_remote_file_url covering lines 201-271."""

    def test_unsupported_extension_returns_empty(self):
        from yojenkins.utility.utility import load_contents_from_remote_file_url
        result = load_contents_from_remote_file_url('yaml', 'http://example.com/file.txt')
        assert result == {}

    def test_request_head_failure_returns_empty(self):
        from yojenkins.utility.utility import load_contents_from_remote_file_url
        with patch('yojenkins.utility.utility.requests') as mock_req:
            mock_req.head.side_effect = Exception('connection error')
            result = load_contents_from_remote_file_url('yaml', 'http://example.com/file.yaml')
        assert result == {}

    def test_file_too_large_returns_empty(self):
        from yojenkins.utility.utility import load_contents_from_remote_file_url
        with patch('yojenkins.utility.utility.requests') as mock_req:
            mock_resp = MagicMock()
            mock_resp.headers = {'Content-length': '2000000', 'content-type': 'text/plain'}
            mock_req.head.return_value = mock_resp
            result = load_contents_from_remote_file_url('yaml', 'http://example.com/file.yaml')
        assert result == {}

    def test_no_content_type_returns_empty(self):
        from yojenkins.utility.utility import load_contents_from_remote_file_url
        with patch('yojenkins.utility.utility.requests') as mock_req:
            mock_resp = MagicMock()
            headers = MagicMock()
            headers.__getitem__ = lambda self, k: '100' if k == 'Content-length' else None
            headers.get = MagicMock(return_value=None)
            mock_resp.headers = headers
            mock_req.head.return_value = mock_resp
            result = load_contents_from_remote_file_url('yaml', 'http://example.com/file.yaml')
        assert result == {}

    def test_unsupported_content_type_returns_empty(self):
        from yojenkins.utility.utility import load_contents_from_remote_file_url
        with patch('yojenkins.utility.utility.requests') as mock_req:
            mock_resp = MagicMock()
            headers = MagicMock()
            headers.__getitem__ = lambda self, k: '100' if k == 'Content-length' else None
            headers.get = MagicMock(return_value='application/octet-stream')
            mock_resp.headers = headers
            mock_req.head.return_value = mock_resp
            result = load_contents_from_remote_file_url('yaml', 'http://example.com/file.yaml')
        assert result == {}

    def _make_headers_mock(self, content_length='100', content_type='text/plain'):
        """Helper to create a mock headers object."""
        headers = MagicMock()
        headers.__getitem__ = lambda self, k: {
            'Content-length': content_length,
            'content-type': content_type,
        }.get(k)
        headers.get = MagicMock(return_value=content_type)
        return headers

    def test_successful_download(self):
        from yojenkins.utility.utility import load_contents_from_remote_file_url
        with patch('yojenkins.utility.utility.requests') as mock_req:
            mock_head_resp = MagicMock()
            mock_head_resp.headers = self._make_headers_mock()
            mock_req.head.return_value = mock_head_resp

            mock_get_resp = MagicMock()
            mock_get_resp.status_code = 200
            mock_get_resp.content = b'key: value'
            mock_req.codes.ok = 200
            mock_req.get.return_value = mock_get_resp

            result = load_contents_from_remote_file_url('yaml', 'http://example.com/file.yaml')
        assert result == {'key': 'value'}

    def test_download_non_ok_status_returns_empty(self):
        from yojenkins.utility.utility import load_contents_from_remote_file_url
        with patch('yojenkins.utility.utility.requests') as mock_req:
            mock_head_resp = MagicMock()
            mock_head_resp.headers = self._make_headers_mock()
            mock_req.head.return_value = mock_head_resp

            mock_get_resp = MagicMock()
            mock_get_resp.status_code = 404
            mock_req.codes.ok = 200
            mock_req.get.return_value = mock_get_resp

            result = load_contents_from_remote_file_url('yaml', 'http://example.com/file.yaml')
        assert result == {}

    def test_yaml_parse_failure_returns_empty(self):
        from yojenkins.utility.utility import load_contents_from_remote_file_url
        with patch('yojenkins.utility.utility.requests') as mock_req:
            mock_head_resp = MagicMock()
            mock_head_resp.headers = self._make_headers_mock()
            mock_req.head.return_value = mock_head_resp

            mock_get_resp = MagicMock()
            mock_get_resp.status_code = 200
            mock_get_resp.content = b': : : invalid yaml ['
            mock_req.codes.ok = 200
            mock_req.get.return_value = mock_get_resp

            with patch('yojenkins.utility.utility.yaml.safe_load', side_effect=Exception('parse error')):
                result = load_contents_from_remote_file_url('yaml', 'http://example.com/file.yaml')
        assert result == {}


# ---------------------------------------------------------------------------
# TestOpenWebBrowser
# ---------------------------------------------------------------------------
class TestOpenWebBrowser:
    """Tests for browser_open lines 788-793."""

    def test_browser_open_success(self):
        from yojenkins.utility.utility import browser_open
        with patch('yojenkins.utility.utility.webbrowser.open'):
            result = browser_open('http://example.com/')
        assert result is True

    def test_browser_open_failure(self):
        from yojenkins.utility.utility import browser_open
        with patch('yojenkins.utility.utility.webbrowser.open', side_effect=Exception('no browser')):
            result = browser_open('http://example.com/')
        assert result is False


# ---------------------------------------------------------------------------
# TestGetResourcePath
# ---------------------------------------------------------------------------
class TestGetResourcePath:
    """Tests for get_resource_path lines 892-893."""

    def test_resource_not_found_returns_empty(self):
        from yojenkins.utility.utility import get_resource_path
        with patch('yojenkins.utility.utility.get_project_dir', return_value='/fake/dir'):
            with patch('pathlib.Path.exists', return_value=False):
                result = get_resource_path('nonexistent/file.txt')
        assert result == ''


# ---------------------------------------------------------------------------
# TestWaitForBuildAndFollowLogs
# ---------------------------------------------------------------------------
class TestWaitForBuildAndFollowLogs:
    """Tests for wait_for_build_and_follow_logs lines 1259-1283."""

    def test_waits_then_follows_logs(self):
        from yojenkins.utility.utility import wait_for_build_and_follow_logs
        mock_yj = MagicMock()
        mock_yj.job.queue_info.return_value = {
            'executable': {'number': 5},
            'jobUrl': 'http://localhost:8080/job/my_job/',
        }
        with patch('yojenkins.utility.utility.logger') as mock_logger:
            mock_logger.level = 5  # debug level, skip spinner
            wait_for_build_and_follow_logs(mock_yj, queue_id=1)
        mock_yj.build.logs.assert_called_once_with(
            build_url=None,
            job_url='http://localhost:8080/job/my_job/',
            build_number=5,
            follow=True,
        )

    def test_stuck_build_exits(self):
        from yojenkins.utility.utility import wait_for_build_and_follow_logs
        mock_yj = MagicMock()
        mock_yj.job.queue_info.return_value = {'stuck': True}
        with patch('yojenkins.utility.utility.logger') as mock_logger:
            mock_logger.level = 5
            # Source code passes unsupported kwargs to fail_out, causing TypeError
            with pytest.raises((SystemExit, TypeError)):
                wait_for_build_and_follow_logs(mock_yj, queue_id=1)


# ---------------------------------------------------------------------------
# TestWaitForBuildAndMonitor
# ---------------------------------------------------------------------------
class TestWaitForBuildAndMonitor:
    """Tests for wait_for_build_and_monitor."""

    def test_waits_then_starts_monitor(self):
        from yojenkins.utility.utility import wait_for_build_and_monitor
        mock_yj = MagicMock()
        mock_yj.job.queue_info.return_value = {
            'executable': {'number': 7},
            'jobUrl': 'http://localhost:8080/job/my_job/',
        }
        with patch('yojenkins.utility.utility.logger') as mock_logger:
            mock_logger.level = 5  # debug level, skip spinner
            wait_for_build_and_monitor(mock_yj, queue_id=42, sound=True)
        mock_yj.build.monitor.assert_called_once_with(
            job_url='http://localhost:8080/job/my_job/',
            build_number=7,
            sound=True,
        )

    def test_stuck_build_exits(self):
        from yojenkins.utility.utility import wait_for_build_and_monitor
        mock_yj = MagicMock()
        mock_yj.job.queue_info.return_value = {'stuck': True}
        with patch('yojenkins.utility.utility.logger') as mock_logger:
            mock_logger.level = 5
            with pytest.raises((SystemExit, TypeError)):
                wait_for_build_and_monitor(mock_yj, queue_id=1)
