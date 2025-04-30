#!/bin/bash
set -e

cd /home/bat
git apply /home/test.patch
cargo test

