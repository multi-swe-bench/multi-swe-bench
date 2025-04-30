#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 939cf25789c72fec3e623570cb4f8cf934fc6214
bash /home/check_git_changes.sh


    