"""YoJenkins class definition"""

import logging

from yojenkins.yo_jenkins.account import Account
from yojenkins.yo_jenkins.build import Build
from yojenkins.yo_jenkins.credential import Credential
from yojenkins.yo_jenkins.folder import Folder
from yojenkins.yo_jenkins.job import Job
from yojenkins.yo_jenkins.node import Node
from yojenkins.yo_jenkins.server import Server
from yojenkins.yo_jenkins.stage import Stage
from yojenkins.yo_jenkins.step import Step

# Getting the logger reference
logger = logging.getLogger()


class YoJenkins:
    """This class is a composite class of other objects

    All work is done by other, included, objects
    """

    def __init__(self, auth: object) -> None:
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
