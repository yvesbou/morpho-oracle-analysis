from setuptools import setup, find_packages

setup(
    name="oracle_analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "web3>=6.15.1",
        "python-dotenv>=1.0.0",
        "pandas>=2.1.1",
        "tqdm>=4.66.1",
    ],
    python_requires=">=3.8",
)