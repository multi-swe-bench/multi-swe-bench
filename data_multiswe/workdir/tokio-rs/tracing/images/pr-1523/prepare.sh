#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout ac4a8dd27c0b28c36b9cf77cdc52b595168d1c5f
bash /home/check_git_changes.sh

cargo test || true

