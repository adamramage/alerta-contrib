
from setuptools import setup, find_packages

version = '5.3.3'

setup(
    name="alerta-enhance-fxtl",
    version=version,
    description='Alerta plugin for alert enhancement Foxtel',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='peter.smith@foxtel.com.au',
    packages=find_packages(),
    py_modules=['alerta_enhance_fxtl'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'enhance_fxtl = alerta_enhance_fxtl:EnhanceAlert'
        ]
    }
)
