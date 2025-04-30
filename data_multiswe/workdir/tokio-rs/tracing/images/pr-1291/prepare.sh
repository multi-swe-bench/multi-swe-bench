#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 4ad1e62a2dd9f3e97a06ead14285993a9df99ea5
bash /home/check_git_changes.sh

cargo test || true

