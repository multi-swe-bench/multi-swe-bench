#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout f80bbec28ff790d15481a29583c9b778bf0cc40e
bash /home/check_git_changes.sh

cargo test || true

