import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyddb",
    version="0.1.8",
    author="Bernard van Niekerk",
    description="Python DynamoDB Abstraction layer",
    long_description=long_description,
    url="https://github.com/frizzy/pyddb",
    packages=["pyddb"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["fastapi>=0.73.0", "pydantic>=1.9.0"],
    python_requires=">=3.8",
)
