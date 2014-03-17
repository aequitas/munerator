from setuptools import setup, find_packages


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='munerator',
    version="0.3.10",
    description='Manager of OpenArena battles',
    long_description=read("README.rst"),
    author='Johan Bloemberg',
    author_email='mail@ijohan.nl',
    url='https://github.com/aequitas/munerator',
    install_requires=[
        'docopt',
        'pyzmq',
        'codernitydb',
        'webcolors'
    ],
    packages=find_packages(),
    license=read("LICENSE"),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    entry_points={
        'console_scripts': [
            "munerator = munerator:main",
            "munerator_game = munerator.gamewrapper:main",
            "munerator_trans = munerator.event_translate:main"
        ]
    },
)
