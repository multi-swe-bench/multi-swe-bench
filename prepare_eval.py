import json
import os
import shutil
from pathlib import Path

def clean_directories():
    """
    Clean both output directories and instance directories containing reports
    """
    print("Performing comprehensive cleanup...")
    
    # Directories to completely remove and recreate
    dirs_to_remove = [
        "data/workdir",
        "data/logs",
        "data/output",
        "data/repos"
    ]
    
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            print(f"Removing {dir_path}")
            try:
                shutil.rmtree(dir_path)
            except Exception as e:
                print(f"Error removing {dir_path}: {e}")
        
        os.makedirs(dir_path, exist_ok=True)
    
    print("Directory cleaning completed")

def fix_and_clean():
    """
    Fix test names and ensure all previous reports are cleaned
    """
    # Clean everything first
    clean_directories()
    
    # Ensure directories exist
    dirs = ["data", "data/patches", "data/datasets", "data/repos"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # Define paths
    patches_file = "data/patches/gold_patches.jsonl"
    dataset_file = "data/datasets/dataset.jsonl"
    
    # Target repositories to find
    target_repos = [
        ("alibaba", "fastjson2"),
        # ("fmtlib", "fmt"), # cpp dataset
        # ("jqlang", "jq"), # c dataset
        ("elastic", "logstash"),
        ("mockito", "mockito"),
        ("google", "guava"),
        ("spring-projects", "spring-boot"),
    ]
    
    # Paths to the local dataset files
    # Assumes you've cloned the repository using:
    # git clone https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench
    dataset_base_path = "./mswebench_dataset"  # Adjust this to your actual path
    
    # Mapping of repo types to their dataset files
    repo_file_map = {
        # "jqlang/jq": os.path.join(dataset_base_path, "c/jqlang__jq_dataset.jsonl"),
        # "fmtlib/fmt": os.path.join(dataset_base_path, "cpp/fmtlib__fmt_dataset.jsonl"),
        "alibaba/fastjson2": os.path.join(dataset_base_path, "java/alibaba__fastjson2_dataset.jsonl"),
        "mockito/mockito": os.path.join(dataset_base_path, "java/mockito__mockito_dataset.jsonl"),
        "elastic/logstash": os.path.join(dataset_base_path, "java/elastic__logstash_dataset.jsonl"),
        "google/guava": os.path.join(dataset_base_path, "java/google__guava_dataset.jsonl"),
        "spring-projects/spring-boot": os.path.join(dataset_base_path, "java/spring-projects__spring-boot_dataset.jsonl"),
    }
    
    # Track which repositories we've found
    found_repos = set()
    
    # Create patch and dataset files
    with open(patches_file, "w", encoding="utf-8") as f_patches, \
         open(dataset_file, "w", encoding="utf-8") as f_dataset:
        
        # Process each target repository
        for org, repo in target_repos:
            repo_full = f"{org}/{repo}"
            
            if repo_full not in repo_file_map:
                print(f"No dataset file mapping for {repo_full}, skipping...")
                continue
                
            dataset_file_path = repo_file_map[repo_full]
            if not os.path.exists(dataset_file_path):
                print(f"Dataset file not found: {dataset_file_path}, skipping...")
                continue
                
            print(f"Processing dataset file for {repo_full}: {dataset_file_path}")
            
            # Read the repository's dataset file
            with open(dataset_file_path, "r", encoding="utf-8") as repo_file:
                # Process each line (which should be a JSON object)
                for line in repo_file:
                    if not line.strip():
                        continue
                        
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON from {dataset_file_path}: {e}")
                        continue
                    
                    # Extract patch data
                    patch_data = {
                        "org": org,
                        "repo": repo,
                        "number": item.get("number", 0),
                        "fix_patch": item.get("fix_patch", "")
                    }
                    
                    # Skip if missing fix_patch
                    if not patch_data["fix_patch"]:
                        continue
                    
                    # Print info about available tests
                    print(f"\nData for {org}/{repo}:{patch_data['number']}:")
                    if item.get("p2p_tests"):
                        print(f"  p2p_tests: {list(item['p2p_tests'].keys())}")
                    if item.get("f2p_tests"):
                        print(f"  f2p_tests: {list(item['f2p_tests'].keys())}")
                    if item.get("s2p_tests"):
                        print(f"  s2p_tests: {list(item['s2p_tests'].keys())}")
                    if item.get("n2p_tests"):
                        print(f"  n2p_tests: {list(item['n2p_tests'].keys())}")
                    if item.get("fixed_tests"):
                        print(f"  fixed_tests: {list(item['fixed_tests'].keys())}")
                    
                    # Write files (using the original data, no modifications)
                    f_patches.write(json.dumps(patch_data) + "\n")
                    f_dataset.write(json.dumps(item) + "\n")
                    
                    found_repos.add((org, repo))
                    print(f"Added example for {org}/{repo}:{patch_data['number']}")
                    
                    # We only need one instance per repository
                    break
            
            # If we've found all target repositories, we can stop
            if len(found_repos) == len(target_repos):
                break
    
    print(f"Found {len(found_repos)} out of {len(target_repos)} requested repositories")
    print(f"Found: {', '.join([f'{org}/{repo}' for org, repo in found_repos])}")
    print(f"Missing: {', '.join([f'{org}/{repo}' for org, repo in target_repos if (org, repo) not in found_repos])}")
    
    # Create config file with force_build set to true
    config = {
        "mode": "evaluation",
        "workdir": "data/workdir",
        "patch_files": ["data/patches/gold_patches.jsonl"],
        "dataset_files": ["data/datasets/dataset.jsonl"],
        "force_build": True,  # Force rebuild of images
        "output_dir": "data/output",
        "specifics": [],
        "skips": [],
        "repo_dir": "data/repos",
        "need_clone": True,
        "global_env": [],
        "clear_env": True,
        "stop_on_error": False,
        "max_workers": 2,
        "max_workers_build_image": 2,
        "max_workers_run_instance": 2,
        "log_dir": "data/logs",
        "log_level": "INFO"
    }
    
    with open("clean_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    print("\nSetup complete! Clean configuration created")
    print("To run the evaluation with a completely fresh setup:")
    print("python -m multi_swe_bench.harness.run_evaluation --config clean_config.json")

if __name__ == "__main__":
    fix_and_clean()