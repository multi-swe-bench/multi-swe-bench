#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout ff61416da46dd4a0712d330c59c25d6e8fbf36af
bash /home/check_git_changes.sh


