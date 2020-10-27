from setuptools import setup
from setuptools_scm import get_version


version = get_version()


setup(
    name="libecl",
    author="Equinor ASA",
    author_email="fg_sib-scout@equinor.com",
    version=version,
    install_requires=["ecl==" + version],
)
