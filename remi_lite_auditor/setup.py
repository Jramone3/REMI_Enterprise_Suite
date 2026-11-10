from setuptools import setup, find_packages

setup(
    name="remi-lite-auditor",
    version="1.0.0",
    description="Sistema autónomo de ciberinteligencia y auditoría para equipos legacy y de bajos recursos.",
    author="REMI_CORE Ecosystem",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "remi-audit=core.runner:main",
        ],
    },
    python_requires=">=3.8",
)
