"""YoJenkins class definition"""

import logging

from yo_jenkins.YoJenkins.account import Account
from yo_jenkins.YoJenkins.build import Build
from yo_jenkins.YoJenkins.credential import Credential
from yo_jenkins.YoJenkins.folder import Folder
from yo_jenkins.YoJenkins.job import Job
from yo_jenkins.YoJenkins.node import Node
from yo_jenkins.YoJenkins.server import Server
from yo_jenkins.YoJenkins.stage import Stage
from yo_jenkins.YoJenkins.step import Step

# Getting the logger reference
logger = logging.getLogger()


class YoJenkins:
    """This class is a composite class of other objects

    All work is done by other, included, objects
    """

    def __init__(self, Auth_obj) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.Auth = Auth_obj
        self.REST = self.Auth.get_REST()
        self.JenkinsSDK = self.Auth.JenkinsSDK

        self.Server = Server(self.REST, self.Auth)
        self.Node = Node(self.REST)
        self.Account = Account(self.REST)
        self.Credential = Credential(self.REST)
        self.Folder = Folder(self.REST, self.JenkinsSDK)
        self.Build = Build(self.REST, self.Auth)
        self.Job = Job(self.REST, self.Folder, self.JenkinsSDK, self.Auth, self.Build)
        self.Step = Step(self.REST)
        self.Stage = Stage(self.REST, self.Build, self.Step)
