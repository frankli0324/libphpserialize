import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libphpserialize",
    version="0.0.1-beta",
    author="Frank",
    author_email="frankli0324@hotmail.com",
    description="A port of PHP's serialize function, in pure python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frankli0324/libphpserialize",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
    install_requires=[]
)
