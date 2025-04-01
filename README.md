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

<!-- 注释：以上为Seed官方信息，可直接复制使用，请注意导入"Seed WeChat"（第12行）、"Seed logo"(第20行)图片替换 -->


## 🚀 Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving
<p align="center">
  <a href="https://github.com/multi-swe-bench/multi-swe-bench">
    <img src="https://img.shields.io/badge/Multi_SWE_bench-Project Page-yellow"></a>
  <a href="https://arxiv.org/pdf/2502.19811">
    <img src="https://img.shields.io/badge/Multi_SWE_bench-Tech Report-red"></a>
  <a href="https://huggingface.co/datasets/Multi-SWE-RL/Multi-SWE-Bench">
    <img src="https://img.shields.io/badge/Multi_SWE_bench-Hugging Face-orange"></a>
  <br>
  <a href="https://huggingface.co/Multi-SWE-RL">
    <img src="https://img.shields.io/badge/Multi_SWE_RL_Community-Hugging Face-EE9A12"></a>
  <a href="https://discord.gg/EtfbkfqUuN">
    <img src="https://img.shields.io/badge/Multi_SWE_RL_Community-Discord-1449DA"></a>
  <a href="https://github.com/multi-swe-bench/multi-swe-bench/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-Apache-blue"></a>
</p>


We are extremely delighted to release **Multi-SWE-Bench**! Multi-SWE-Bench addresses the lack of multilingual benchmarks for evaluating LLMs in real-world code issue resolution. Unlike existing Python-centric benchmarks (e.g., SWE-bench), our framework spans ​7 languages (Java, Go, Rust, TypeScript, JavaScript, C, C++) with ​1,632 high-quality instances, curated from 2,803 candidates by ​88 expert annotators for reliability.

We aim to accelerate progress in automated issue resolution and RL, bridging the gap toward AGI. Let's join the **Multi-SWE-RL community** to expand datasets, tools, and research collaboration!

<!-- 注释：以上为项目基础信息，以项目COMET举例，Comet一级标题（第25行）、徽章Comet名字（第28、30、32、34行）记得替换，徽章可按需使用
请注意，徽章可根据具体项目自定义，如技术成果落地页、技术成果报告/Paper、Hugging Face、项目微信交流群、License、打榜榜单等，更换名字和链接即可；
专属微信群出现在两个位置，第34行、第42行，可以联系EB同学创建 -->
## ⚡ Features

- **Comprehensive Evaluation**: Tests top models (GPT-4o, Claude 3.5/3.7, DeepSeek V3/R1, Doubao-Pro, etc.) across frameworks (Agentless, SWE-agent, OpenHands), yielding actionable insights.  
- **Multi-SWE-RL Community**: Open-source initiative for large-scale reinforcement learning (RL) datasets. Initial release includes **4723 structured instances** across languages to advance RL research.  
- **Open Infrastructure**: Full data pipeline and tutorials open-sourced to foster community contributions and scalability.  

## 📢 News
[2025/03/XX]🔥We have supported XXXXXX.
<br>
[2025/02/XX]🔥XXX is accepted as XXXXXX.
<br>
[2025/01/XX]🔥We release XXX.

## 📊 Evaluation

### Run Evaluation

To run the evaluation, you need to prepare the following:

1. Patch Files: Some patch files in JSONL format, each item containing:
   - `org`: Organization Name
   - `repo`: Repository Name
   - `number`: Pull Request Number
   - `fix_patch`: Fix Patch Content
2. Dataset Files: Dataset files in JSONL format available on Hugging Face, such as [Multi-SWE-Bench](https://huggingface.co/datasets/Multi-SWE-RL/Multi-SWE-Bench) or [Multi-SWE-RL](https://huggingface.co/datasets/Multi-SWE-RL/Multi-SWE-RL)

Then you can run the evaluation using the following command:

```bash
python -m multi_swe_bench.harness.run_evaluation --config /path/to/your/config.json
```

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

## TODO
- Merge the Java instances from [previous work](https://github.com/multi-swe-bench/multi-swe-bench-env).
- Integrate the Python instances from the [SWE-bench](https://github.com/swe-bench/SWE-bench) project.


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

## 🌟 Star Growth Trends

<p align="center">
  <a href="https://star-history.com/#multi-swe-bench/multi-swe-bench&Date">
    <img src="https://api.star-history.com/svg?repos=multi-swe-bench/multi-swe-bench&type=Date" width="500" alt="Star History Chart">
  </a>
</p>

## 📜 License
This project is licensed under Apache License 2.0. See the [LICENSE](/LICENSE) flie for details.
## 📖 Citation
If you find XXX useful for your research and applications, feel free to give us a star ⭐ or cite us using:

```bibtex
@article{zan2024swe,
  title={Swe-bench-java: A github issue resolving benchmark for java},
  author={Zan, Daoguang and Huang, Zhirong and Yu, Ailun and Lin, Shaoxin and Shi, Yifan and Liu, Wei and Chen, Dong and Qi, Zongshuai and Yu, Hao and Yu, Lei and others},
  journal={arXiv preprint arXiv:2408.14354},
  year={2024}
}
```
## 🏢 About [ByteDance Seed Team](https://team.doubao.com/)

Founded in 2023, ByteDance Seed Team is dedicated to crafting the industry's most advanced AI foundation models. The team aspires to become a world-class research team and make significant contributions to the advancement of science and society.

<!-- 注释：About ByteDance Seed Team可直接复制使用 -->
