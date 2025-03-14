# Multi-SWE-Bench 数据集构建工具

这是一个用于构建和处理 Multi-SWE-Bench 数据集的命令行工具。

## 使用方法

基本命令格式：

```bash
python -m multi_swe_bench.harness.build_dataset [参数]
```

### 主要参数

- `--mode`: 运行模式，可选值：
  - `dataset`: 构建完整数据集（默认）, 包括构建镜像, 运行实例并进行分析、生成最终的报告
  - `instance`: 构建镜像并运行
  - `instance_only`: 仅运行实例
  - `image`: 仅构建镜像

- `--workdir`: 工作目录路径, 与镜像、实例相关的文件将放在这里
- `--raw_dataset_files`: 从 github 上收集的原始数据集文件路径（支持 glob 模式）
- `--output_dir`: 输出目录路径, 最终形成的数据集以及报告将放在这里
- `--repo_dir`: 代码仓库目录路径, 存放自动下载的代码仓库
- `--config`: 从 json, toml 或 yaml 文件中加载配置

### 可选参数

- `--force_build`: 是否强制重新构建镜像（默认：False）
- `--specifics`: 指定要处理的特定项目
- `--skips`: 指定要跳过的项目
- `--need_clone`: 是否需要克隆代码仓库（默认：True）, 为 True 时从 github 拉取, 否则从本地拷贝
- `--global_env`: 全局环境变量设置
- `--clear_env`: 是否清除环境变量（默认：True）
- `--stop_on_error`: 遇到错误时是否停止（默认：True）

### 性能相关参数

- `--max_workers`: 最大工作线程数（默认：8）
- `--max_workers_build_image`: 构建镜像的最大工作线程数（默认：8）
- `--max_workers_run_instance`: 运行实例的最大工作线程数（默认：8）

### 日志相关参数

- `--log_dir`: 日志目录路径
- `--log_level`: 日志级别（默认：INFO）
- `--log_to_console`: 是否输出日志到控制台（默认：True）

## 示例

命令:
```bash
python -m multi_swe_bench.harness.build_dataset --config <your_config_file_path>
```

参考配置:
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

# Multi-SWE-Bench 报告生成工具

这是一个用于生成 Multi-SWE-Bench 数据集报告的命令行工具。

## 使用方法

基本命令格式：

```bash
python -m multi_swe_bench.harness.gen_report [参数]
```

### 主要参数

- `--mode`: 运行模式，可选值：
  - `dataset`: 生成数据集和最终报告（默认）
  - `summary`: 仅生成最终报告
  - `regen`: 仅重新生成每个数据的报告

- `--workdir`: 工作目录路径，存放实例运行结果
- `--output_dir`: 输出目录路径，用于存放生成的报告和数据集
- `--raw_dataset_files`: 从 github 上收集的原始数据集文件路径（支持 glob 模式）
- `--config`: 从 json, toml 或 yaml 文件中加载配置

### 可选参数

- `--specifics`: 指定要处理的特定项目
- `--skips`: 指定要跳过的项目
- `--max_workers`: 最大工作线程数（默认：8）

### 日志相关参数

- `--log_dir`: 日志目录路径
- `--log_level`: 日志级别（默认：INFO）
- `--log_to_console`: 是否输出日志到控制台（默认：True）

## 示例

命令 
```bash
python -m multi_swe_bench.harness.gen_report --config <your_config_file_path>
```

参考配置:
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
