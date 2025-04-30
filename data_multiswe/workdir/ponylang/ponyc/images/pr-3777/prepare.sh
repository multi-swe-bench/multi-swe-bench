#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 89b03703acfebf6ee6d1b92298f6b671ce14d556
bash /home/check_git_changes.sh


