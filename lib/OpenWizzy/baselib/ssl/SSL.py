from OpenWizzy import o

# from OpenSSL import crypto
import os
try:
    import M2Crypto as m2c
except:
    if o.system.platform.ubuntu.check():
        o.system.platform.ubuntu.install("python-m2crypto")
    import M2Crypto as m2c

import textwrap

# PASSWD="apasswd_now2easy"

def empty_callback ():
    return None

#howto used from http://e1ven.com/2011/04/06/how-to-use-m2crypto-tutorial/

import OpenWizzy.baselib.key_value_store

class SSL(object):

    def getSSLHandler(self,keyvaluestor=None):
        """
        default keyvaluestor=o.db.keyvaluestore.getFileSystemStore("sslkeys", serializers=[])  #make sure to use no serializers
        pass another keyvaluestor if required (first do 'import OpenWizzy.baselib.key_value_store')
        """
        if keyvaluestor==None:
            keyvaluestor=o.db.keyvaluestore.getFileSystemStore("sslkeys", serializers=[])
        return KeyStor(keyvaluestor)


class KeyStor():

    def __init__(self,keyvaluestor=None):
        self.keys={}
        self.db=keyvaluestor


    def createKeyPair(self,organization="",user="",path=""):
        """
        creates keypairs & stores in localdb
        @return (priv,pub) keys
        """
        m2c.Rand.rand_seed (os.urandom (1024))
        # print "Generating a 1024 bit private/public key pair ..."
        #If you don't like the default M2Crypto ASCII "progress" bar it makes when generating keys, you can use:
        #You can change the key size, though key lengths < 1024 are considered insecure
        #The larger the key size the longer it will take to generate the key and the larger the signature will be when signing
        #You should probably leave the public exponent at 65537 (http://en.wikipedia.org/wiki/Rsa#Key_generation_2)
        keys = m2c.RSA.gen_key (1024, 65537, empty_callback)

        #Save Alice's private key
        #The 'None' tells it to save the private key in an unencrypted format
        #For best security practices, you'd use:
        #That would cause the private key to be saved in an encrypted format
        #Python would ask you to enter a password to use to encrypt the key file
        #For a demo script though it's easier/quicker to just use 'None' :) 

        if path<>"":
            q.system.fs.createDir(path)
            p1="%s/priv.pem"%path
            p2="%s/pub.pem"%path
        else:
            p1='/tmp/_key_%s'%o.base.idgenerator.generateGUID()
            p2='/tmp/_key_%s'%o.base.idgenerator.generateGUID()

        keys.save_key (p1, None)
        keys.save_pub_key (p2)

        priv=o.system.fs.fileGetContents(p1)
        pub=o.system.fs.fileGetContents(p2)


        if path=="":
            o.system.fs.removeFile(p1)
            o.system.fs.removeFile(p2)

            self.db.set(organization,"private_%s"%user,priv)
            self.db.set(organization,"public_%s"%user,pub)

        return (priv,pub)

    def _getKey(self,organization,user,cat,returnAsString=False):
        cachekey="%s_%s_%s"%(organization,user,cat)
        if self.keys.has_key(cachekey):
            return self.keys[cachekey]
        p1='/tmp/_key_%s'%o.base.idgenerator.generateGUID()
        key=self.db.get(organization,"%s_%s"%(cat,user))
        if returnAsString:
            return key
        o.system.fs.writeFile(p1,key)
        try:
            if cat=="public":
                key=m2c.RSA.load_pub_key(p1)
            else:
                key=m2c.RSA.load_key(p1,empty_callback)
        except:
            raise RuntimeError("Cannot load key:%s"%cachekey)
        o.system.fs.removeFile(p1)
        self.keys[cachekey]=key
        return key

    def getPrivKey(self,organization,user):
        key=self._getKey(organization,user,"private")
        return key

    def getPubKey(self,organization,user,returnAsString=False):
        key=self._getKey(organization,user,"public",returnAsString)
        return key

    def setPubKey(self,organization,user,pemstr):
        key=self.db.set(organization,"%s_%s"%("public",user))

    def test(self):
        """
        """
        org="myorg.com"
        self.createKeyPair(org,"alice")
        self.createKeyPair(org,"bob")
        msg,signature= self.encrypt(org,"alice","bob","this is a test message.")
        print "msg"
        print msg
        print "signature"
        print signature
        print "decrypt"
        print self.decrypt(org,"alice","bob",msg,signature)


    def perftest(self,nrrounds=1000,sign=True):
        o.base.timer.start()
        org="myorg.com"
        print "\n\nstart perftest for encryption, nrrounds:%s"%nrrounds
        for i in range(nrrounds):
            msg,signature= self.encrypt(org,"alice","bob","this is a test message.",sign=sign)
            self.decrypt(org,"alice","bob",msg,signature)
        o.base.timer.stop(nrrounds)

    def encrypt(self,organization,sender,reader,message,sign=True,base64=True):
        """
        @param sender, name of person sending
        @param name of person reading
        @return encryptedtext,signature
        """

        # print "encrypt org:%s for:%s from:%s message:%s"%(organization,reader,sender,message)

        #Alice wants to send a message to reader, which only reader will be able to decrypt
        #Step 1, load reader's public key
        WriteRSA=self.getPubKey(organization,reader)

        #Step 2, encrypt the message using that public key
        #Only reader's private key can decrypt a message encrypted using reader's public key
        CipherText = WriteRSA.public_encrypt (message, m2c.RSA.pkcs1_oaep_padding)
        if base64:
            CipherText2=CipherText.encode ('base64')
        else:
            CipherText2=CipherText

        if sign:
            #Generate a signature
            MsgDigest = m2c.EVP.MessageDigest ('sha1')
            MsgDigest.update (CipherText)

            RSAsender = self.getPrivKey(organization,sender)

            signature = RSAsender.sign_rsassa_pss (MsgDigest.digest ())
            if base64:
                signature=signature.encode ('base64')
            else:
                signature=signature
        else:
            signature=None

        return CipherText2,signature

    def decrypt(self,organization,sender,reader,message,signature=None,base64=True):
        # print "decrypt org:%s for:%s from:%s\nmessage:%s"%(organization,reader,sender,message)
        ReadRSA=self.getPrivKey(organization,reader)
        if base64:
            message2=message.decode("base64")
        else:
            message2=message
        plainText = ReadRSA.private_decrypt (message2, m2c.RSA.pkcs1_oaep_padding)

        if signature<>None:
            if base64:
                signature2=signature.decode("base64")
            else:
                signature2=signature

            PubKey = self.getPubKey(organization,sender)

            MsgDigest = m2c.EVP.MessageDigest ('sha1')
            MsgDigest.update (message2)

            if not PubKey.verify_rsassa_pss (MsgDigest.digest (), signature2) == 1:
                raise RuntimeError("Could not verify the message")


        return plainText
