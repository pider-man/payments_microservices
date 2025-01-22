from setuptools import setup, find_packages

setup(
    name="shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "pydantic>=2.4.2",
        "pymongo>=4.6.0",
    ],
)