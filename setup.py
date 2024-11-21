from setuptools import setup, find_packages

setup(
    name="easyconfig",
    version="0.0.1",
    packages=find_packages(where="src"),  # Specify src directory
    package_dir={"": "src"},  # Tell setuptools that packages are under src
    install_requires=[
        "pyqt5",
        "pyyaml"
    ],
    author="Danilo Tardioli",
    author_email="dantard@unizar.es",
    description="A library for easy configuration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dantard/easyconfig",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10'
)
