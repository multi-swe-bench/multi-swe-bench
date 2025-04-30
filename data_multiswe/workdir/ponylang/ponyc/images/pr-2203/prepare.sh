#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 7f8c5b6ee6d27b8596c785960e5515e1fdebbca0
bash /home/check_git_changes.sh


    