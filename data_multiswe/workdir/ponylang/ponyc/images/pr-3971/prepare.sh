#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 8c8306a8b4e1f42afa2b19a6007987901b0864c8
bash /home/check_git_changes.sh


