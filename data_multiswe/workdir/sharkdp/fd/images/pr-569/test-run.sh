#!/bin/bash
set -e

cd /home/fd
git apply /home/test.patch
cargo test

