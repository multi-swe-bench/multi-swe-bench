#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout a1acfd8c20475e8a878b012ac4aa90b361f004ae
bash /home/check_git_changes.sh

cargo test || true

