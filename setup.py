from setuptools import setup, find_packages

from es_odm import __version__


VERSION_STATUS = ""
VERSION_TEXT = f'{__version__}{VERSION_STATUS}'


setup(
    name="es_odm",
    version=VERSION_TEXT,
    description="ODM (Object Document Mapper) for Elasticsearch based on Elasticsearch_dsl and Pydantic",
    long_description=open("README.rst", "r").read(),
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    install_requires=[
        "pydantic",
        "elasticsearch_dsl",
    ],
    author="leon",
    url="",
    author_email="lstk520@qq.com",
    packages=find_packages(),
    package_data={
        '': ["README.rst", "MANIFEST.in"],
        "es_odm": ["*"]
    },
    include_package_data=True,
)
