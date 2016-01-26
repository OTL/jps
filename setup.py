from setuptools import setup, find_packages

setup(name='jsp', version='0.0.1', description='json pub/sub using zmq',
      author='Takashi Ogura', author_email='t.ogura@gmail.com',
      url='http://github.com/OTL/jsp', packages=find_packages(),
      install_requires=[
        'zmq',
        'tornado'
        ],
      entry_points= {
        'console_scripts': [
            'jps_forwarder = jps.forwarder:main',
            'jps_echo = jps.tools:echo_command',
            'jps_pub = jps.tools:pub_command',
            ]
        }
      )
