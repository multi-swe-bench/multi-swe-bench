#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 8ae0ecd7dcc1fc483cd964509f4a91ad35419dc3
bash /home/check_git_changes.sh


    