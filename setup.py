"""A setuptools based setup module.
Authoritative references:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import re
from setuptools import setup, find_packages
from os import path

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md")) as f:
    long_description = f.read()


def find_version(*file_paths):
    """
    Reads out software version from provided path(s).
    """
    version_file = open("/".join(file_paths), 'r').read()
    lookup = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                       version_file, re.M)

    if lookup:
        return lookup.group(1)

    raise RuntimeError("Unable to find version string.")


setup(
    name="mrkutil",
    version=find_version("mrkutil", "__init__.py"),
    description="Python package containing common functions for python service based arch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ivke-99/mrkutil",
    packages=find_packages(exclude=["doc"]),
    include_package_data=True,
    namespace_packages=["mrkutil"],
    author="Nebojsa Mrkic",
    author_email="mrkic.nebojsa@gmail.com",
    license="Apache 2.0",
    install_requires=[
        # "sqlalchemy>=1.4",
        # "redis>=4.3",
        "RabbitMQPubSub>=0.1.5"
    ],
    dependency_links=[
    ],
    setup_requires=["pytest-runner"],
    tests_require=[
        "pytest",
        "mock",
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
)
