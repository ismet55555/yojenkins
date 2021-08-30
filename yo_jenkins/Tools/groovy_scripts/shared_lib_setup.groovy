#!groovy

import org.jenkinsci.plugins.workflow.libs.SCMSourceRetriever
import org.jenkinsci.plugins.workflow.libs.LibraryConfiguration
import org.jenkinsci.plugins.github_branch_source.BranchDiscoveryTrait
import org.jenkinsci.plugins.github_branch_source.GitHubSCMSource
import org.jenkinsci.plugins.github_branch_source.*
import org.jenkinsci.plugins.workflow.libs.*
import hudson.scm.SCM
import hudson.plugins.git.*


// Either repoOwner + repository OR repositoryUrl

// GitHubSCMSource gitSCMSource = new GitHubSCMSource(githubRepoOwner, gitRepoName)

// Most people just use owner/org and repo name in GitHub
// Should be able to also do URL



// Get the variables added via templating
//      NOTE: Paceholders are replaced at runtime depending on user specification
String globalLibraryName = "${lib_name}"
String repoOwner = "${repo_owner}"  // Pairs with repository (OPTIONAL)
String repository = "${repo_name}"  // Pairs with repoOwner (OPTIONAL)
String repositoryUrl = "${repo_url}"
Boolean implicit = ${implicit}
String credentialsId = "${credential_id}"  // OPTIONAL
String defaultVersion = "${repo_branch}"

println globalLibraryName
println repoOwner
println repository
println repositoryUrl
println implicit
println credentialsId
println defaultVersion

return

// try {
//     ....
// } catch (groovyError) {
//     print "['yo-jenkins groovy script failed', '${groovyError.message}', 'failed to find/match permission ID(s)']"
//     return
// }

Hudson instance = Jenkins.get()
def globalLibraryDescriptor = instance.getDescriptor("org.jenkinsci.plugins.workflow.libs.GlobalLibraries")


// Setting up the GitHub Source
GitHubSCMSource gitHubSCMSource = new GitHubSCMSource(repoOwner: repoOwner, repository: repository, repositoryUrl: repositoryUrl, configuredByUrl: true)
if (credentialsId) {
    gitHubSCMSource.credentialsId = credentialsId  // Optional
}
BranchDiscoveryTrait branchDiscoveryTrait = new BranchDiscoveryTrait(3)
List<BranchDiscoveryTrait> branchDiscoveryTraits = new ArrayList<BranchDiscoveryTrait>();
branchDiscoveryTraits.add(new BranchDiscoveryTrait(3))
gitHubSCMSource.setTraits(branchDiscoveryTraits)


// Setting up the Library Configuration
SCMSourceRetriever retriever = new SCMSourceRetriever(gitHubSCMSource)
LibraryConfiguration libraryConfiguration = new LibraryConfiguration(globalLibraryName, retriever)
libraryConfiguration.setDefaultVersion(defaultVersion)
libraryConfiguration.setImplicit(implicit)
globalLibraryDescriptor.get().setLibraries([libraryConfiguration])



// ONLINE EXAMPLE
//   - https://github.com/DigiaFactory/automated-jenkins-pipeline/blob/master/jenkins/init.groovy.d/40-shared-libraries.groovy
def libName = globalLibraryName
def gitHubId = null
def gitHubApiUri = null
def gitHubCredentialsId = credentialsId
def sharedLibOwner = sharedLibOwners.getAt(ind)
def sharedLibRepoName = sharedLibRepos.getAt(ind)

def libraryConfiguration = new LibraryConfiguration(libName,
    new SCMSourceRetriever(new GitHubSCMSource(
        gitHubId,
        gitHubApiUri,
        GitHubSCMSource.DescriptorImpl.SAME,
        gitHubCredentialsId,
        sharedLibOwner,
        sharedLibRepoName
    ))
)
libraryConfiguration.defaultVersion = defaultVersion // Could be configurable, override enough for now
libraryConfiguration.implicit = implicit // There could be a lot of libraries, don't autoload anything
libraryConfiguration.allowVersionOverride = true // Allows users to specify a version, e.g. @Library('myLib@2.0.0')

GlobalLibraries.get().setLibraries([libraryConfiguration])