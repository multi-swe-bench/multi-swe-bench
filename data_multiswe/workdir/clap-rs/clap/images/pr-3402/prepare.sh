#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 5c3868ea4cb8063731d8526e8e97414942a987ae
bash /home/check_git_changes.sh

cargo test || true

