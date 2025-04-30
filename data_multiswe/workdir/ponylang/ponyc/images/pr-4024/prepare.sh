#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 073bad675760bfd1d6a7e1a7c37fdb56744b7a14
bash /home/check_git_changes.sh


