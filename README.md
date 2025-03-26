<div align="center">
 👋 Hi, everyone! 
    <br>
    We are <b>ByteDance Seed team.</b>
</div>

<p align="center">
  You can get to know us better through the following channels👇
  <br>
  <a href="https://team.doubao.com/">
    <img src="https://img.shields.io/badge/Website-%231e37ff?style=for-the-badge&logo=bytedance&logoColor=white"></a>
  <a href="https://github.com/user-attachments/assets/93481cda-a7f3-47f3-b333-fe6b3da86b78">
    <img src="https://img.shields.io/badge/WeChat-07C160?style=for-the-badge&logo=wechat&logoColor=white"></a>
 <a href="https://www.xiaohongshu.com/user/profile/668e7e15000000000303157d?xsec_token=ABl2-aqekpytY6A8TuxjrwnZskU-6BsMRE_ufQQaSAvjc%3D&xsec_source=pc_search">
    <img src="https://img.shields.io/badge/Xiaohongshu-%23FF2442?style=for-the-badge&logo=xiaohongshu&logoColor=white"></a>
  <a href="https://www.zhihu.com/org/dou-bao-da-mo-xing-tuan-dui/">
    <img src="https://img.shields.io/badge/zhihu-%230084FF?style=for-the-badge&logo=zhihu&logoColor=white"></a>
</p>

![seed logo](https://github.com/user-attachments/assets/c42e675e-497c-4508-8bb9-093ad4d1f216)

<!-- 注释：以上为Seed官方信息，可直接复制使用，请注意导入“Seed WeChat”（第12行）、“Seed logo”(第20行)图片替换 -->


# Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving
<p align="center">
  <a href="https://github.com/bytedance/flux">
    <img src="https://img.shields.io/badge/Multi_SWE_bench-Project Page-yellow"></a>
  <a href="https://arxiv.org/pdf/2502.19811">
    <img src="https://img.shields.io/badge/Multi_SWE_bench-Tech Report-red"></a>
  <a href="XXXX">
    <img src="https://img.shields.io/badge/Multi_SWE_bench-Hugging Face-orange"></a>
  <br>
  <a href="https://github.com/user-attachments/assets/d3fcb3bf-466b-4efe-8c3f-5f85258202ae">
    <img src="https://img.shields.io/badge/Multi_SWE_bench-Wechat Communication Group-07C160"></a>
  <a href="XXX">
    <img src="https://img.shields.io/badge/License-XXX-blue"></a>
</p>

We are extremely delighted to release **Multi-SWE-Bench** and **Multi-SWE-Bench RL**.Multi-SWE-Bench aims to build a multi-language benchmark dataset containing real software engineering scenarios for evaluating the ability of LLM to solve real software engineering problems. The dataset supports multiple languages, currently including C, C++, Java, Javascript, Typescript, Rust, Go.

Among other things, our team has also created a **Multi-SWE-Bench RL community** to encourage people to make more real software engineering datasets and then contribute to the community to accelerate the research of LLM in software engineering. If you are interested in this, try to follow the following to make a dataset with your hands!

Welcome to join our community and stay tuned!

<!-- 注释：以上为项目基础信息，以项目COMET举例，Comet一级标题（第25行）、徽章Comet名字（第28、30、32、34行）记得替换，徽章可按需使用
请注意，徽章可根据具体项目自定义，如技术成果落地页、技术成果报告/Paper、Hugging Face、项目微信交流群、License、打榜榜单等，更换名字和链接即可；
专属微信群出现在两个位置，第34行、第42行，可以联系EB同学创建 -->

# News
[2025/03/XX]🔥We have supported XXXXXX.
<br>
[2025/02/XX]🔥XXX is accepted as XXXXXX.
<br>
[2025/01/XX]🔥We release XXX.

# Introduction

This repository is about the datasets construction of Multi-SWE-Bench (Phase1~4) :

<img src=".\Doc\image\Construction.png">

This repository including three modules:

* Multi-SWE-Bench data collection module
* Multi-SWE-Bench dataset construction module
* Multi-SWE-Bench report generation Module

The following sections describe the use of each module in turn !

# Getting started

## Install from Source

```bash
git clone https://github.com/multi-swe-bench/multi-swe-bench.git
cd multi-swe-bench

# Install dependencies
pip install -r requirements.txt
```

## 1.Multi-SWE-Bench data collection module

This module is used to automate the collection of software engineering benchmark datasets, primarily Pull Requests containing issue fixes and their associated Issues from GitHub repositories.

### Usage

```bash
python -m multi_swe_bench.collect.get_pipeline \
    --out_dir <your_output_dir_path> \
    --org <ORG> \         # organization name，For example: python
    --repo <REPO> \       # repository name，For example: cpython
    --tokens <your_github_tokens>    # Github tokens
```

### workflow

1. Get all Pull Requests
2. Filter valid PRs (closed and associated Issues)
3. Collect associated Issues
4. Merge the PR and Issue data.
5. Generate the final raw dataset

**Example of a generated file:**

```
your_output_dir/
├── <ORG>__<REPO>_prs.jsonl             
├── <ORG>__<REPO>_filtered_prs.jsonl    
├── <ORG>__<REPO>_related_issues.jsonl  
└── <ORG>__<REPO>_dataset.jsonl         # Raw data of the PR
```

## 2.Multi-SWE-Bench dataset building module

This is a module for building and processing Multi-SWE-Bench datasets.

### Usage

```bash
python -m multi_swe_bench.harness.build_dataset [Arguments]
```

### Main parameters

- `-mode`: Run mode, optional:
  - `-dataset`: build the full dataset (default), including building the image, running the instance and analyzing it, and generating the final report.
  - `instance`: build the image and run it.
  - `instance_only`: run instance only
  - `-image`: build image only

- `--workdir`: path to the working directory, where files related to the image and instance will be placed.
- `--raw_dataset_files`: path to raw dataset files collected from github (glob mode supported)
- `--output_dir`: path to the output directory, where the final dataset and reports will be located
- `--repo_dir`: path to the repository directory, where the automatically downloaded repositories will be stored.
- `--config`: Load configuration from json, toml or yaml file.

### Optional parameters

- `-force_build`: Whether to force a rebuild of the image (default: False)
- `--specifics`: Specify specific items to be processed
- `--skips`: Specify which items to skip
- `--need_clone`: If or not need to clone the repository (default: True), pull from github if True, otherwise copy locally.
- `--global_env`: Global environment variable settings.
- `-clear_env`: Clear environment variables (default: True)
- `--stop_on_error`: whether to stop on error (default: True)

### Performance-related parameters

- `-max_workers`: Maximum number of worker threads (default: 8)
- `-max_workers_build_image`: Maximum number of worker threads to build an image (default: 8)
- `-max_workers_run_instance`: Maximum number of worker threads to run an instance (default: 8)

### Logging related parameters

- `--log_dir`: Path to the log directory.
- `--log_level`: log level (default: INFO)
- `--log_to_console`: Whether to output logs to the console (default: True)

### Example

```bash
python -m multi_swe_bench.harness.build_dataset --config <your_config_file_path>
```

example_config:

```json
{
    "mode": "dataset",
    "workdir": "./tmp/workdir",
    "raw_dataset_files": [
        "./tmp/raw_dataset/*.jsonl"
    ],
    "force_build": false,
    "output_dir": "./tmp/dataset",
    "specifics": [],
    "skips": [],
    "repo_dir": "./tmp/repos",
    "need_clone": false,
    "global_env": [],
    "clear_env": true,
    "stop_on_error": true,
    "max_workers": 2,
    "max_workers_build_image": 8,
    "max_workers_run_instance": 8,
    "log_dir": "./tmp/logs",
    "log_level": "DEBUG"
}
```

**Example of a generated file:**

```
your_workdir/
├── <ORG_1>         	# Github organization name
	└── <REPO_1>    	# Github repository name
		├── images  	# Files and logs related to BASE and PR images
		└── instances	# Instances run-related logs
├── <ORG_2>         	
	└── <REPO_2>    	
		├── images  	
		└── instances	
└── ...
```

## 3.Multi-SWE-Bench report generation module

This is a module for generating reports on Multi-SWE-Bench datasets.

### Usage

```bash
python -m multi_swe_bench.harness.gen_report [arguments]
```

### Main parameters

- `-mode`: Run mode, optional:
  - `-dataset`: generate dataset and final report (default)
  - `-summary`: Generate final report only.
  - `-regen`: regenerate the report for each data only

- `--workdir`: path to the work directory where the results of the instance run are stored
- `--output_dir`: path to the output directory where generated reports and datasets are stored
- `--raw_dataset_files`: path to raw dataset files collected from github (glob mode supported)
- `--config`: Load configuration from json, toml or yaml files.

### Optional parameters

- `-specifics`: Specify specific items to be processed
- `-skips`: Specify items to skip.
- `-max_workers`: maximum number of worker threads (default: 8)

### Logging related parameters

- `--log_dir`: Path to the log directory.
- `--log_level`: log level (default: INFO)
- `--log_to_console`: Whether to output logs to the console (default: True)

### Example

```bash
python -m multi_swe_bench.harness.gen_report --config <your_config_file_path>
```

example_config:

```json
{
{
    "mode": "dataset",
    "workdir": "./tmp/workdir",
    "output_dir": "./tmp/dataset",
    "specifics": [],
    "skips": [],
    "raw_dataset_files": [
        "./tmp/raw_dataset/*.jsonl"
    ],
    "log_dir": "./tmp/logs",
    "log_level": "DEBUG"
}
}
```



# Features
xxxxxx

# License
This project is licensed under XXX. See the XXX flie for details.

# Citation
If you find XXX useful for your research and applications, feel free to give us a star ⭐ or cite us using:

```bibtex
@article{zan2024swe,
  title={Swe-bench-java: A github issue resolving benchmark for java},
  author={Zan, Daoguang and Huang, Zhirong and Yu, Ailun and Lin, Shaoxin and Shi, Yifan and Liu, Wei and Chen, Dong and Qi, Zongshuai and Yu, Hao and Yu, Lei and others},
  journal={arXiv preprint arXiv:2408.14354},
  year={2024}
}
```

# About [ByteDance Seed Team](https://team.doubao.com/)

Founded in 2023, ByteDance Seed Team is dedicated to crafting the industry's most advanced AI foundation models. The team aspires to become a world-class research team and make significant contributions to the advancement of science and society.

<!-- 注释：About ByteDance Seed Team可直接复制使用 -->