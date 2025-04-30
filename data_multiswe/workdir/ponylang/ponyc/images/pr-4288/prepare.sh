#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout d9a01b50be50dcc4570cfceaa675aefc0225002a
bash /home/check_git_changes.sh


