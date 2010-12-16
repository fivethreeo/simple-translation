from setuptools import setup, find_packages
setup(
    name='simple-translation',
    version='0.5.1',
    description='This is a translation app/plugin with support for django-cms 2.0 plugins in the admin',
    author='Oyvind Saltvik',
    author_email='oyvind@gmail.com',
    url='http://bitbucket.org/fivethreeo/simple-translation/',
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
    include_package_data=True,
    zip_safe=False,
)

