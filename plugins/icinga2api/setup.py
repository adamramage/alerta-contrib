
from setuptools import setup, find_packages

version = '5.0.3'

setup(
    name="alerta-icinga2api",
    version=version,
    description='Alerta plugin for icinga2api',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Pete Smith',
    author_email='seasurfpete@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_icinga2api'],
    install_requires=[
        'requests'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'icinga2api = alerta_icinga2api:TriggerEvent'
        ]
    }
)
