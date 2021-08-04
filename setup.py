import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyDmdReader",
    version="0.0.1",
    author="Matthias Straka",
    author_email="matthias.straka@dewetron.com",
    description="Python module to read Dewetron Oxygen DMD files",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DEWETRON/pyDmdReader",
    project_urls={
        "Bug Tracker": "https://github.com/DEWETRON/pyDmdReader/issues",
        "Source Code": "https://github.com/DEWETRON/pyDmdReader",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    platforms=["Windows", "Linux"],
    packages=setuptools.find_packages(),
    install_requires=['numpy'],
    python_requires=">=3.6",
)
