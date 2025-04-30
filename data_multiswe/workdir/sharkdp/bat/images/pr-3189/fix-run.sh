#!/bin/bash
set -e

cd /home/bat
git apply /home/test.patch /home/fix.patch
cargo test

