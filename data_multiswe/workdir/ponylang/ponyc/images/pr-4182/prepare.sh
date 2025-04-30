#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout ac7a441dfb7c6d390dd8d78e8d46670b2faad1cb
bash /home/check_git_changes.sh


