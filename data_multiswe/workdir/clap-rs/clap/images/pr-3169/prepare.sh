#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout fa439d4f272e55c116e8a272f31efa35cf1e8e0a
bash /home/check_git_changes.sh

cargo test || true

