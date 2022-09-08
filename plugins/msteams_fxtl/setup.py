
from setuptools import setup, find_packages

version = '5.2.1'

setup(
    name="alerta-msteams-fxtl",
    version=version,
    description='Alerta plugin for Microsoft Teams',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Anton Delitsch',
    author_email='anton@trugen.net',
    packages=find_packages(),
    py_modules=['alerta_msteams_fxtl'],
    install_requires=[
        'pymsteams',
        'jinja2'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'msteams_fxtl = alerta_msteams_fxtl:SendConnectorCardMessage'
        ]
    }
)
