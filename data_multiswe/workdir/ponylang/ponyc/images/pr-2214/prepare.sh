#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout fff0bdb528a255eb1e87319b9eba908f96364a19
bash /home/check_git_changes.sh


    