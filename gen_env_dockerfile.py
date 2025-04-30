import os
import re
import subprocess
from pathlib import Path
import shutil
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# rawdata_dir= Path("")
base_dir = Path("data_multiswe/workdir")
output_dir = Path("data_multiswe/envbench/")


def build_docker_image(dockerfile_path, org, repo, pr_name):
    image_name = f"mswebench_env/{org.lower()}_{repo.lower()}"
    tag = pr_name
    try:
        delete_result = subprocess.run(
            ["docker", "rmi", "-f", f"{image_name}:{tag}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        if delete_result.returncode == 0:
            print(f"✅ 成功删除旧镜像: {image_name}:{tag}")
    except Exception as e:
        print(f"🚨 删除镜像时发生异常: {str(e)}")

    sh_src = base_dir / f'{org}/{repo}/images/{pr_name}'
    sh_dest = output_dir / "image" /f'{org}/{repo}/{pr_name}'
    shutil.copy2(sh_src / 'run.sh', sh_dest /'run.sh')
    shutil.copy2(sh_src / 'check_git_changes.sh', sh_dest /'check_git_changes.sh')

   
    original_dir = os.getcwd()
    os.chdir(dockerfile_path.parent)
    try:
        build_cmd = [
            "docker", "build",
            "-t", f"{image_name}:{tag}",
            "-f", dockerfile_path.name,
            "."
        ]
        print(f"Building image: {image_name}:{tag}")
        subprocess.run(build_cmd, check=True, capture_output=True, text=True) 
    except subprocess.CalledProcessError as e:
        print(f"Failed to build image {image_name}:{tag}")
        print("Error:", e.stderr)
    finally:
        os.chdir(original_dir)

def gen_dockerfile_image(args):
    org, repo, pr_dir = args
    pr_name = pr_dir.name

    with open(pr_dir / "Dockerfile", 'r') as f:
        first_line = f.readline().strip()
        match = re.match(r'FROM\s+([^:\s]+)(?::([^\s]+))?', first_line)
        if match:
            image_name = match.group(1)
            base = match.group(2)

    base_dir = pr_dir.parent / base
    base_dockerfile_lines = []
    with open(base_dir / "Dockerfile", 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith(("FROM", "WORKDIR", "RUN git clone","RUN cd /home/ && git clone")):
                base_dockerfile_lines.append(line)
                if line.startswith("FROM"):
                    base_dockerfile_lines.append(f"ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118")
                    base_dockerfile_lines.append(f"ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118")
                    base_dockerfile_lines.append(f"RUN apt-get update && apt-get install -y git")
                    base_dockerfile_lines.append('\n')


    prepare_sh_lines = []
    prepare_sh_path = pr_dir / "prepare.sh"
    with open(prepare_sh_path, 'r') as f:
        found_check_script = False
        for line in f:
            line = line.strip()
            if not found_check_script:
                if "bash /home/check_git_changes.sh" in line:
                    prepare_sh_lines.append(line)
                    found_check_script = True
                    continue
                if line.startswith("cd") or line.startswith("git reset"):
                    prepare_sh_lines.append(line)
            else:
                prepare_sh_lines.append(line)
                if "bash /home/check_git_changes.sh" in line:
                    break


    ins_dir = output_dir / 'image' / org / repo / pr_name 
    ins_dir.mkdir(parents=True, exist_ok=True)
    with open(ins_dir / 'Dockerfile' , 'w') as f:
        for line in base_dockerfile_lines:
            f.write(line + "\n")
        
        f.write(f"\n")
        f.write("COPY run.sh /home/")
        f.write(f"\n")
        f.write("COPY check_git_changes.sh /home/")
        f.write(f"\n")
        f.write(f"\n")

        for line in prepare_sh_lines:
            if line: 
                if line.startswith("cd"):
                    f.write(f"WORKDIR {line.split(' ')[1].strip()}\n")
                elif line.startswith("base"):
                    f.write(f"RUN ['/bin/bash', {line.split(' ')[1].strip()}]")
                    f.write(f"\n")
                else:
                    f.write(f"RUN {line}\n")
        
        f.write(f"\n")
        
    return build_docker_image(ins_dir / 'Dockerfile', org, repo, pr_name)


def select_prs():
    image_to_pr = {}
    for images_dir in base_dir.glob("*/*/images"):
        org, repo = images_dir.parts[-3:-1]
        
        for pr_dir in images_dir.glob("pr-*"):
            dockerfile = pr_dir / "Dockerfile"           
            # 解析第一行的FROM
            with open(dockerfile, 'r') as f:
                first_line = f.readline().strip()
                match = re.match(r'FROM\s+([^\s]+)', first_line)
                if match:
                    base_image = match.group(1)
                    if base_image not in image_to_pr.keys():
                        image_to_pr[base_image] = []
                    image_to_pr[base_image].append((org, repo, pr_dir))
    selected_prs = []
    for base_id, pr_list in image_to_pr.items():
        selected_prs.append(pr_list[0])
    
    # selected_tuple = [f"{org}__{repo}_{path.name}" for org, repo, path in selected_prs]
    # dataset_dir= output_dir / 'dataset'
    # dataset_dir.mkdir(parents=True, exist_ok=True)
    # with open(dataset_dir / 'dataset.jsonl', 'w', encoding='utf-8') as f:
    #     for jsonl_file in rawdata_dir.glob('*.jsonl'):
    #         with open(jsonl_file, 'r', encoding='utf-8') as infile:
    #             for line in infile:
    #                 record = json.loads(line)
    #                 if f"{record['org']}__{record['repo']}_pr-{record['number']}" in selected_tuple:
    #                     json.dump(record, f)
    #                     f.write('\n') 

    return selected_prs

def main():
    selected_prs = select_prs()
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(gen_dockerfile_image, args) for args in selected_prs]
      
        for future in as_completed(futures):
            res= future.result()

    

if __name__ == "__main__":
    main()