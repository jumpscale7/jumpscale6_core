
from Crypto.Cipher import Blowfish
from random import randrange

class SerializerBlowfish(object):
    # def __init__(self):
    #     pass

    def dumps(self,obj,encrkey):
        bf=Blowfish.new(encrkey)
        return bf.encrypt(self.__pad_file(str(obj)))

    def loads(self,s,encrkey):
        bf=Blowfish.new(encrkey)
        return self.__depad_file(bf.decrypt(s))

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