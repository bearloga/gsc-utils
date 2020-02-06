from setuptools import setup
from setuptools import find_packages

# Load the contents of the metadata module without using import, since importing requires all dependencies
# to be available and at this point pip hasn't checked them yet.
metadata = {}
with open("gsc_utils/metadata.py") as file:
    exec(file.read(), metadata)

setup(
    name='gsc-utils',
    version=metadata["version"],
    install_requires=[
        'google-api-python-client>=1.7.11',
        'httplib2>=0.14.0',
        'numpy>=1.18.1',
        'pandas>=0.25.3'
    ],
    packages=find_packages(),
    url=metadata["source"],
    license='Apache License 2.0',
    author='Mikhail Popov',
    author_email='mpopov@wikimedia.org',
    description='Wrapper for fetching data from Google Search Console using the Google API Python Client.',
    python_requires=">=3"
)
