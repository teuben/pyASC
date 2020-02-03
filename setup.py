from setuptools import setup

version = {}
with open("pyASC/version.py", "r") as f:
    exec(f.read(), version)

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='pyASC',
    version=version['__version__'],
    author='Peter Teuben and Geoffrey Ryan',
    author_email='teuben@astro.umd.edu',
    description='Package for managing an all-sky camera network',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/teuben/pyASC',
    packages=['pyASC'],
    scripts=['scripts/testArchive', 'scripts/testMovie', 'scripts/pyASC-run'],
    install_requires=['numpy', 'opencv-contrib-python-headless',
                      'pyyaml >= 3.08', 'astropy >= 4.0'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy"],
    )
