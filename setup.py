from setuptools import setup

long_description = open('README.rst').read()

setup(name='emulaterest',
      description='WSGI middleware that does Rails style PUT and DELETE request emulation',
      long_description=long_description,
      author='Andras Biczo',
      author_email='abiczo@gmail.com',
      url='http://github.com/abiczo/emulaterest',
      license='MIT',
      version='0.1',
      py_modules=['emulaterest'],
      keywords='web wsgi middleware rest',
      test_suite='nose.collector',
      tests_require=['nose>=0.10.4', 'WebTest>=1.1'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      entry_points="""
        [paste.filter_factory]
        emulaterest = emulaterest:emulaterest_filter_factory
        [paste.filter_app_factory]
        emulaterest = emulaterest:emulaterest_filter_app_factory
      """,
      )
