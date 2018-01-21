from setuptools import setup, find_packages

setup(
    name="aws-mfa-tool",
    description="",
    version="0.1.1",
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
