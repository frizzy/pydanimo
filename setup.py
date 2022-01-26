import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyddb",
    version="1.0.0-beta.1",
    author="Bernard van Niekerk",
    description="Python DynamoDB Abstraction layer",
    long_description=long_description,
    url="https://github.com/frizzy/pyddb",
    packages=["pydanimo"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["fastapi>=0.74.0", "pydantic>=1.9.0"],
    python_requires=">=3.9",
)
