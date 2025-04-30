#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 3bdad0dac9b51a03b50609d37027aea587243e0e
bash /home/check_git_changes.sh


