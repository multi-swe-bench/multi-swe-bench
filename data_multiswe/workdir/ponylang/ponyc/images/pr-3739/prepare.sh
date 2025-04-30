#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 19cd02f1dc5852c199148f0aebbfce2f8e8ad81e
bash /home/check_git_changes.sh


