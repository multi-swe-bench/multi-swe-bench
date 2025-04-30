#!/bin/bash
set -e

cd /home/axios
git reset --hard
bash /home/check_git_changes.sh
git checkout 85740c3e7a1fa48346dfcbd4497f463ccb1c1b05
bash /home/check_git_changes.sh

npm ci || true

