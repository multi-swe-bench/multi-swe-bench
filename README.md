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


## 🚀 Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving
<p align="center">
  <a href="https://arxiv.org/pdf/2504.02605">
    <img src="https://img.shields.io/badge/Tech Report-arXiv-red"></a>
  <a href="https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench">
    <img src="https://img.shields.io/badge/Dataset-HuggingFace-orange"></a>
  <br>
  <a href="https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-RL">
    <img src="https://img.shields.io/badge/RL Dataset-HuggingFace-EE9A12"></a>
  <a href="https://discord.gg/EtfbkfqUuN">
    <img src="https://img.shields.io/badge/Community-Discord-1449DA"></a>
  <a href="https://github.com/multi-swe-bench/multi-swe-bench/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-Apache-blue"></a>
</p>


We are extremely delighted to release **Multi-SWE-bench**! Multi-SWE-bench addresses the lack of multilingual benchmarks for evaluating LLMs in real-world code issue resolution. Unlike existing Python-centric benchmarks (e.g., SWE-bench), our framework spans ​7 languages (i.e., Java, TypeScript, JavaScript, Go, Rust, C, and C++) with ​1,632 high-quality instances, curated from 2,456 candidates by ​68 expert annotators for reliability.

We aim to accelerate progress in automated issue resolution and RL, bridging the gap toward AGI. Let's join the **Multi-SWE-RL community** to expand datasets, tools, and research collaboration!

## 📢 News
[2025/09/19] 🎉 Multi-SWE-bench has been accepted to the NeurIPS 2025 Datasets and Benchmarks track!

[2025/09/18] 🔧 We have added a `hints` field to all instances in Multi-SWE-bench, describing the newly defined variables in `test.patch` and `fix.patch`, making the tasks more complete. Please feel free to use [it](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench)!

[2025/07/15] 🔥 We are excited to announce the release of [Multi-SWE-bench flash](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench-flash)! This collection features 300 carefully selected multilingual evaluation instances, designed for rapid evaluation and efficient agent rollouts.

[2025/04/15]🔥We released [Multi-SWE-bench mini](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench_mini)! A lightweight version of the full benchmark — 400 instances in total, covering 8 languages, designed to reduce compute cost and make evaluation faster and easier.

[2025/04/03]🔥We released [Multi-SWE-bench](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench) and [Multi-SWE-RL](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-RL).

## ⚡ Features

- **Comprehensive Evaluation**: Evaluating nine powerful models (GPT-4o, OpenAI-o1, OpenAI-o3-mini-high, Claude-3.5-Sonnet, Claude-3.7-Sonnet, DeepSeek-V3, DeepSeek-R1, Qwen2.5-72B-Instruct, and Doubao-1.5-Pro) across three agent frameworks (Agentless, SWE-agent, OpenHands), yielding several valuable insights.  
- **Multi-SWE-RL Community**: Open-source initiative for large-scale RL datasets. Initial release includes **4723 instances** to advance RL research.  
- **Fully Open Source Data, Code, and Environment**: All data, code, and container images are publicly released, along with detailed tutorials, to foster community contributions and enable scalable extension.

## 🚀 Set Up
Multi-SWE-bench uses Docker for reproducible evaluations.
Follow the instructions in the [Docker setup guide](https://docs.docker.com/engine/install/) to install Docker on your machine.
If you're setting up on Linux, we recommend seeing the [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/) as well.

Finally, to build Multi-SWE-bench from source, follow these steps:
```bash
git clone git@github.com:multi-swe-bench/multi-swe-bench.git
cd multi-swe-bench
make install
```

### Development Setup

For development, install with dev dependencies and set up pre-commit hooks:

```bash
make install-dev
```

## 📊 Evaluation

### Run Evaluation

To run the evaluation, you need to prepare the following:

1. Patch Files: Some patch files in JSONL format, each item containing:
   - `org`: Organization Name
   - `repo`: Repository Name
   - `number`: Pull Request Number
   - `fix_patch`: Fix Patch Content

    Example:
    ```json
    {
        "org": "zeromicro",
        "repo": "go-zero",
        "number": "2787",
        "fix_patch": "diff --git ...."
    }
    ```

2. Dataset Files: Dataset files in JSONL format available on Hugging Face, such as [Multi-SWE-bench](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench) or [Multi-SWE-RL](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-RL)
3. (Optional) Docker Images: You can download required Docker images using `scripts/download_images.ps1` (for Windows) or `scripts/download_images.sh` (for Linux/macOS) with either mini and verified images, or RL images:
   ```bash
   # For Windows
   .\scripts\download_images.ps1 scripts\images_mini.txt      # For mini images
   .\scripts\download_images.ps1 scripts\images_verified.txt  # For verified images
   .\scripts\download_images.ps1 scripts\images_rl.txt        # For RL images
   
   # For Linux/macOS
   bash scripts/download_images.sh scripts/images_mini.txt      # For mini images
   bash scripts/download_images.sh scripts/images_verified.txt  # For verified images
   bash scripts/download_images.sh scripts/images_rl.txt        # For RL images
   ```
   This step is optional. If images don't exist locally, they will be built during evaluation.

Then you can run the evaluation using the following command:

```bash
python -m multi_swe_bench.harness.run_evaluation --config /path/to/your/config.json
```

The evaluation process will generate a `final_report.json` file in your specified `output_dir`, which provides a summary of results including resolved_instances, unresolved_instances, and other metrics. For detailed information about failed instances and specific error reasons, you can check the log files in the `log_dir` directory.

#### Configuration File Example

```json
{
    "mode": "evaluation",
    "workdir": "./data/workdir",
    "patch_files": [
        "./data/patches/<your_patch_file>.jsonl"
    ],
    "dataset_files": [
        "./data/patches/<to_evaluate_dataset_file>.jsonl"
    ],
    "force_build": false,
    "output_dir": "./data/dataset",
    "specifics": [],
    "skips": [],
    "repo_dir": "./data/repos",
    "need_clone": false,
    "global_env": [],
    "clear_env": true,
    "stop_on_error": true,
    "max_workers": 8,
    "max_workers_build_image": 8,
    "max_workers_run_instance": 8,
    "log_dir": "./data/logs",
    "log_level": "DEBUG"
}
```

Note, if there are issues when applying the above config file with git apply, you can add the following item. This will replace `git apply` with `patch --batch`, which can increase the success rate of applying patches:
```json
{
    "fix_patch_run_cmd": "bash -c \"apt update && apt install -y patch && sed -i 's@git apply /home/test.patch /home/fix.patch@patch --batch --fuzz=5 -p1 -i /home/test.patch;patch --batch --fuzz=5 -p1 -i /home/fix.patch@g' /home/fix-run.sh && bash /home/fix-run.sh\""
}
```

#### Configuration Parameters

| Parameter | Description |
|-----------|-------------|
| `mode` | Execution mode for the script. Options: `"evaluation"`, `"instance"`, `"instance_only"`, `"image"`. Default: `"evaluation"` |
| `workdir` | Working directory path for evaluation operations |
| `patch_files` | List of patch file paths in JSONL format (supports glob patterns) |
| `dataset_files` | List of dataset file paths in JSONL format (supports glob patterns) |
| `force_build` | Whether to force rebuild Docker images even if they already exist |
| `output_dir` | Directory path for output results |
| `specifics` | List of specific PR IDs to evaluate (empty = all) |
| `skips` | List of PR IDs to skip during evaluation |
| `repo_dir` | Directory containing cloned repositories |
| `need_clone` | Whether repositories should be cloned if not present |
| `global_env` | Global environment variables to pass to Docker containers (format: `"KEY=VALUE"`) |
| `clear_env` | Whether to clear environment variables in Docker containers |
| `stop_on_error` | Whether to stop execution when an error occurs |
| `max_workers` | Maximum number of concurrent worker threads for general tasks |
| `max_workers_build_image` | Maximum number of concurrent worker threads for building Docker images |
| `max_workers_run_instance` | Maximum number of concurrent worker threads for running instances |
| `log_dir` | Directory for log files |
| `log_level` | Logging level. Options: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` |


## [🏆 Multi-SWE-RL Community](https://huggingface.co/Multi-SWE-RL)
[📋 Multi-SWE-RL Dataset Overview](https://docs.google.com/spreadsheets/d/1C90SiRmlac3FizmsJzxzrhSNsnCjyYewdrXzFbBV4x0/edit?gid=493937140#gid=493937140)

The Multi-SWE-RL Community is an open-source initiative focused on collaborative dataset creation for software engineering and reinforcement learning research. To foster active participation and recognize contributors, we introduce this Contribution Incentive Plan. By contributing high-quality data, you directly support advancements in AI research and earn recognition within the community.  

**Incentive Tiers:**
1. **Be a Contributor**: Get listed in the [Contribution Progress Sheet](https://docs.google.com/spreadsheets/d/1C90SiRmlac3FizmsJzxzrhSNsnCjyYewdrXzFbBV4x0/)  
2. **Report Authorship**: Become an author in future technical reports   

Full details: [Contribution Incentive Plan](docs/contribution-incentive-plan.md)

**Get Started in 2 Steps:**
1. **Learn**: [Quick-Start Guide](docs/build-dataset-quick-start.md)  
2. **Try**: Follow our [Contribution Demo](docs/contribution-demo.md)  

Welcome to our [Discord](https://discord.gg/EtfbkfqUuN) to join in Multi-SWE-RL and Multi-SWE-bench related discussions!

## 🌟 Star Growth Trends

<p align="center">
  <a href="https://star-history.com/#multi-swe-bench/multi-swe-bench&Date">
    <img src="https://api.star-history.com/svg?repos=multi-swe-bench/multi-swe-bench&type=Date" width="500" alt="Star History Chart">
  </a>
</p>

## 🙏 Acknowledgements
We express our deepest gratitude to the creators of the [SWE-bench](https://www.swebench.com) dataset. This project references their [repository](https://github.com/SWE-bench/SWE-bench) and builds upon their work.
## 📖 Citation
If you find [Multi-SWE-bench](https://multi-swe-bench.github.io) useful for your research and applications, feel free to give us a star ⭐ or cite us using:

```bibtex
@misc{zan2025multiswebench,
      title={Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving}, 
      author={Daoguang Zan and Zhirong Huang and Wei Liu and Hanwu Chen and Linhao Zhang and Shulin Xin and Lu Chen and Qi Liu and Xiaojian Zhong and Aoyan Li and Siyao Liu and Yongsheng Xiao and Liangqiang Chen and Yuyu Zhang and Jing Su and Tianyu Liu and Rui Long and Kai Shen and Liang Xiang},
      year={2025},
      eprint={2504.02605},
      archivePrefix={arXiv},
      primaryClass={cs.SE},
      url={https://arxiv.org/abs/2504.02605}, 
}
```
## 📜 License
This project is licensed under Apache License 2.0. See the [LICENSE](/LICENSE) file for details.
## 🏢 About [ByteDance Seed Team](https://team.doubao.com/)

Founded in 2023, ByteDance Seed Team is dedicated to crafting the industry's most advanced AI foundation models. The team aspires to become a world-class research team and make significant contributions to the advancement of science and society.
