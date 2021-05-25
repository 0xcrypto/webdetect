import os
from setuptools import setup

try:
    from pypandoc import convert_file
    read_md = lambda f: convert_file(f, 'rst', 'md')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name = "webdetect",
    version = "0.0.1",
    author = "Vikrant Singh Chauhan",
    author_email = "vi@hackberry.xyz",
    description = ("Detects technologies of a web page using Wappalyzer in a headless browser."),
    license = "MIT",
    keywords = ("detect technology", "web", "wappalyzer"),
    url = "http://github.com/0xcrypto/webdetect",
    long_description=read_md('README.md'),
    py_modules=['webdetect'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Security",
        "License :: Public Domain",
    ],
    install_requires=[
        'asyncio', 'python-Wappalyzer', 'click', 'pyppeteer', 
    ],
    entry_points = {
        'console_scripts': ['webdetect=webdetect:detect'],
    }
)
