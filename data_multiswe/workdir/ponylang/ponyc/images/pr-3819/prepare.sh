#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout c83552c339960a7cf71155081a7a58df4e4a7862
bash /home/check_git_changes.sh


