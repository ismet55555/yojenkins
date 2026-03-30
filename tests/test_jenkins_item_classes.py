"""Tests for JenkinsItemClasses enum."""

import pytest

from yojenkins.yo_jenkins.jenkins_item_classes import JenkinsItemClasses


class TestJenkinsItemClassesMembers:
    """Verify all expected enum members exist."""

    @pytest.mark.parametrize('member_name', ['FOLDER', 'VIEW', 'JOB', 'BUILD', 'QUEUE', 'NODE'])
    def test_enum_has_expected_member(self, member_name):
        assert member_name in JenkinsItemClasses.__members__

    def test_enum_has_exactly_six_members(self):
        assert len(JenkinsItemClasses) == 6


class TestJenkinsItemClassesValues:
    """Verify each enum member has the correct value dict."""

    def test_folder_value(self):
        val = JenkinsItemClasses.FOLDER.value
        assert val['item_type'] == 'jobs'
        assert val['prefix'] == 'job'
        assert 'com.cloudbees.hudson.plugins.folder.Folder' in val['class_type']
        assert 'org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject' in val['class_type']
        assert 'jenkins.branch.OrganizationFolder' in val['class_type']
        assert len(val['class_type']) == 3

    def test_view_value(self):
        val = JenkinsItemClasses.VIEW.value
        assert val['item_type'] == 'views'
        assert val['prefix'] == 'view'
        assert 'hudson.model.AllView' in val['class_type']
        assert 'hudson.model.ListView' in val['class_type']
        assert 'jenkins.branch.MultiBranchProjectViewHolder$ViewImpl' in val['class_type']
        assert len(val['class_type']) == 3

    def test_job_value(self):
        val = JenkinsItemClasses.JOB.value
        assert val['item_type'] == 'jobs'
        assert val['prefix'] == 'job'
        assert 'org.jenkinsci.plugins.workflow.job.WorkflowJob' in val['class_type']
        assert 'hudson.model.FreeStyleProject' in val['class_type']
        assert len(val['class_type']) == 2

    def test_build_value(self):
        val = JenkinsItemClasses.BUILD.value
        assert val['item_type'] == 'builds'
        assert val['prefix'] == ''
        assert 'org.jenkinsci.plugins.workflow.job.WorkflowRun' in val['class_type']
        assert 'hudson.model.FreeStyleBuild' in val['class_type']
        assert len(val['class_type']) == 2

    def test_queue_value(self):
        val = JenkinsItemClasses.QUEUE.value
        assert val['item_type'] == 'queue'
        assert val['prefix'] == ''
        assert 'hudson.model.Queue$BuildableItem' in val['class_type']
        assert 'hudson.model.Queue$BlockedItem' in val['class_type']
        assert len(val['class_type']) == 2

    def test_node_value(self):
        val = JenkinsItemClasses.NODE.value
        assert val['item_type'] == 'computer'
        assert val['prefix'] == ''
        assert 'hudson.slaves.SlaveComputer' in val['class_type']
        assert 'hudson.slaves.DumbSlave' in val['class_type']
        assert 'hudson.model.Hudson$MasterComputer' in val['class_type']
        assert len(val['class_type']) == 3


class TestJenkinsItemClassesStructure:
    """Verify structural properties of the enum."""

    @pytest.mark.parametrize('member', list(JenkinsItemClasses))
    def test_each_member_value_has_required_keys(self, member):
        val = member.value
        assert 'item_type' in val
        assert 'prefix' in val
        assert 'class_type' in val
        assert isinstance(val['class_type'], list)
