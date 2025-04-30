#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout ecb3b3a364b3332ac9df51dbecd780f1f73e21e8
bash /home/check_git_changes.sh

cargo test || true

