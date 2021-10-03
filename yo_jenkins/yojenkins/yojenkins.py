"""YoJenkins class definition"""

import logging

from yo_jenkins.yojenkins.account import Account
from yo_jenkins.yojenkins.build import Build
from yo_jenkins.yojenkins.credential import Credential
from yo_jenkins.yojenkins.folder import Folder
from yo_jenkins.yojenkins.job import Job
from yo_jenkins.yojenkins.node import Node
from yo_jenkins.yojenkins.server import Server
from yo_jenkins.yojenkins.stage import Stage
from yo_jenkins.yojenkins.step import Step

# Getting the logger reference
logger = logging.getLogger()


class YoJenkins:
    """This class is a composite class of other objects

    All work is done by other, included, objects
    """

    def __init__(self, auth) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.auth = auth
        self.rest = self.auth.get_rest()
        self.jenkins_sdk = self.auth.jenkins_sdk
        self.server = Server(self.rest, self.auth)
        self.node = Node(self.rest)
        self.account = Account(self.rest)
        self.credential = Credential(self.rest)
        self.folder = Folder(self.rest, self.jenkins_sdk)
        self.build = Build(self.rest, self.auth)
        self.job = Job(self.rest, self.folder, self.jenkins_sdk, self.auth, self.build)
        self.step = Step(self.rest)
        self.stage = Stage(self.rest, self.build, self.step)
