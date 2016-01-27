from setuptools import setup, find_packages

setup(name='jps', version='0.0.2a', description='json pub/sub using zmq',
      author='Takashi Ogura', author_email='t.ogura@gmail.com',
      url='http://github.com/OTL/jps', packages=find_packages(),
      install_requires=[
        'zmq',
        'tornado'
        ],
      entry_points= {
        'console_scripts': [
            'jps_forwarder = jps.forwarder:main',
            'jps_topic = jps.tools:topic_command',
            ]
        }
      )
