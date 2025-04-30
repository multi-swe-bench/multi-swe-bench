#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout d8a46edafd0a51ee20e1d0e38e42274c7ca270ee
bash /home/check_git_changes.sh

cargo test || true

