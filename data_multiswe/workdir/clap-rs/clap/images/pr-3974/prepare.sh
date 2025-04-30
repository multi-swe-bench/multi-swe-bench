#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout bd0ceb7a0a9c66c622ff63fffee6a990191fa18c
bash /home/check_git_changes.sh

cargo test || true

