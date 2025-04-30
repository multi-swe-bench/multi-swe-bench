#!/bin/bash
set -e

cd /home/bytes
git apply /home/test.patch /home/fix.patch
cargo test

