from pathlib import Path

from setuptools import find_packages, setup


def read_requirements() -> list[str]:
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        return []
    return [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


setup(
    name="qcvz",
    version="0.1.0",
    description="Lightweight quantum circuit visualization helpers.",
    author="",
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=read_requirements(),
)

