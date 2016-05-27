__author__ = 'Toni'

#!/usr/bin/env python

from distutils.core import setup

setup(name='awsExportImportManager',
      version='1.1',
      description='brige to aws databases',
      author='Toni Nurmi',
      author_email='toni.nurmi@hotmail.com',
      install_requires=[
          "requests",
          "untangle"
      ]
     )