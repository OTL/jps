Serializer
======================

jps itsself does not have serializer. If you want to serialize your payload,
You have to handle yourself.

Only serialization by json is supported. If you set environ like below (for bash), ::

  export JPS_SERIALIZE=json

payload will be automatically serialized as json.
Actually, it does just ``json.dumps(payload)`` before published,
``json.loads(payload)`` after subscription.

You can use any serializer if you pass it to publisher/subscriber.  ::

  def my_serialize(payload):
    return payload + 'hoge'

  def my_deserialize(payload):
    return payload + 'hoge'

  pub = jps.Publisher('topic1', serializer=my_serialize)
  sub = jps.Subscriber('topic1', serializer=my_deserialize)
