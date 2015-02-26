# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(name='zoterocleanup',
      version='dev',
      description='Zotero library management tools',
      author='Christian Brodbeck',
      author_email='christianbrodbeck@nyu.edu',
      url='https://github.com/christianbrodbeck/zotero-cleanup',
      packages=['zoterocleanup'],
      install_requires=['pyzotero', 'keyring >= 5.0'])
