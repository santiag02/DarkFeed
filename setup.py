from setuptools import setup, find_packages

print(find_packages(include="lib", where="darkfeed"))

setup(
    name="darkfeed",
    version="0.2",
    author="Camila Santiago",
    packages=["darkfeed", "darkfeed.lib"],
    description="A CLI for parser data from Dark Feed",
    install_requires = ['python-dateutil','requests'],
    keywords= ['ransomware', 'victims', 'darkfeed', 'dark feed'],
    entry_points={
        "console_scripts": [ "darkfeed = darkfeed.main:main"],
    },
)