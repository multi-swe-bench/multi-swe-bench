#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout e3ddede6c4ee818825c4e5a6dfa1d384860c27d9
bash /home/check_git_changes.sh
mkdir build || true

