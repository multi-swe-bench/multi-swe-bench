#!/bin/bash
set -e

cd /home/fd
git apply /home/test.patch /home/fix.patch
cargo test

