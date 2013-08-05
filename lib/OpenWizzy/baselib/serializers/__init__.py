from OpenWizzy import o
from .SerializerInt import SerializerInt
from .SerializerUJson import SerializerUJson
from .SerializerPickle import SerializerPickle
from .SerializerTime import SerializerTime
from .SerializerBlosc import SerializerBlosc
from .SerializerMSGPack import SerializerMSGPack
from .SerializerSnappy import SerializerSnappy
from .SerializerLZMA import SerializerLZMA
from .SerializerBlowfish import SerializerBlowfish
from .SerializerBase64 import SerializerBase64

o.base.loader.makeAvailable(o, 'db.serializers')
o.db.serializers.int = SerializerInt()
o.db.serializers.ujson = SerializerUJson()
o.db.serializers.pickle = SerializerPickle()
o.db.serializers.time = SerializerTime()
o.db.serializers.blosc = SerializerBlosc()
o.db.serializers.msgpack = SerializerMSGPack()
o.db.serializers.snappy = SerializerSnappy()
o.db.serializers.lzma = SerializerLZMA()
o.db.serializers.blowfish = SerializerBlowfish()
o.db.serializers.base64 = SerializerBase64()
