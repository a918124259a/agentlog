from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentlog",
    version="0.2.0",
    description="Cross-platform AI Agent Action Tracker — log, search, and replay what your AI agents did",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AgentForge Team",
    author_email="a918124259a@gmail.com",
    url="https://github.com/a918124259a/agentlog",
    project_urls={
        "Homepage": "https://github.com/a918124259a/agentlog",
        "Issues": "https://github.com/a918124259a/agentlog/issues",
        "Donate": "https://github.com/sponsors/a918124259a",
    },
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "agentlog=agentlog.cli:main",
            "agentlog-hook=agentlog.hook:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Logging",
        "Topic :: Software Development :: AI/ML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="ai agent logging audit trail claude code codex cursor hermes",
)
