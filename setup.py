# coding:utf8
from distutils.core import setup
import py2exe

py2exe_options = {
    "compressed": True,
    "optimize": 2,
    "bundle_files": 1,
}

setup(name="Tweets Cleaner",
      version='0.1',
      description="",
      license='MIT',
      author='PyYoshi',
      zip_safe = True,
      install_requires=[
          'tweepy',
      ],
      options = {"py2exe": py2exe_options},
      console = [
          {"script" : "rm_tweets.py"}
      ],
      zipfile = None
)