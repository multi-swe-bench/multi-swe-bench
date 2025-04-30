#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 649fe0fc8b9366375eab67639cab404617c527cd
bash /home/check_git_changes.sh
mkdir build || true

