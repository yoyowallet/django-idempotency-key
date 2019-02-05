#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='django-idempotency-key',
    version='1.0.2',
    author='Del Hyman-Jones',
    author_email='dev@yoyowallet.com',
    description='Django middleware for idempotency key support in view and viewset functions.',
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=['Any'],
    keywords=['django', 'idempotency', 'key', 'idempotency-key', 'middleware'],
    url='https://github.com/yoyowallet/django-idempotency-key',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'Django>=1.11'
    ],
    project_urls={
        'Documentation': 'https://github.com/yoyowallet/django-idempotency-key/blob/master/README.md',
        'Source': 'https://github.com/yoyowallet/django-idempotency-key',
    },
    packages=[
        'idempotency_key'
    ],
    setup_requires=[
        'setuptools>=38.6.0'
    ],
    include_package_data=True,
    zip_safe=False,
)
