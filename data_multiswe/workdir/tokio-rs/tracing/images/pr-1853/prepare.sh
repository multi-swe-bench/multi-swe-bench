#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 9d8d366b15e282ee7767c52e68df299673151587
bash /home/check_git_changes.sh

cargo test || true

