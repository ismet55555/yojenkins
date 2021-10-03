# BFG Repo Cleaner

The [BFG Repo Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) is a simpler,
faster alternative to git-filter-branch for cleansing bad data out of your
Git repository history:

- Removing Crazy Big Files
- Removing Passwords, Credentials & other Private data

**IMPORTANT**: *Be careful running this Git cleaner, git history is changed*

---

## Removing Sensitive Data From Git History

1. Close all pull requests on the git repo

2. Clone the repo locally with the `--mirror` flag
    - `git clone --mirror git@github.com:ismet55555/yojenkins.git`

3. Download the BFG tool binary (`bfg.jar`)
    - https://rtyley.github.io/bfg-repo-cleaner/

4. Create a `replace.txt` file that contains the sensitive text to be replaced by `**REMOVED**`
    - Each line in this text file is text to be replaced as shown below
    ```bash
    # replace.txt
    mypassword
    someAPItoken$%
    login_info
    ```

5. Run BFG Repo Cleaner
    - `java -jar bfg.jar --replace-text replace.txt yojenkins.git`

6. Cleanup unnecessary files and optimize the local repository
    - `cd yojenkins.git`
    - `git reflog expire --expire=now --all && git gc --prune=now --aggressive`

7. Push updated Git commits
    - `git push`

## Remove Big Binary Files From the Git History
`TODO`
