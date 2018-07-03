
import setuptools


setuptools.setup(
    name = 'nanten2-tools',
    version = __import__('n2').__version__,
    description = 'tools for astronomy data',
    url = 'https://github.com/nanten2/n2-tools',
    author = 'Atsushi Nishimura',
    author_email = 'ars096@gmail.com',
    license = 'MIT',
    keywords = '',
    packages = [
        'n2',
    ],
    install_requires = [
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
