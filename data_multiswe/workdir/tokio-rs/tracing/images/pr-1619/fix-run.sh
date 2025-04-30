#!/bin/bash
set -e

cd /home/tracing
git apply /home/test.patch /home/fix.patch
cargo test

