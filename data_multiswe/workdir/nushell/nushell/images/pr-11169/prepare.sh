#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout 112306aab57c7e0d262bc0659fbfe79318d5bf46
bash /home/check_git_changes.sh

cargo test || true

