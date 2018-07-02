import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="san-python",
    version="0.0.1",
    author="Santiment",
    author_email="admin@santiment.net",
    description="Package for Santiment API access with python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="",
    #install_requires=install_requires,
    test_suite='nose.collector',
    tests_require=['nose'],
    packages=setuptools.find_packages(),
)
