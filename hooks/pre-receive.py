import sys
import re
from git import Repo


def main():
    repository_file = Repo('.')
    branch_name = repository_file.active_branch.name
    requiredRegex = "^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test){1}(([\w\-\.]+))?(!)?: ([\w ])+([\s\S]*)"
    commitMessageFile = open(sys.argv[1])
    commitMessage = commitMessageFile.read().strip()

    if re.search("(major|feature|bugfix|hotfix)/*", branch_name):
        print('Branch name is correct')

        if re.search(requiredRegex, commitMessage):
            print("Exccelent job")
            sys.exit(0)
        else:
            print("The commit message is wrong, try again. Proper regex is: ^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test){1}(([\w\-\.]+))?(!)?: ([\w ])+([\s\S]*)")
            sys.exit(1)
    else:
        print('Branch name is incorrect. Try this: (major|feature|bugfix|hotfix)/* ')
        sys.exit(1)


if __name__ == '__main__':
    main()
