#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout c63b8a78be17b5bffcafdd15bb6fbd58be736295
bash /home/check_git_changes.sh


