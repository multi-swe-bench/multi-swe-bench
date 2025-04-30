#!/bin/bash
set -e

cd /home/rayon
git reset --hard
bash /home/check_git_changes.sh
git checkout 2de810e97d5ce832ff98023a4a9cf215a86244ea
bash /home/check_git_changes.sh

cargo test || true

