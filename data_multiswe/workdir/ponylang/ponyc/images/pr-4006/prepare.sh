#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout d330436df984eb3000c64ced4c2b5b308c296019
bash /home/check_git_changes.sh


