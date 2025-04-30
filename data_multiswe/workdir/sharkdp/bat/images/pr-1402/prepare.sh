#!/bin/bash
set -e

cd /home/bat
git reset --hard
bash /home/check_git_changes.sh
git checkout e3b114236452dc5a9084f623b3bd4b39100edd15
bash /home/check_git_changes.sh

cargo test || true

