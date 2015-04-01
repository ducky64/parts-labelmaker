from pysimplesoap.client import SoapClient

class DigiKeySwsInterface(object):
  def __init__(self):
    self.client = SoapClient(wsdl="http://services.digikey.com/search/search.asmx?wsdl",trace=False)

