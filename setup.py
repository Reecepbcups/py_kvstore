from setuptools import setup

# pip install .
# pip install --upgrade .
#
# pip install twine
# python setup.py bdist
# twine upload -r py_kvstore dist/*

setup(
    name="py_kvstore",
    version="0.0.6",
    description="A key value store",
    url="https://github.com/Reecepbcups/py_kvstore",
    author="Reece Willims",
    author_email="reecepbcups@gmail.com",
    license="Apache 2.0",
    packages=["py_kvstore"],
    install_requires=[],
    long_description=open("README.md").read() + "\n\n",
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
