import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="sanpy",
    version="0.7.16",
    author="Santiment",
    author_email="admin@santiment.net",
    description="Package for Santiment API access with python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/santiment/sanpy",
    test_suite='nose.collector',
    tests_require=['nose'],
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas',
        'httpx',
        'iso8601',
        'setuptools'
    ],
    extras_require={
        "extras":  ["numpy", "matplotlib"]
    }
)
