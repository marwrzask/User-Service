#!/usr/bin/env python

import sys
import re

# Required parts
requiredRegex = "^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test){1}(([\w\-\.]+))?(!)?: ([\w ])+([\s\S]*)"

# Get the commit file
commitMessageFile = open(sys.argv[1])
commitMessage = commitMessageFile.read().strip()


if re.search(requiredRegex, commitMessage):
    print("Exccelent job")
    sys.exit(0)
else:
    print("The commit message is wrong, try again. Proper regex is: ^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test){1}(([\w\-\.]+))?(!)?: ([\w ])+([\s\S]*)")
    sys.exit(1)

