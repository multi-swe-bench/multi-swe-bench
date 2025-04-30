#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 908cc432a5994f6e17c8f36e13c217dc40085704
bash /home/check_git_changes.sh

cargo test || true

