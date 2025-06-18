from setuptools import setup, find_packages

setup(
    name="lambda-http-server",
    version="0.1.0",
    author="Sean Xiong",
    author_email="sean@acessment.ai",
    description="A simple HTTP server that converts requests to Lambda function event objects and returns HTTP responses according to the function's return value, which roughly means you can test Lambda function URLs locally.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/acessment/lambda-http-server",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
)
