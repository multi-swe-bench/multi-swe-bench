#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout cb2f814b6c182f7d469d5007aa52885cf24fad34
bash /home/check_git_changes.sh


