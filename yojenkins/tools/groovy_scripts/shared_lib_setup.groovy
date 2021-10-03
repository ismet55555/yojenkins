#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/plugin/github-branch-source/org/jenkinsci/plugins/github_branch_source/GitHubSCMSource.html
//   - https://javadoc.jenkins.io/plugin/git/jenkins/plugins/git/traits/BranchDiscoveryTrait.html
//   - https://javadoc.jenkins.io/plugin/workflow-cps-global-lib/org/jenkinsci/plugins/workflow/libs/SCMSourceRetriever.html
//   - https://javadoc.jenkins.io/plugin/workflow-cps-global-lib/org/jenkinsci/plugins/workflow/libs/LibraryConfiguration.html

import org.jenkinsci.plugins.workflow.libs.SCMSourceRetriever
import org.jenkinsci.plugins.workflow.libs.LibraryConfiguration
import org.jenkinsci.plugins.github_branch_source.BranchDiscoveryTrait
import org.jenkinsci.plugins.github_branch_source.GitHubSCMSource
import hudson.scm.SCM

// TODO: Generalize to ANY git repo, not just GitHub

// Get the variables added via templating
//      NOTE: Paceholders are replaced at runtime depending on user specification
String globalLibraryName = "${lib_name}"
String repoOwner = "${repo_owner}"
String repository = "${repo_name}"
String repositoryUrl = "${repo_url}"
Boolean implicit = ${implicit}
String credentialsId = "${credential_id}"
String defaultVersion = "${repo_branch}"

Hudson instance = Jenkins.get()
def globalLibraryDescriptor = instance.getDescriptor("org.jenkinsci.plugins.workflow.libs.GlobalLibraries")

try {
    // Setting up the GitHub Source
    GitHubSCMSource gitHubSCMSource = new GitHubSCMSource(repoOwner, repository, repositoryUrl, implicit)

    // Assign github repo credentials (Optional)
    if (credentialsId) {
        gitHubSCMSource.credentialsId = credentialsId
    }

    // Set branch discovery trait
    BranchDiscoveryTrait branchDiscoveryTrait = new BranchDiscoveryTrait(3)
    List<BranchDiscoveryTrait> branchDiscoveryTraits = new ArrayList<BranchDiscoveryTrait>();
    branchDiscoveryTraits.add(new BranchDiscoveryTrait(3))
    gitHubSCMSource.setTraits(branchDiscoveryTraits)

    // Setting up and adding Library Configuration
    SCMSourceRetriever retriever = new SCMSourceRetriever(gitHubSCMSource)
    LibraryConfiguration libraryConfiguration = new LibraryConfiguration(globalLibraryName, retriever)
    libraryConfiguration.setDefaultVersion(defaultVersion)
    libraryConfiguration.setImplicit(implicit)
    globalLibraryDescriptor.get().setLibraries([libraryConfiguration])
} catch (groovyError) {
    print "['yojenkins groovy script failed', '${groovyError.message}', 'failed to create shared libraray: ${globalLibraryName}']"
}
