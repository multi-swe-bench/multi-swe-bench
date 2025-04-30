#!/bin/bash
set -e

cd /home/express
git reset --hard
bash /home/check_git_changes.sh
git checkout a1fa90fcea7d8e844e1c9938ad095d62669c3abd
bash /home/check_git_changes.sh

npm install || true

