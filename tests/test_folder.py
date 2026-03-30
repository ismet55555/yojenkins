"""Tests for yojenkins/yo_jenkins/folder.py"""

from unittest.mock import MagicMock, patch

import pytest

from yojenkins.yo_jenkins.exceptions import YoJenkinsException
from yojenkins.yo_jenkins.folder import Folder
from yojenkins.yo_jenkins.jenkins_item_classes import JenkinsItemClasses

FOLDER_CLASS = JenkinsItemClasses.FOLDER.value['class_type'][0]
JOB_CLASS = JenkinsItemClasses.JOB.value['class_type'][0]
VIEW_CLASS = JenkinsItemClasses.VIEW.value['class_type'][0]


@pytest.fixture
def folder_obj(mock_rest):
    """Create a Folder instance with mocked rest and jenkins_sdk."""
    jenkins_sdk = MagicMock()
    mock_rest.get_server_url = MagicMock(return_value='http://localhost:8080/')
    return Folder(mock_rest, jenkins_sdk)


# ---------- Constructor ----------

class TestConstructor:
    def test_init_sets_rest_and_sdk(self, mock_rest):
        sdk = MagicMock()
        f = Folder(mock_rest, sdk)
        assert f.rest is mock_rest
        assert f.jenkins_sdk is sdk
        assert f.search_results == []
        assert f.search_items_count == 0


# ---------- info ----------

class TestInfo:
    def test_info_by_url(self, folder_obj):
        folder_data = {
            '_class': FOLDER_CLASS,
            'name': 'my-folder',
            'url': 'http://localhost:8080/job/my-folder/',
        }
        folder_obj.rest.request.return_value = (folder_data, {}, True)

        result = folder_obj.info(folder_url='http://localhost:8080/job/my-folder/')
        assert result == folder_data
        folder_obj.rest.request.assert_called_once_with(
            'http://localhost:8080/job/my-folder/api/json',
            request_type='get',
            is_endpoint=False,
        )

    def test_info_by_name(self, folder_obj):
        folder_data = {
            '_class': FOLDER_CLASS,
            'name': 'my-folder',
            'url': 'http://localhost:8080/job/my-folder/',
        }
        folder_obj.rest.request.return_value = (folder_data, {}, True)

        result = folder_obj.info(folder_name='my-folder')
        assert result['name'] == 'my-folder'

    def test_info_no_args_exits(self, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.info()

    def test_info_request_failure_exits(self, folder_obj):
        folder_obj.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            folder_obj.info(folder_url='http://localhost:8080/job/bad/')

    def test_info_wrong_class_exits(self, folder_obj):
        folder_data = {
            '_class': JOB_CLASS,
            'name': 'not-a-folder',
        }
        folder_obj.rest.request.return_value = (folder_data, {}, True)
        with pytest.raises(YoJenkinsException):
            folder_obj.info(folder_url='http://localhost:8080/job/not-a-folder/')


# ---------- __recursive_search ----------

class TestRecursiveSearch:
    def test_empty_folder(self, folder_obj):
        folder_obj._Folder__recursive_search('.*', [], 0)
        assert folder_obj.search_results == []
        assert folder_obj.search_items_count == 0

    def test_single_level_match(self, folder_obj):
        items = [
            {'_class': FOLDER_CLASS, 'name': 'alpha', 'fullname': 'alpha', 'url': 'http://x/job/alpha/'},
            {'_class': JOB_CLASS, 'name': 'beta', 'url': 'http://x/job/beta/'},
        ]
        folder_obj.search_results = []
        folder_obj.search_items_count = 0
        folder_obj._Folder__recursive_search('alpha', items, 0)
        assert len(folder_obj.search_results) == 1
        assert folder_obj.search_results[0]['name'] == 'alpha'
        assert folder_obj.search_items_count == 2

    def test_multi_level_nesting(self, folder_obj):
        nested = {
            '_class': FOLDER_CLASS,
            'name': 'child',
            'fullname': 'parent/child',
            'url': 'http://x/job/parent/job/child/',
        }
        items = [
            {
                '_class': FOLDER_CLASS,
                'name': 'parent',
                'fullname': 'parent',
                'url': 'http://x/job/parent/',
                'jobs': [nested],
            },
        ]
        folder_obj.search_results = []
        folder_obj.search_items_count = 0
        folder_obj._Folder__recursive_search('child', items, 0)
        assert len(folder_obj.search_results) == 1
        assert folder_obj.search_results[0]['name'] == 'child'

    def test_fullname_false_uses_name_key(self, folder_obj):
        items = [
            {
                '_class': FOLDER_CLASS,
                'name': 'leaf',
                'fullname': 'root/leaf',
                'url': 'http://x/job/root/job/leaf/',
            },
        ]
        folder_obj.search_results = []
        folder_obj.search_items_count = 0
        # Pattern that matches 'root/leaf' (fullname) but not 'leaf' (name)
        folder_obj._Folder__recursive_search('root/', items, 0, fullname=True)
        assert len(folder_obj.search_results) == 1

        folder_obj.search_results = []
        folder_obj.search_items_count = 0
        folder_obj._Folder__recursive_search('root/', items, 0, fullname=False)
        assert len(folder_obj.search_results) == 0

    def test_regex_match(self, folder_obj):
        items = [
            {'_class': FOLDER_CLASS, 'name': 'deploy-prod', 'fullname': 'deploy-prod', 'url': 'http://x/1/'},
            {'_class': FOLDER_CLASS, 'name': 'deploy-staging', 'fullname': 'deploy-staging', 'url': 'http://x/2/'},
            {'_class': FOLDER_CLASS, 'name': 'test-unit', 'fullname': 'test-unit', 'url': 'http://x/3/'},
        ]
        folder_obj.search_results = []
        folder_obj.search_items_count = 0
        folder_obj._Folder__recursive_search('^deploy', items, 0)
        assert len(folder_obj.search_results) == 2

    def test_invalid_regex_does_not_crash(self, folder_obj):
        items = [
            {'_class': FOLDER_CLASS, 'name': 'abc', 'fullname': 'abc', 'url': 'http://x/1/'},
        ]
        folder_obj.search_results = []
        folder_obj.search_items_count = 0
        folder_obj._Folder__recursive_search('[invalid', items, 0)
        assert folder_obj.search_results == []

    def test_non_folder_items_not_matched(self, folder_obj):
        items = [
            {'_class': JOB_CLASS, 'name': 'my-job', 'fullname': 'my-job', 'url': 'http://x/1/'},
        ]
        folder_obj.search_results = []
        folder_obj.search_items_count = 0
        folder_obj._Folder__recursive_search('my-job', items, 0)
        assert len(folder_obj.search_results) == 0
        assert folder_obj.search_items_count == 1


# ---------- search ----------

class TestSearch:
    def test_search_entire_jenkins(self, folder_obj):
        folder_obj.jenkins_sdk.get_all_jobs.return_value = [
            {'_class': FOLDER_CLASS, 'name': 'target', 'fullname': 'target', 'url': 'http://x/job/target/'},
        ]
        results, urls = folder_obj.search('target')
        assert len(results) == 1
        assert urls == ['http://x/job/target/']

    @patch('yojenkins.yo_jenkins.folder.utility.name_to_url', return_value='http://localhost:8080/job/parent')
    def test_search_within_folder(self, mock_name_to_url, folder_obj):
        subfolder = {'_class': FOLDER_CLASS, 'name': 'child', 'fullname': 'parent/child', 'url': 'http://x/1/'}
        folder_info = {
            '_class': FOLDER_CLASS,
            'name': 'parent',
            'url': 'http://localhost:8080/job/parent/',
            'jobs': [subfolder],
        }
        folder_obj.rest.request.return_value = (folder_info, {}, True)
        results, urls = folder_obj.search('child', folder_name='parent')
        assert len(results) == 1


# ---------- subfolder_list ----------

class TestSubfolderList:
    @patch('yojenkins.yo_jenkins.folder.utility.item_subitem_list')
    def test_returns_expected_data(self, mock_subitem_list, folder_obj):
        folder_data = {'_class': FOLDER_CLASS, 'name': 'root', 'url': 'http://x/', 'jobs': []}
        folder_obj.rest.request.return_value = (folder_data, {}, True)
        expected_items = [{'name': 'sub1'}]
        expected_urls = ['http://x/job/sub1/']
        mock_subitem_list.return_value = (expected_items, expected_urls)

        items, urls = folder_obj.subfolder_list(folder_url='http://x/')
        assert items == expected_items
        assert urls == expected_urls

    @patch('yojenkins.yo_jenkins.folder.utility.item_subitem_list')
    def test_empty_subfolders(self, mock_subitem_list, folder_obj):
        folder_data = {'_class': FOLDER_CLASS, 'name': 'root', 'url': 'http://x/', 'jobs': []}
        folder_obj.rest.request.return_value = (folder_data, {}, True)
        mock_subitem_list.return_value = ([], [])

        items, urls = folder_obj.subfolder_list(folder_url='http://x/')
        assert items == []
        assert urls == []


# ---------- jobs_list ----------

class TestJobsList:
    @patch('yojenkins.yo_jenkins.folder.utility.item_subitem_list')
    def test_returns_jobs(self, mock_subitem_list, folder_obj):
        folder_data = {'_class': FOLDER_CLASS, 'name': 'root', 'url': 'http://x/', 'jobs': []}
        folder_obj.rest.request.return_value = (folder_data, {}, True)
        mock_subitem_list.return_value = ([{'name': 'job1'}], ['http://x/job/job1/'])

        items, urls = folder_obj.jobs_list(folder_url='http://x/')
        assert len(items) == 1

    @patch('yojenkins.yo_jenkins.folder.utility.item_subitem_list')
    def test_empty_jobs(self, mock_subitem_list, folder_obj):
        folder_data = {'_class': FOLDER_CLASS, 'name': 'root', 'url': 'http://x/', 'jobs': []}
        folder_obj.rest.request.return_value = (folder_data, {}, True)
        mock_subitem_list.return_value = ([], [])

        items, urls = folder_obj.jobs_list(folder_url='http://x/')
        assert items == []


# ---------- view_list ----------

class TestViewList:
    @patch('yojenkins.yo_jenkins.folder.utility.item_subitem_list')
    def test_returns_views(self, mock_subitem_list, folder_obj):
        folder_data = {'_class': FOLDER_CLASS, 'name': 'root', 'url': 'http://x/', 'views': []}
        folder_obj.rest.request.return_value = (folder_data, {}, True)
        mock_subitem_list.return_value = ([{'name': 'view1'}], ['http://x/view/view1/'])

        items, urls = folder_obj.view_list(folder_url='http://x/')
        assert len(items) == 1


# ---------- config ----------

class TestConfig:
    def test_get_config_xml(self, folder_obj):
        xml_content = '<folder><description>test</description></folder>'
        folder_obj.rest.request.return_value = (xml_content, {}, True)

        result = folder_obj.config(folder_url='http://localhost:8080/job/my-folder/')
        assert result == xml_content
        folder_obj.rest.request.assert_called_once_with(
            'http://localhost:8080/job/my-folder/config.xml',
            'get',
            json_content=False,
            is_endpoint=False,
        )

    def test_config_no_args_exits(self, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.config()

    def test_config_request_failure_exits(self, folder_obj):
        folder_obj.rest.request.return_value = ('', {}, False)
        with pytest.raises(YoJenkinsException):
            folder_obj.config(folder_url='http://localhost:8080/job/bad/')

    @patch('yojenkins.yo_jenkins.folder.utility.write_xml_to_file', return_value=True)
    def test_config_writes_to_file(self, mock_write, folder_obj):
        xml_content = '<folder/>'
        folder_obj.rest.request.return_value = (xml_content, {}, True)

        result = folder_obj.config(filepath='/tmp/config.xml', folder_url='http://localhost:8080/job/f/')
        assert result == xml_content
        mock_write.assert_called_once()


# ---------- create ----------

class TestCreate:
    def test_create_no_folder_exits(self, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.create(name='new-folder')

    def test_create_blank_name_exits(self, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.create(name='', folder_url='http://localhost:8080/job/parent/')

    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=True)
    def test_create_special_chars_exits(self, mock_special, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.create(name='bad@name', folder_url='http://localhost:8080/job/parent/')

    @patch('yojenkins.yo_jenkins.folder.utility.item_exists_in_folder', return_value=False)
    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_create_success_no_config_file(self, mock_special, mock_exists, folder_obj):
        folder_obj.rest.request.return_value = ({}, {}, True)
        result = folder_obj.create(name='new-folder', folder_url='http://localhost:8080/job/parent/', config='')
        assert result is True

    @patch('yojenkins.yo_jenkins.folder.utility.item_exists_in_folder', return_value=True)
    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_create_already_exists_exits(self, mock_special, mock_exists, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.create(name='existing', folder_url='http://localhost:8080/job/parent/', config='')


# ---------- copy ----------

class TestCopy:
    def test_copy_no_folder_exits(self, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.copy('orig', 'new')

    @patch('yojenkins.yo_jenkins.folder.utility.item_exists_in_folder', return_value=True)
    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_copy_success(self, mock_special, mock_exists, folder_obj):
        folder_obj.rest.request.return_value = ({}, {}, True)
        result = folder_obj.copy('orig', 'new', folder_url='http://localhost:8080/job/parent/')
        assert result is True

    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_copy_original_not_found_exits(self, mock_special, folder_obj):
        with patch('yojenkins.yo_jenkins.folder.utility.item_exists_in_folder', return_value=False):
            with pytest.raises(YoJenkinsException):
                folder_obj.copy('missing', 'new', folder_url='http://localhost:8080/job/parent/')


# ---------- delete ----------

class TestDelete:
    def test_delete_no_args_exits(self, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.delete()

    def test_delete_success_by_url(self, folder_obj):
        folder_obj.rest.request.return_value = ({}, {}, True)
        result = folder_obj.delete(folder_url='http://localhost:8080/job/my-folder/')
        assert result is True
        folder_obj.rest.request.assert_called_once_with(
            'http://localhost:8080/job/my-folder/doDelete',
            'post',
            is_endpoint=False,
        )

    def test_delete_failure_exits(self, folder_obj):
        folder_obj.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            folder_obj.delete(folder_url='http://localhost:8080/job/my-folder/')

    def test_delete_by_name(self, folder_obj):
        folder_obj.rest.request.return_value = ({}, {}, True)
        result = folder_obj.delete(folder_name='my-folder')
        assert result is True


# ---------- browser_open ----------

class TestBrowserOpen:
    @patch('yojenkins.yo_jenkins.folder.utility.browser_open', return_value=True)
    def test_browser_open_by_url(self, mock_browser, folder_obj):
        result = folder_obj.browser_open(folder_url='http://localhost:8080/job/my-folder/')
        assert result is True

    def test_browser_open_no_args_exits(self, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.browser_open()

    @patch('yojenkins.yo_jenkins.folder.utility.browser_open', return_value=False)
    def test_browser_open_failure_exits(self, mock_browser, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.browser_open(folder_url='http://localhost:8080/job/my-folder/')


# ---------- config edge cases ----------

class TestConfigEdgeCases:
    def test_config_by_name(self, folder_obj):
        xml_content = '<folder/>'
        folder_obj.rest.request.return_value = (xml_content, {}, True)
        result = folder_obj.config(folder_name='my-folder')
        assert result == xml_content


# ---------- item_list ----------

class TestItemList:
    def test_item_list_returns_all_items(self, folder_obj):
        folder_data = {
            '_class': FOLDER_CLASS,
            'name': 'root',
            'url': 'http://x/',
            'jobs': [
                {'_class': JOB_CLASS, 'name': 'job1', 'url': 'http://x/job/job1/', 'fullname': 'job1'},
                {'_class': FOLDER_CLASS, 'name': 'sub', 'url': 'http://x/job/sub/', 'fullname': 'sub'},
            ],
        }
        folder_obj.rest.request.return_value = (folder_data, {}, True)
        items, urls = folder_obj.item_list(folder_url='http://x/')
        assert len(items) == 2
        assert len(urls) == 2

    def test_item_list_no_args_exits(self, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.item_list()


# ---------- create edge cases ----------

class TestCreateEdgeCases:
    @patch('yojenkins.yo_jenkins.folder.utility.item_exists_in_folder', return_value=False)
    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_create_request_failure_exits(self, mock_special, mock_exists, folder_obj):
        folder_obj.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            folder_obj.create(name='new-folder', folder_url='http://localhost:8080/job/parent/', config='')

    @patch('yojenkins.yo_jenkins.folder.utility.item_exists_in_folder', return_value=False)
    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_create_view_type(self, mock_special, mock_exists, folder_obj):
        folder_obj.rest.request.return_value = ({}, {}, True)
        result = folder_obj.create(
            name='new-view',
            folder_url='http://localhost:8080/job/parent/',
            config='',
            type='view',
        )
        assert result is True

    @patch('yojenkins.yo_jenkins.folder.utility.item_exists_in_folder', return_value=False)
    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_create_job_type(self, mock_special, mock_exists, folder_obj):
        folder_obj.rest.request.return_value = ({}, {}, True)
        result = folder_obj.create(
            name='new-job',
            folder_url='http://localhost:8080/job/parent/',
            config='',
            type='job',
        )
        assert result is True

    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_create_unsupported_type_exits(self, mock_special, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.create(
                name='item',
                folder_url='http://localhost:8080/job/parent/',
                config='',
                type='pipeline',
            )


# ---------- copy edge cases ----------

class TestCopyEdgeCases:
    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_copy_blank_original_exits(self, mock_special, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.copy('', 'new', folder_url='http://localhost:8080/job/parent/')

    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_copy_blank_new_name_exits(self, mock_special, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.copy('orig', '', folder_url='http://localhost:8080/job/parent/')

    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', side_effect=[False, True])
    def test_copy_special_char_new_name_exits(self, mock_special, folder_obj):
        with pytest.raises(YoJenkinsException):
            folder_obj.copy('orig', 'bad@name', folder_url='http://localhost:8080/job/parent/')

    @patch('yojenkins.yo_jenkins.folder.utility.item_exists_in_folder', return_value=True)
    @patch('yojenkins.yo_jenkins.folder.utility.has_special_char', return_value=False)
    def test_copy_request_failure_exits(self, mock_special, mock_exists, folder_obj):
        folder_obj.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            folder_obj.copy('orig', 'new', folder_url='http://localhost:8080/job/parent/')
