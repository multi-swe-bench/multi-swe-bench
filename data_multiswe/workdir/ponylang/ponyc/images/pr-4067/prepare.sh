#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 95581106d93b1f16aad6269f12d6f02684f8dd8c
bash /home/check_git_changes.sh


