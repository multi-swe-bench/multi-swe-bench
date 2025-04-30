#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout a9a82de5c48b23958ead9d011765396d29217630
bash /home/check_git_changes.sh

cargo test || true

