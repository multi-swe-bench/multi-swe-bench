#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout c3b03ecdce07da8e0f867fd784a9e4aac9e45659
bash /home/check_git_changes.sh


