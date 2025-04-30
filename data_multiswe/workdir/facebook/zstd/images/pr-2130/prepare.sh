#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout e7d2391e9a75154657183b049b69a7a2effa9724
bash /home/check_git_changes.sh

