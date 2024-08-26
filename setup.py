import setuptools

setuptools.setup(
    name="Pygilent",
    version="0.1.0",
    url="https://github.com/AlgalMatt/Pygilent",
    author="Matt Dumont",
    author_email="mdumont1989@gmail.com",
    description="Tools for working with Agilent data files.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    include_package_data=True,
    package_data={'': ['data/*.csv']},
)