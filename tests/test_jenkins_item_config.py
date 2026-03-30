"""Tests for yojenkins/yo_jenkins/jenkins_item_config.py"""

import xml.etree.ElementTree as ET

import pytest

from yojenkins.yo_jenkins.jenkins_item_config import JenkinsItemConfig


class TestJenkinsItemConfigExists:
    """Each config type exists and has non-empty values."""

    @pytest.mark.parametrize('member_name', ['FOLDER', 'VIEW', 'JOB'])
    def test_enum_member_exists(self, member_name):
        member = JenkinsItemConfig[member_name]
        assert isinstance(member.value, dict)
        assert len(member.value) > 0

    @pytest.mark.parametrize(
        'member_name,key',
        [
            ('FOLDER', 'blank'),
            ('VIEW', 'blank'),
            ('JOB', 'blank'),
            ('JOB', 'script'),
        ],
    )
    def test_non_empty_xml_configs(self, member_name, key):
        value = JenkinsItemConfig[member_name].value[key]
        assert isinstance(value, str)
        assert len(value.strip()) > 0


class TestXmlValidity:
    """XML config strings must be valid XML."""

    @pytest.mark.parametrize(
        'member_name,key',
        [
            ('FOLDER', 'blank'),
            ('VIEW', 'blank'),
            ('JOB', 'blank'),
            ('JOB', 'script'),
        ],
    )
    def test_xml_parses_without_error(self, member_name, key):
        xml_string = JenkinsItemConfig[member_name].value[key]
        # The JOB script config has {{ SCRIPT }} placeholder, not valid XML content
        # but the XML structure itself should still parse
        root = ET.fromstring(xml_string)
        assert root is not None


class TestXmlRootElements:
    """XML configs contain expected root elements."""

    def test_folder_blank_root_element(self):
        xml_string = JenkinsItemConfig.FOLDER.value['blank']
        root = ET.fromstring(xml_string)
        assert root.tag == 'com.cloudbees.hudson.plugins.folder.Folder'

    def test_view_blank_root_element(self):
        xml_string = JenkinsItemConfig.VIEW.value['blank']
        root = ET.fromstring(xml_string)
        assert root.tag == 'hudson.model.ListView'

    @pytest.mark.parametrize('key', ['blank', 'script'])
    def test_job_root_element_is_project(self, key):
        xml_string = JenkinsItemConfig.JOB.value[key]
        root = ET.fromstring(xml_string)
        assert root.tag == 'project'
