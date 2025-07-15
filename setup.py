from setuptools import find_packages, setup

setup(
    name="multi-swe-bench",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "dataclasses_json",
        "docker",
        "tqdm",
        "gitpython",
        "toml",
        "pyyaml",
        "PyGithub",
        "unidiff",
        "swe-rex"
    ],
    author="seal-research",
    author_email="seal-research-team@email.com",
    description="multiswebench version for omnicode",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seal-research/multi-swe-bench",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
