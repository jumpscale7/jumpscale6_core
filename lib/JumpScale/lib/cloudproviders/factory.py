from amazon import AmazonProvider

class Factory(object):

    def get(provider):
        '''Gets an instance of the cloud provider class
        @param provider: sting represents provider type, can be GOOGLE, AMAZON, DIGITALOCEAN, ...
        '''
        providers = {'AMAZON': AmazonProvider}
        return providers[provider]()