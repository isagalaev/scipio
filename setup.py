#!/usr/bin/env python
from distutils.core import setup


setup(
    name='scipio',
    version='0.1',
    packages=[
        'scipio',
        'scipio.antispam',
        'scipio.management',
        'scipio.management.commands',
        'scipio.migrations',
        'scipio.utils',
    ],

    package_data={
        'scipio': ['templates/scipio/*.html']
    },

    author='Ivan Sagalaev',
    author_email='Maniac@SoftwareManiacs.org',
    description='Simple but powerfull OpenID integration django app',
    url='https://github.com/isagalaev/scipio',
)
