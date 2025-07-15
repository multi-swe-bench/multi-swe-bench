
import json
from pathlib import Path

def validate_files():
    dataset_file = Path("data/datasets/dataset.jsonl")
    with open(dataset_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            print(f"Entry {i+1}:")
            print(f"  org/repo: {data.get('org')}/{data.get('repo')}")
            print(f"  p2p_tests: {list(data.get('p2p_tests', {}).keys())}")
            print(f"  f2p_tests: {list(data.get('f2p_tests', {}).keys())}")
            print(f"  test_patch_result passed: {data.get('test_patch_result', {}).get('passed_tests', [])}")
            print(f"  test_patch_result failed: {data.get('test_patch_result', {}).get('failed_tests', [])}")
            print()

if __name__ == "__main__":
    validate_files()
