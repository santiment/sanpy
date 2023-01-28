import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name='sanpy',
    version='0.11.4',
    author='Santiment',
    author_email='admin@santiment.net',
    description='Package for Santiment API access with python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/santiment/sanpy',
    test_suite='nose.collector',
    tests_require=['nose'],
    packages=setuptools.find_packages(),
    setup_requires=[
        'numpy',
        'Cython'
    ],
    install_requires=[
        'pandas>=1.3.0',
        'requests',
        'iso8601',
        'setuptools'
    ],
    extras_require={
        'extras':  ['numpy', 'matplotlib', 'scipy', 'mlfinlab']
    }
)
