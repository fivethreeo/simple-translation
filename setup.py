from setuptools import setup, find_packages
import os

setup(
    name='simple-translation',
    version='0.8',
    description='This is a translation app/plugin with support for django-cms 2.1 plugins in the admin',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    author='Oyvind Saltvik',
    author_email='oyvind.saltvik@gmail.com',
    url='http://github.com/fivethreeo/simple-translation/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    test_suite = 'simple_translation.test.run_tests.run_tests',
    include_package_data=True,
    zip_safe=False
)

