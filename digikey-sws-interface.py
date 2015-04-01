import configparser

from pysimplesoap.client import SoapClient



class DigiKeySwsInterface(object):
  CONFIG_SECTION = 'DigiKeySwsInterface'
  def __init__(self):
    config = configparser.RawConfigParser()
    config.read('config.cfg')

    self.client = SoapClient(wsdl='http://services.digikey.com/search/search.asmx?wsdl',
                             trace=True)
    self.client['wsse:Security'] = {'wsse:UsernameToken': 
                                    {'wsse:Username': config.get(self.CONFIG_SECTION, 'Username'), 
                                     'wsse:Password': config.get(self.CONFIG_SECTION, 'Password')}}
    self.client['PartnerInformation'] = {'PartnerId': config.get(self.CONFIG_SECTION, 'PartnerId')}

  def get_component_parameters(self, components):
    output = {}
    for component in components:
      output[component] = self.client.GetProductInfoByDigikeyPartNumber(digikeyPartNumber=component)
  
if __name__ == '__main__':
  dksi = DigiKeySwsInterface()
  print(dksi.get_component_parameters(['NDP7060-ND']))
  