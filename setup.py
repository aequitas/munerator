__version__ = '0.12.10'
from setuptools import setup, find_packages
import os
import fnmatch
import glob


# from: https://wiki.python.org/moin/Distutils/Tutorial
def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)


def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    def walk_helper(arg, dirname, files):
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                    names.append(filename)
        if names:
            lst.append((dirname.replace(srcdir, kw.get('prefix', dirname)), names))

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name='munerator',
    version=__version__,
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
        'python-dateutil',
        'rcfile'
    ],
    extras_require={
        'db': [
            'mongoengine',
            'eve_mongoengine==0.0.6-dev',
            'eve==0.4-dev',
            'flask',
        ]
    },
    dependency_links=[
        'https://github.com/hellerstanislav/eve-mongoengine/tarball/01e983b0dcf80b95cdbee799e78405559cc6cca7'
        '#egg=eve_mongoengine-0.0.6-dev',
        'https://github.com/aequitas/eve/tarball/25fc50e34ddc88ecd7ed14bd77124314f70622da#egg=eve-0.4-dev'
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
    data_files=find_data_files('arena/dist', '*', recursive=True, prefix='static'),
)
