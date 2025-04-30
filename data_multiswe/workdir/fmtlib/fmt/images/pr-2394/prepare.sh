#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout cfc05e05f08dc0b6fe619831c96f00ee27d99613
bash /home/check_git_changes.sh
mkdir build || true

