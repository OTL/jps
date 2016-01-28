import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from multiprocessing import Process

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        import jps
        forwarder = Process(target=jps.forwarder.main)
        forwarder.start()
        errno = pytest.main(self.pytest_args)
        forwarder.terminate()
        sys.exit(errno)


setup(name='jps', version='0.0.2a', description='json pub/sub using zmq',
      author='Takashi Ogura', author_email='t.ogura@gmail.com',
      url='http://github.com/OTL/jps', packages=find_packages(),
      install_requires=[
        'zmq',
        ],
      tests_require = ['pytest'],
      cmdclass = {'test': PyTest},
      entry_points= {
        'console_scripts': [
            'jps_forwarder = jps.forwarder:main',
            'jps_topic = jps.tools:topic_command',
            ]
        }
      )
