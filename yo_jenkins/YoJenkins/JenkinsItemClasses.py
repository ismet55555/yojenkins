#!/usr/bin/env python3

from enum import Enum

class JenkinsItemClasses(Enum):
    """Enum of Jenkins classes ordered in categories for checking and comparison

    Usage Examples:
        - `JenkinsItemClasses.folder.value['class_type']`
        - `JenkinsItemClasses.view.value['item_type']`
    """
    folder = {
        "item_type": "jobs",
        "class_type": [
            'com.cloudbees.hudson.plugins.folder.Folder',
            'org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject',
            'jenkins.branch.OrganizationFolder'
        ]
    }
    view = {
        "item_type": "views",
        "class_type": [
            'hudson.model.AllView',
            'hudson.model.ListView',
            'jenkins.branch.MultiBranchProjectViewHolder$ViewImpl'
        ]
    }
    job = {
        "item_type": "jobs",
        "class_type": [
            'org.jenkinsci.plugins.workflow.job.WorkflowJob',
            'hudson.model.FreeStyleProject'
        ]
    }
    build = {
        "item_type": "builds",
        "class_type": [
            'org.jenkinsci.plugins.workflow.job.WorkflowRun',
            'hudson.model.FreeStyleBuild'
        ]
    }
    queue = {
        "item_type": "queue",
        "class_type": [
            'hudson.model.Queue$BuildableItem',
            'hudson.model.Queue$BlockedItem'
        ]
    }



