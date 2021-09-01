
from setuptools import setup, find_packages

version = '5.0.3'

setup(
    name="alerta-opsgenie2",
    version=version,
    description='Alerta plugin for OpsGenie',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Kurt Westerfeld',
    author_email='kurt.westerfeld@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_opsgenie2'],
    install_requires=[
        'requests'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'opsgenie2 = alerta_opsgenie2:TriggerEvent'
        ]
    }
)
