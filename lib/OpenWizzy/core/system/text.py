CODEC='utf-8'

class Text:
    @staticmethod
    def toStr(value, codec=CODEC):
        if isinstance(value, str):
            return value
        elif isinstance(value, unicode):
            return value.encode(codec)
        else:
            return str(value)

    @staticmethod
    def toUnicode(value, codec=CODEC):
        if isinstance(value, str):
            return value.decode(codec)
        elif isinstance(value, unicode):
            return value
        else:
            return unicode(value)
