#!/bin/bash
set -e

cd /home/darkreader
git reset --hard
bash /home/check_git_changes.sh
git checkout a787eb511f45159c8869d30e5a6ba1f91cb67709
bash /home/check_git_changes.sh

npm ci || true

