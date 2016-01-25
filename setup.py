from distutils.core import setup
from pip.req import parse_requirements

requirements = parse_requirements("requirements.txt")

setup(
    name="Tweets Cleaner",
    version='0.2',
    description="",
    license='MIT',
    author='PyYoshi',
    install_requires=[str(r.req) for r in requirements]
)
