#!/usr/bin/env python3

from enum import Enum


class JenkinsItemClasses(Enum):
    """Enum of Jenkins classes ordered in categories for checking and comparison

    item_type  - How it is stored in the return JSON object from server. The name of the sub-section
    prefix     - The prefix in the URL (ie. for view -> http://localhost:8080/view/My_View/)
    class_type - Any class type Jenkins categorizes this item

    Usage Examples:
        - `JenkinsItemClasses.folder.value['class_type']`
        - `JenkinsItemClasses.view.value['item_type']`
    """
    folder = {
        "item_type":
            "jobs",
        "prefix":
            "job",
        "class_type": [
            'com.cloudbees.hudson.plugins.folder.Folder',
            'org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject',
            'jenkins.branch.OrganizationFolder'
        ]
    }
    view = {
        "item_type":
            "views",
        "prefix":
            "view",
        "class_type": [
            'hudson.model.AllView', 'hudson.model.ListView', 'jenkins.branch.MultiBranchProjectViewHolder$ViewImpl'
        ]
    }
    job = {
        "item_type": "jobs",
        "prefix": "job",
        "class_type": ['org.jenkinsci.plugins.workflow.job.WorkflowJob', 'hudson.model.FreeStyleProject']
    }
    build = {
        "item_type": "builds",
        "prefix": "",
        "class_type": ['org.jenkinsci.plugins.workflow.job.WorkflowRun', 'hudson.model.FreeStyleBuild']
    }
    queue = {
        "item_type": "queue",
        "prefix": "",
        "class_type": ['hudson.model.Queue$BuildableItem', 'hudson.model.Queue$BlockedItem']
    }
    node = {
        "item_type": "computer",
        "prefix": "",
        "class_type": ['hudson.slaves.SlaveComputer', 'hudson.slaves.DumbSlave', 'hudson.model.Hudson$MasterComputer']
    }
