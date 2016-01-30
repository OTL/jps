.. _jps_topic:

jps_topic
============

jsp_topic is similar tool to `rostopic <http://wiki.ros.org/rostopic>`_.
It is automatically installed by ``pip install jps``.

If you want to know how to use, try ``-h`` option. ::

  $ jps_topic -h
  usage: jps_topic [-h] {pub,echo,list,record,play} ...
  
  json pub/sub tool
  
  positional arguments:
    {pub,echo,list,record,play}
                          command
      pub                 publish topic from command line
      echo                show topic data
      list                show topic list
      record              record topic data
      play                play recorded topic data
  
  optional arguments:
    -h, --help            show this help message and exit

jps_topic pub
----------------
**pub** command publishes json text data. ::

  $ jps_topic pub topic_name "{\"data\": 1.0}"

It publishes only once if the ``--repeat`` option is not specified.
see ``-h`` option for more detail. ::

  $ jps_topic pub -h
  usage: jps_topic pub [-h] [--repeat REPEAT] topic_name data
  
  positional arguments:
    topic_name            name of topic
    data                  json string data to be published
  
  optional arguments:
    -h, --help            show this help message and exit
    --repeat REPEAT, -r REPEAT
                          repeat in hz


jps_topic echo
----------------
**echo** command prints json text data. ::

  $ jps_topic echo -h
  usage: jps_topic echo [-h] [--num NUM] topic_name
  
  positional arguments:
    topic_name         name of topic
  
  optional arguments:
    -h, --help         show this help message and exit
    --num NUM, -n NUM  print N times and exit

jps_topic list
----------------
**list** command collects all topics and create list of topic names,
which is published now. It subscribes 1[sec] to create the list.
If the topic is published less than 1[Hz], the list comman may not
catch the name. You can use ``--timeout`` option to catch the slow topics. ::


  $ jps_topic list --help
  usage: jps_topic list [-h] [--timeout TIMEOUT]
  
  optional arguments:
    -h, --help            show this help message and exit
    --timeout TIMEOUT, -t TIMEOUT
                          timeout in sec

jps_topic record
-----------------
**record** command is like `rosbag <http://wiki.ros.org/rosbag>`_ command.
It records the topic data to the file. You can replay the data by ``play`` command.
You can use ``--file`` option to specify the output file name. Default is ``record.jps.txt``.
You can set the topic name to be recorded. If the topic_names is empty, all topics will be recorded. ::

  $ jps_topic record -h
  usage: jps_topic record [-h] [--file FILE] [topic_names [topic_names ...]]
  
  positional arguments:
    topic_names           topic names to be recorded
  
  optional arguments:
    -h, --help            show this help message and exit
    --file FILE, -f FILE  output file name (default: record.jps.txt)


jps_topic play
-----------------
**play** command replays the saved data by ``jps_topic record``.
You can specify the file name by ``--file`` option.



