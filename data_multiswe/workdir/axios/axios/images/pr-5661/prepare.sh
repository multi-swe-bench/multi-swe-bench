#!/bin/bash
set -e

cd /home/axios
git reset --hard
bash /home/check_git_changes.sh
git checkout 0abc70564746496eb211bbd951041b4655aec268
bash /home/check_git_changes.sh

npm ci || true

