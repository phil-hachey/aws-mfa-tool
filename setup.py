from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session='hack')
requirements = [str(ir.req) for ir in install_reqs]

setup(
    name="aws-mfa-tool",
    description="",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    tests_require=[
        'coverage',
        'mockito'
    ],
    test_suite='test',
    entry_points = {
        'console_scripts': [
            'aws-mfa=aws_mfa_tool.cli:cli'
        ],
    }
)
