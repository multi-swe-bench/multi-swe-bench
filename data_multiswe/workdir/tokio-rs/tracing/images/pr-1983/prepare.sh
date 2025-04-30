#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout df9666bdeb8da3e120af15e3c86f4655cb6b29de
bash /home/check_git_changes.sh

cargo test || true

