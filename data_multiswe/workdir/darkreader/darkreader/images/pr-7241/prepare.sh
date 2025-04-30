#!/bin/bash
set -e

cd /home/darkreader
git reset --hard
bash /home/check_git_changes.sh
git checkout 991883df4d5910851130e3dc0e21fcbce604ea7d
bash /home/check_git_changes.sh

npm ci || true

