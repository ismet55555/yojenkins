"""Jenkins item configuration definition"""

from enum import Enum


class JenkinsItemConfig(Enum):
    """Enum of Jenkins item configs ordered in categories for creating

    Usage Examples:
        - `JenkinsItemConfig.FOLDER.value['blank']`
    """

    FOLDER = {
        "blank":
            '''<?xml version='1.1' encoding='UTF-8'?>
                    <com.cloudbees.hudson.plugins.folder.Folder plugin="cloudbees-folder@6.15">
                    <properties/>
                    <folderViews class="com.cloudbees.hudson.plugins.folder.views.DefaultFolderViewHolder">
                        <views>
                        <hudson.model.AllView>
                            <owner class="com.cloudbees.hudson.plugins.folder.Folder" reference="../../../.."/>
                            <name>All</name>
                            <filterExecutors>false</filterExecutors>
                            <filterQueue>false</filterQueue>
                            <properties class="hudson.model.View$PropertyList"/>
                        </hudson.model.AllView>
                        </views>
                        <tabBar class="hudson.views.DefaultViewsTabBar"/>
                    </folderViews>
                    <healthMetrics/>
                    <icon class="com.cloudbees.hudson.plugins.folder.icons.StockFolderIcon"/>
                    </com.cloudbees.hudson.plugins.folder.Folder>''',
        "template":
            ""
    }
    VIEW = {
        "blank":
            '''<?xml version="1.1" encoding="UTF-8"?>
                    <hudson.model.ListView>
                        <name>blankio</name>
                        <filterExecutors>false</filterExecutors>
                        <filterQueue>false</filterQueue>
                        <properties class="hudson.model.View$PropertyList"/>
                        <jobNames>
                            <comparator class="hudson.util.CaseInsensitiveComparator"/>
                        </jobNames>
                        <jobFilters/>
                        <columns>
                            <hudson.views.StatusColumn/>
                            <hudson.views.WeatherColumn/>
                            <hudson.views.JobColumn/>
                            <hudson.views.LastSuccessColumn/>
                            <hudson.views.LastFailureColumn/>
                            <hudson.views.LastDurationColumn/>
                            <hudson.views.BuildButtonColumn/>
                        </columns>
                        <recurse>false</recurse>
                    </hudson.model.ListView>''',
        "template":
            ""
    }
    JOB = {
        "blank":
            '''<?xml version='1.1' encoding='UTF-8'?>
                    <project>
                        <description></description>
                        <keepDependencies>false</keepDependencies>
                        <properties/>
                        <scm class="hudson.scm.NullSCM"/>
                        <canRoam>true</canRoam>
                        <disabled>false</disabled>
                        <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
                        <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
                        <triggers/>
                        <concurrentBuild>false</concurrentBuild>
                        <builders/>
                        <publishers/>
                        <buildWrappers/>
                    </project>''',
        "script":
            '''<?xml version='1.1' encoding='UTF-8'?>
                    <project>
                        <actions/>
                        <description></description>
                        <keepDependencies>false</keepDependencies>
                        <properties/>
                        <scm class="hudson.scm.NullSCM"/>
                        <canRoam>true</canRoam>
                        <disabled>false</disabled>
                        <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
                        <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
                        <triggers/>
                        <concurrentBuild>false</concurrentBuild>
                        <builders>
                            <hudson.tasks.Shell>
                            <command>
                                {{ SCRIPT }}
                            </command>
                            <configuredLocalRules/>
                            </hudson.tasks.Shell>
                        </builders>
                        <publishers/>
                        <buildWrappers/>
                    </project>'''
    }
