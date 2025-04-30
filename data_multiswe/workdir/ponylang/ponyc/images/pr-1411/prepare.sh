#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 4e9779959433c5b5c817e9a0cdb3b71bff9d09ae
bash /home/check_git_changes.sh


    