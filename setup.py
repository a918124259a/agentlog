from setuptools import setup, find_packages

setup(
    name="agentlog",
    version="0.1.0",
    description="Cross-platform AI Agent Action Tracker",
    long_description="Log, search, and replay what your AI agents did across all your tools.",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "agentlog=agentlog.cli:main",
            "agentlog-hook=agentlog.hook:main",
        ],
    },
)
