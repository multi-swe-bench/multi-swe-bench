#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 18583787b3cc1095a002f4a8e1f4d9436e712c54
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

