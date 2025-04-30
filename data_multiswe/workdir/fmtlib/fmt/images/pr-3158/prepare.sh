#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 80f8d34427d40ec5e7ce3b10ededc46bd4bd5759
bash /home/check_git_changes.sh
mkdir build || true

