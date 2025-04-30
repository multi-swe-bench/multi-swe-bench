#!/bin/bash
set -e

cd /home/tracing
git apply /home/test.patch
cargo test

