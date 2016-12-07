from setuptools import setup

# NOTE to setup a development environment, ensure you have setuptools installed and then run:
#  python src/setup.py develop
setup(
    name='Wilderness',
    version='0.1',
    description='Text based adventure game',
    url='https://github.com/SebastianJay/Wilderness',
    author='UVA SGD',
    license='Creative Commons',
    install_requires=[
        'pyyaml',
        'nose',
    ],
    zip_safe=False
)
