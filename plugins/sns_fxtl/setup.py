
from setuptools import setup, find_packages

version = '5.3.1'

setup(
    name="alerta-sns-fxtl",
    version=version,
    description='Alerta plugin for AWS SNS',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_sns_fxtl'],
    install_requires=[
        'boto'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'sns = alerta_sns:SnsTopicPublisher'
        ]
    }
)
