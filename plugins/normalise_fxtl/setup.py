
from setuptools import setup, find_packages

version = '5.3.1'

setup(
    name="alerta-normalise-fxtl",
    version=version,
    description='Alerta plugin for alert normalisation foxtel',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_normalise_fxtl'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'normalise_fxtl = alerta_normalise_fxtl:NormaliseAlert'
        ]
    }
)
