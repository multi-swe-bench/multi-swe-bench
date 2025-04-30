#!/bin/bash
set -e

cd /home/serde
git reset --hard
bash /home/check_git_changes.sh
git checkout 1b4da41f970555e111f471633205bbcb4dadbc63
bash /home/check_git_changes.sh

cargo test || true

