"""
Copyright DEWETRON GmbH 2024

Dmd reader library - Setup Tools Definition
"""
import setuptools

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
except ImportError:
    _bdist_wheel = None

cmdclass = {}
if _bdist_wheel:
    class _PlatformWheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False

        def get_tag(self):
            _, _, plat = _bdist_wheel.get_tag(self)
            return "py3", "none", plat

    cmdclass["bdist_wheel"] = _PlatformWheel

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyDmdReader",
    version="7.3.2",
    author="Matthias Straka",
    author_email="matthias.straka@dewetron.com",
    description="Python module to read Dewetron Oxygen DMD files",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DEWETRON/pyDmdReader",
    keywords="Measurement, Signal processing, Storage",
    project_urls={
        "Bug Tracker": "https://github.com/DEWETRON/pyDmdReader/issues",
        "Source Code": "https://github.com/DEWETRON/pyDmdReader",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    platforms=["Windows", "Linux"],
    packages=["pyDmdReader"],
    package_dir={"pyDmdReader": "pyDmdReader"},
    package_data={
        "pyDmdReader": [
            "bin/*.dll",
            "bin/*.so",
            "bin/linux_x86_64/*.so",
            "bin/linux_x86_64/deps/*.so*",
        ]
    },
    install_requires=["numpy>=1.19.0", "pandas>=1.1.5"],
    python_requires=">=3.7",
    cmdclass=cmdclass,
)
