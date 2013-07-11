from OpenWizzy import o

class Empty():
	pass

if not  o.__dict__.has_key("db"):
	o.db=Empty()

o.db.serializers=Empty()


from SerializerInt import SerializerInt
o.db.serializers.int=SerializerInt()

from SerializerUJson import SerializerUJson
o.db.serializers.ujson=SerializerUJson()

# from SerializerPickle import SerializerPickle
# o.db.serializers.pickle=SerializerPickle()

from SerializerBlosc import SerializerBlosc
o.db.serializers.blosc=SerializerBlosc()

from SerializerTime import SerializerTime
o.db.serializers.time=SerializerTime()

# from SerializerMSGPack import SerializerMSGPack
# o.db.serializers.msgpack=SerializerMSGPack()

# from SerializerSnappy import SerializerSnappy
# o.db.serializers.snappy=SerializerSnappy()

# from SerializerLZMA import SerializerLZMA
# o.db.serializers.lzma=SerializerLZMA()

# from SerializerBlowfish import SerializerBlowfish
# o.db.serializers.blowfish=SerializerBlowfish()

