from setuptools import setup, find_packages

setup(
    name="tagterminal-arbitrage",
    version="0.1.0",
    packages=find_packages(),  # Ensures 'tag-terminal' is included
    install_requires=[
        "google-cloud-storage",
    ],
    entry_points={
        "console_scripts": [
            "list-gcs=tag_terminal.list_gcs_files:main",
        ],
    },
)