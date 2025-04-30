#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d21d388b8dc10c8f04187c3afa6e0b44f0977c65
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

