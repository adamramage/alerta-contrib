from setuptools import setup, find_packages

version = '5.0.0'

setup(
    name="alerta-opmanager",
    version=version,
    description='Alerta webhook for opmanager',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Pete Smith',
    author_email='seasurfpete@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_opmanager'],
    install_requires=[
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'opmanager = alerta_opmanager:OpManagerWebhook'
        ]
    }
)
