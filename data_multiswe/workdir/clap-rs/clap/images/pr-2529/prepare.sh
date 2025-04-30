#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout e3bfa50e8f451b31a00d99147d608607521419a3
bash /home/check_git_changes.sh

cargo test || true

