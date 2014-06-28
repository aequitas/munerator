from setuptools import setup, find_packages


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='munerator',
    version="0.10.2",
    description='Manager of OpenArena battles',
    long_description=read("README.rst"),
    author='Johan Bloemberg',
    author_email='mail@ijohan.nl',
    url='https://github.com/aequitas/munerator',
    install_requires=[
        'six',
        'docopt',
        'pyzmq',
        'webcolors',
        'python-Levenshtein',
        'eve==0.3',
        'flask',
        'tornado',
        'mongoengine',
        'eve-mongoengine',
        'python-dateutil'
    ],
    packages=find_packages(),
    license=read("LICENSE"),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    entry_points={
        'console_scripts': [
            "munerator = munerator:main",
        ]
    },
)
