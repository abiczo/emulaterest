from setuptools import setup

setup(name='emulaterest',
      description = 'WSGI middleware to emulate PUT and DELETE requests',
      author='Andras Biczo',
      author_email='abiczo@gmail.com',
      url='http://github.com/abiczo/emulaterest',
      license='MIT',
      version='0.1',
      py_modules=['emulaterest'],
      keywords='web wsgi rest',
      test_suite='nose.collector',
      tests_require=['nose>=0.10.4', 'WebTest>=1.1'],
      )
