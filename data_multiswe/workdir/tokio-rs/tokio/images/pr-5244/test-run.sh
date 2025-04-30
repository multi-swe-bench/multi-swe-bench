#!/bin/bash
set -e

cd /home/tokio
git apply /home/test.patch
cargo test

