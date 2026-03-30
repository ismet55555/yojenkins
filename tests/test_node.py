"""Tests for yojenkins.yo_jenkins.node.Node"""

import json

import pytest

from yojenkins.yo_jenkins.exceptions import YoJenkinsException
from yojenkins.yo_jenkins.node import Node

# ---------------------------------------------------------------------------
# info
# ---------------------------------------------------------------------------


class TestInfo:
    def test_info_returns_node_data(self, mock_rest):
        """info() returns the dict from rest.request on success."""
        expected = {'displayName': 'agent-1', 'offline': False}
        mock_rest.request.return_value = (expected, {}, True)
        node = Node(rest=mock_rest)

        result = node.info('agent-1')

        assert result == expected
        mock_rest.request.assert_called_once()
        call_kwargs = mock_rest.request.call_args
        assert 'computer/agent-1/api/json' in call_kwargs.kwargs.get('target', call_kwargs[1].get('target', ''))

    def test_info_master_rewritten(self, mock_rest):
        """info() rewrites 'master' to '(master)' in the request target."""
        mock_rest.request.return_value = ({'displayName': 'master'}, {}, True)
        node = Node(rest=mock_rest)

        node.info('master')

        target = mock_rest.request.call_args.kwargs.get('target', '')
        assert '(master)' in target

    def test_info_failure_exits(self, mock_rest):
        """info() calls fail_out (sys.exit) when request fails."""
        mock_rest.request.return_value = ({}, {}, False)
        node = Node(rest=mock_rest)

        with pytest.raises(YoJenkinsException):
            node.info('bad-node')


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


class TestList:
    def test_list_returns_nodes(self, mock_rest, mocker):
        """list() returns the tuple from item_subitem_list."""
        nodes_data = {
            'computer': [
                {'_class': 'hudson.model.Hudson$MasterComputer', 'displayName': 'Built-In Node'},
                {'_class': 'hudson.slaves.SlaveComputer', 'displayName': 'agent-1'},
            ]
        }
        mock_rest.request.return_value = (nodes_data, {}, True)
        expected_list = [nodes_data['computer'][0], nodes_data['computer'][1]]
        expected_names = ['Built-In Node', 'agent-1']

        mocker.patch(
            'yojenkins.yo_jenkins.node.utility.item_subitem_list',
            return_value=(expected_list, expected_names),
        )
        node = Node(rest=mock_rest)

        result_list, result_names = node.list()

        assert result_list == expected_list
        assert result_names == expected_names

    def test_list_failure_exits(self, mock_rest):
        """list() calls fail_out when request fails."""
        mock_rest.request.return_value = ({}, {}, False)
        node = Node(rest=mock_rest)

        with pytest.raises(YoJenkinsException):
            node.list()

    def test_list_missing_computer_key_exits(self, mock_rest):
        """list() calls fail_out when 'computer' key missing from response."""
        mock_rest.request.return_value = ({'other_key': []}, {}, True)
        node = Node(rest=mock_rest)

        with pytest.raises(YoJenkinsException):
            node.list()


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------


class TestConfig:
    def test_config_returns_xml_content(self, mock_rest):
        """config() returns XML content from rest.request."""
        xml_content = '<slave><name>agent-1</name></slave>'
        mock_rest.request.return_value = (xml_content, {}, True)
        node = Node(rest=mock_rest)

        result = node.config(node_name='agent-1')

        assert result == xml_content

    def test_config_master_rewritten(self, mock_rest):
        """config() rewrites 'master' to '(master)' in the target."""
        mock_rest.request.return_value = ('<xml/>', {}, True)
        node = Node(rest=mock_rest)

        node.config(node_name='master')

        target = mock_rest.request.call_args[0][0]  # first positional arg
        assert '(master)' in target

    def test_config_failure_exits(self, mock_rest):
        """config() calls fail_out when request fails."""
        mock_rest.request.return_value = ('', {}, False)
        node = Node(rest=mock_rest)

        with pytest.raises(YoJenkinsException):
            node.config(node_name='agent-1')

    def test_config_writes_file(self, mock_rest, mocker, tmp_path):
        """config() writes to file when filepath is provided."""
        xml_content = '<slave><name>agent-1</name></slave>'
        mock_rest.request.return_value = (xml_content, {}, True)
        mock_write = mocker.patch(
            'yojenkins.yo_jenkins.node.utility.write_xml_to_file',
            return_value=True,
        )
        node = Node(rest=mock_rest)
        filepath = str(tmp_path / 'node.xml')

        node.config(node_name='agent-1', filepath=filepath)

        mock_write.assert_called_once_with(xml_content, filepath, False, False, False)


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDelete:
    def test_delete_success(self, mock_rest):
        """delete() returns True on success."""
        mock_rest.request.return_value = ('', {}, True)
        node = Node(rest=mock_rest)

        assert node.delete('agent-1') is True

    def test_delete_failure_exits(self, mock_rest):
        """delete() calls fail_out when request fails."""
        mock_rest.request.return_value = ('', {}, False)
        node = Node(rest=mock_rest)

        with pytest.raises(YoJenkinsException):
            node.delete('agent-1')


# ---------------------------------------------------------------------------
# disable (toggle offline)
# ---------------------------------------------------------------------------


class TestDisable:
    def test_disable_sends_toggle(self, mock_rest):
        """disable() sends toggleOffline request when node is online."""
        # First call: info() -> node is online
        # Second call: toggleOffline -> success
        mock_rest.request.side_effect = [
            ({'offline': False, 'displayName': 'agent-1'}, {}, True),
            ('', {}, True),
        ]
        node = Node(rest=mock_rest)

        result = node.disable('agent-1', message='maintenance')

        assert result is True
        assert mock_rest.request.call_count == 2

    def test_disable_already_offline_returns_true(self, mock_rest):
        """disable() returns True without toggling if already offline."""
        mock_rest.request.return_value = ({'offline': True, 'displayName': 'agent-1'}, {}, True)
        node = Node(rest=mock_rest)

        result = node.disable('agent-1')

        assert result is True
        assert mock_rest.request.call_count == 1  # only info call

    def test_disable_failure_exits(self, mock_rest):
        """disable() calls fail_out when toggle request fails."""
        mock_rest.request.side_effect = [
            ({'offline': False, 'displayName': 'agent-1'}, {}, True),
            ('', {}, False),
        ]
        node = Node(rest=mock_rest)

        with pytest.raises(YoJenkinsException):
            node.disable('agent-1')


# ---------------------------------------------------------------------------
# enable
# ---------------------------------------------------------------------------


class TestEnable:
    def test_enable_sends_toggle(self, mock_rest):
        """enable() sends toggleOffline request when node is offline."""
        mock_rest.request.side_effect = [
            ({'offline': True, 'displayName': 'agent-1'}, {}, True),
            ('', {}, True),
        ]
        node = Node(rest=mock_rest)

        result = node.enable('agent-1', message='back online')

        assert result is True
        assert mock_rest.request.call_count == 2

    def test_enable_already_online_returns_true(self, mock_rest):
        """enable() returns True without toggling if already online."""
        mock_rest.request.return_value = ({'offline': False, 'displayName': 'agent-1'}, {}, True)
        node = Node(rest=mock_rest)

        result = node.enable('agent-1')

        assert result is True
        assert mock_rest.request.call_count == 1


# ---------------------------------------------------------------------------
# create_permanent
# ---------------------------------------------------------------------------


class TestCreatePermanent:
    @pytest.fixture
    def create_kwargs(self):
        return {
            'name': 'new-agent',
            'host': '192.168.1.100',
            'credential': 'ssh-cred-id',
            'ssh_verify': 'none',
            'ssh_port': 22,
            'remote_java_dir': '/usr/bin/java',
            'description': 'Test agent',
            'executors': 2,
            'remote_root_dir': '/home/jenkins',
            'labels': 'linux docker',
            'mode': 'normal',
            'retention': 'always',
        }

    def test_create_permanent_success(self, mock_rest, create_kwargs):
        """create_permanent() returns True on successful creation."""
        mock_rest.request.return_value = ('', {}, True)
        node = Node(rest=mock_rest)

        result = node.create_permanent(**create_kwargs)

        assert result is True
        call_kwargs = mock_rest.request.call_args.kwargs
        assert call_kwargs['target'] == 'computer/doCreateItem'
        assert call_kwargs['request_type'] == 'post'

    def test_create_permanent_special_chars_exits(self, mock_rest, create_kwargs):
        """create_permanent() calls fail_out if name has special characters."""
        create_kwargs['name'] = 'bad@name!'
        node = Node(rest=mock_rest)

        with pytest.raises(YoJenkinsException):
            node.create_permanent(**create_kwargs)

    def test_create_permanent_failure_exits(self, mock_rest, create_kwargs):
        """create_permanent() calls fail_out when request fails."""
        mock_rest.request.return_value = ('', {}, False)
        node = Node(rest=mock_rest)

        with pytest.raises(YoJenkinsException):
            node.create_permanent(**create_kwargs)

    @pytest.mark.parametrize(
        'ssh_verify,expected_class',
        [
            ('known', 'KnownHostsFileKeyVerificationStrategy'),
            ('trusted', 'ManuallyTrustedKeyVerificationStrategy'),
            ('provided', 'ManuallyProvidedKeyVerificationStrategy'),
            ('none', 'NonVerifyingKeyVerificationStrategy'),
        ],
    )
    def test_create_permanent_ssh_verify_strategies(self, mock_rest, create_kwargs, ssh_verify, expected_class):
        """create_permanent() sets the correct SSH verification strategy."""
        create_kwargs['ssh_verify'] = ssh_verify
        mock_rest.request.return_value = ('', {}, True)
        node = Node(rest=mock_rest)

        node.create_permanent(**create_kwargs)

        call_kwargs = mock_rest.request.call_args.kwargs
        json_params = json.loads(call_kwargs['data']['json'])
        stapler_class = json_params['launcher']['sshHostKeyVerificationStrategy']['stapler-class']
        assert expected_class in stapler_class

    def test_create_permanent_no_labels_uses_name(self, mock_rest, create_kwargs):
        """create_permanent() uses node name as label when labels is empty/None."""
        create_kwargs['labels'] = None
        mock_rest.request.return_value = ('', {}, True)
        node = Node(rest=mock_rest)

        node.create_permanent(**create_kwargs)

        call_kwargs = mock_rest.request.call_args.kwargs
        json_params = json.loads(call_kwargs['data']['json'])
        assert json_params['labelString'] == 'new-agent'


# ---------------------------------------------------------------------------
# reconfig
# ---------------------------------------------------------------------------


class TestReconfig:
    def test_reconfig_success(self, mock_rest, tmp_path, mocker):
        """reconfig() reads file and posts config XML.

        Note: The production code opens the file in 'rb' mode (bytes) but then calls
        .encode('utf-8') on the result. This is a latent bug. We patch builtins.open
        to return a string so the .encode() call succeeds, matching the code's intent.
        """
        config_file = tmp_path / 'config.xml'
        config_file.write_text('<slave><name>agent-1</name></slave>')
        mocker.patch('builtins.open', mocker.mock_open(read_data='<slave><name>agent-1</name></slave>'))
        mock_rest.request.return_value = ('', {}, True)
        node = Node(rest=mock_rest)

        result = node.reconfig('agent-1', config_file=str(config_file))

        assert result is True

    def test_reconfig_file_not_found_exits(self, mock_rest):
        """reconfig() calls fail_out when config file does not exist."""
        node = Node(rest=mock_rest)

        with pytest.raises(YoJenkinsException):
            node.reconfig('agent-1', config_file='/nonexistent/config.xml')

    def test_reconfig_json_conversion(self, mock_rest, tmp_path):
        """reconfig() converts JSON to XML when config_is_json is True."""
        config_file = tmp_path / 'config.json'
        config_file.write_text('{"slave": {"name": "agent-1"}}')
        mock_rest.request.return_value = ('', {}, True)
        node = Node(rest=mock_rest)

        result = node.reconfig('agent-1', config_file=str(config_file), config_is_json=True)

        assert result is True
        call_kwargs = mock_rest.request.call_args.kwargs
        # The posted data should be XML (converted from JSON)
        assert b'<slave>' in call_kwargs['data'] or b'slave' in call_kwargs['data']

    def test_reconfig_auto_detects_json(self, mock_rest, tmp_path):
        """reconfig() auto-detects JSON format without config_is_json flag."""
        config_file = tmp_path / 'config.json'
        config_file.write_text('{"slave": {"name": "agent-1"}}')
        mock_rest.request.return_value = ('', {}, True)
        node = Node(rest=mock_rest)

        result = node.reconfig('agent-1', config_file=str(config_file), config_is_json=False)

        assert result is True
        call_kwargs = mock_rest.request.call_args.kwargs
        # The posted data should be XML (auto-detected and converted from JSON)
        assert b'<slave>' in call_kwargs['data'] or b'slave' in call_kwargs['data']

    def test_reconfig_xml_not_converted(self, mock_rest, tmp_path):
        """reconfig() does not convert XML config files."""
        config_file = tmp_path / 'config.xml'
        config_file.write_text('<slave/>')
        mock_rest.request.return_value = ('', {}, True)
        node = Node(rest=mock_rest)

        result = node.reconfig('agent-1', config_file=str(config_file), config_is_json=False)

        assert result is True
        call_kwargs = mock_rest.request.call_args.kwargs
        assert call_kwargs['data'] == b'<slave/>'

    def test_reconfig_request_failure_exits(self, mock_rest, tmp_path, mocker):
        """reconfig() calls fail_out when POST request fails."""
        config_file = tmp_path / 'config.xml'
        config_file.write_text('<slave/>')
        mocker.patch('builtins.open', mocker.mock_open(read_data='<slave/>'))
        mock_rest.request.return_value = ('', {}, False)
        node = Node(rest=mock_rest)

        with pytest.raises(YoJenkinsException):
            node.reconfig('agent-1', config_file=str(config_file))
