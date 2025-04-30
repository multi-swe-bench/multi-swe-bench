#!/bin/bash
set -e

cd /home/serde
git apply /home/test.patch
cargo test

