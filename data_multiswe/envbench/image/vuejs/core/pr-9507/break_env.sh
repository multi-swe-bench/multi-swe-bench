#!/bin/bash
cd /home/core
apt-get install -y jq

TARGET_COMMIT=2599580bcadc9b58de00cd02fb20cbb02700da51

TARGET_DEPS=$(git show "$TARGET_COMMIT:package.json" | jq -c '.devDependencies')

jq --argjson deps "$TARGET_DEPS" '.devDependencies = $deps' package.json > package.json.tmp && mv package.json.tmp package.json
            