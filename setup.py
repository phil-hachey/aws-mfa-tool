from setuptools import setup, find_packages

setup(
    name="aws-mfa-tool",
    description="Simple CLI for caching temporary credentials in ~/.aws/credentials",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        'boto3>=1.5, <1.6',
        'click>=6.7, < 6.8',
    ],
    entry_points = {
        'console_scripts': [
            'aws-mfa=aws_mfa_tool.cli:cli'
        ],
    }
)
