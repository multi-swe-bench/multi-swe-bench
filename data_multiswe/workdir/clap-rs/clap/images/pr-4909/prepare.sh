#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 3fa7b8fe510ebc17efc49e881f4c70cb89d88f4f
bash /home/check_git_changes.sh

cargo test || true

