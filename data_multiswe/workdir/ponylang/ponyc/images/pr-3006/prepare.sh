#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 3aa1a4167d23f435897bf006c1a6baf9c9b54609
bash /home/check_git_changes.sh


    