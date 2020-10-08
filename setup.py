from setuptools import setup, find_packages

name = "queryt"
version = "0.0.1"

setup(
    name=name,
    version=version,
    packages=find_packages(),
    platforms=['POSIX', 'MacOS', 'Windows'],
    python_requires='>=3.6',
    install_requires=[
        "google-cloud-bigquery"
    ]
)
