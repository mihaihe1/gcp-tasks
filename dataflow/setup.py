import setuptools

REQUIRED_PACKAGES = ['apache-beam']

setuptools.setup(
    name='setup',
    version='0.0.1',
    description='install module',
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages()
)
