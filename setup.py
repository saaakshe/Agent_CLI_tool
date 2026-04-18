from pathlib import Path

from setuptools import find_packages, setup


def read_requirements() -> list[str]:
    requirements = Path(__file__).resolve().parent / "requirements.txt"
    if not requirements.exists():
        return []
    return [
        line.strip()
        for line in requirements.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

setup(
    name="local-agentic-cli",
    version="0.1.0",
    description="Local AI-powered CLI with memory and multi-agent workflows",
    author="Saakshe",
    packages=find_packages(),
    py_modules=["config"],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "agent=Agent_Client.cli:app",
        ],
    },
)
