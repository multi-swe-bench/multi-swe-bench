#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 2e4e9e27dc9bb935c4319f4b1dcd4fe54bbca81d
bash /home/check_git_changes.sh


