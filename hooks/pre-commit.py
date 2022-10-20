#!/usr/bin/env python

import sys
import re
from git import Repo


def main():
    repository_file = Repo('.')
    branch_name = repository_file.active_branch.name
    if re.search("(major|feature|bugfix|hotfix)/*", branch_name):
        print('Branch name is correct')
        sys.exit(0)
    else:
        print('Branch name is incorrect. Try this: (major|feature|bugfix|hotfix)/* ')
        sys.exit(1)

if __name__ == '__main__':
    main()