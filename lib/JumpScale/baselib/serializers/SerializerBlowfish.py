
from Crypto.Cipher import Blowfish
from random import randrange

class SerializerBlowfish(object):
    def __init__(self,encrkey):
        self.c=Blowfish.new(encrkey)

    def dumps(self,obj):
        return self.c.encrypt(self.__pad_file(obj))

    def loads(self,s):
        return self.__depad_file(self.c.decrypt(s))


    # Blowfish cipher needs 8 byte blocks to work with
    def __pad_file(self, data):
        pad_bytes = 8 - (len(data) % 8)                                 
        for i in range(pad_bytes - 1): data += chr(randrange(0, 256))
        # final padding byte; % by 8 to get the number of padding bytes
        bflag = randrange(6, 248); bflag -= bflag % 8 - pad_bytes
        data += chr(bflag)
        return data

    def __depad_file(self, data):
        pad_bytes = ord(data[-1]) % 8
        if not pad_bytes: pad_bytes = 8
        return data[:-pad_bytes]        