from OpenWizzy import o
from .SerializerInt import SerializerInt
from .SerializerTime import SerializerTime
from .SerializerBase64 import SerializerBase64

from SerializersFactory import SerializersFactory

o.base.loader.makeAvailable(o, 'db')

o.db.serializers=SerializersFactory()

o.db.serializers.int = SerializerInt()
o.db.serializers.time = SerializerTime()
o.db.serializers.base64 = SerializerBase64()


