from setuptools import setup, find_packages


with open('README.rst') as readme:
    next(readme)  # Skip badges
    long_description = ''.join(readme).strip()


setup(
    name='orphanage',
    version='0.1.0',
    url='https://github.com/tonyseek/python-orphanage',
    author='Jiangge Zhang',
    author_email='tonyseek@gmail.com',
    description='Let orphan processes suicide',
    long_description=long_description,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    license='MIT',
    platforms=['POSIX', 'Linux'],
    keywords=['process', 'management', 'orphan'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    setup_requires=[
        'cffi>=1.0.0',
    ],
    install_requires=[
        'cffi>=1.0.0',
    ],
    extras_require={},
    cffi_modules=[
        'orphanage/poll_build.py:ffibuilder',
    ],
)
