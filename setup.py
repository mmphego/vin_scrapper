#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""The setup script."""

import io
import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

# Package meta-data.
AUTHOR = "Mpho Mphego"
DESCRIPTION = "Web scrapping tool for Vehicle information by VIN number"
EMAIL = "mpho112@gmail.com"
NAME = "vin_scrapper"
REQUIRED = [
    # put all required packages here
    "beautifulsoup4==4.7.1",
    "loguru",
    "psutil==5.6.3",
    "requests==2.22.0",
    "selenium-wire==1.0.11",
    "selenium==3.141.0",
    "webdriver-manager==2.4.0",
]

REQUIRES_PYTHON = ">=3.6.0"
URL = "https://github.com/mmphego/vin_scrapper"
VERSION = None


try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION if VERSION else "0.0.1"

SCRIPTS = []
for dirname, dirnames, filenames in os.walk("scripts"):
    for filename in filenames:
        SCRIPTS.append(os.path.join(dirname, filename))


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print(f"\033[1m{s}\033[0m")

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        try:
            import twine
        except ImportError:
            errmsg = "\n'Twine' is not installed.\n\nRun: \n\tpip install twine"
            self.status(errmsg)
            raise SystemExit(1)

        self.status("Building Source and Wheel (universal) distribution...")
        os.system(f"{sys.executable} setup.py sdist bdist_wheel --universal")

        self.status("Uploading the package to PyPI via Twine...")
        os.system("twine upload dist/*")

        self.status("Pushing git tags...")
        os.system(f"git tag v{about.get('__version__')}")
        os.system("git push --tags")
        response = input("Do you want to generate a CHANGELOG.md? (y/n) ")
        if response == "Y" or "y":
            self.status("Generating the CHANGELOG.md.")
            os.system("make changelog")
        sys.exit()


setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    author=NAME,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(
        include=["vin_scrapper"], exclude=["tests", "*.tests", "*.tests.*", "tests.*"],
    ),
    install_requires=REQUIRED,
    include_package_data=True,
    scripts=SCRIPTS,
    license="BSD license",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="vin_scrapper",
    test_suite="tests",
    tests_require=["pytest", "unittest"],
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
        "Say Thanks!": f"https://saythanks.io/to/mmphego",
    },
    zip_safe=False,
    # $ setup.py publish support.
    cmdclass={"upload": UploadCommand},
)
