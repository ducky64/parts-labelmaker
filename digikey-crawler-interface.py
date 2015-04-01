import re
import pprint

from bs4 import BeautifulSoup
from ghost import Ghost

import httplib2

class DigiKeyCrawlerInterface(object):
  URL_PREFIX = 'http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail?name='

  def parse_table(self, soup_table):
    elements = {}
    for row in soup_table.findChildren('tr'):
      header = row.find('th')
      value = row.find('td')
      if (header is not None) and (value is not None):
        elements[header.get_text()] = value.get_text()
    return elements
    
  def get_component_parameters(self, component):
    h = httplib2.Http('.cache')
    resp_headers, content = h.request(self.URL_PREFIX + component)
    content = content.decode("utf-8")
    
    # The part attributes table has a hanging </a> tag. Fail...
    content = re.sub(r'</a>', '', content)
    content = re.sub(r'<a[^>]*>', '', content)
    content = re.sub(r'<img[^>]*>', '', content)

    soup = BeautifulSoup(content)
    parametrics = {}

    parametrics.update(self.parse_table(soup.find('table', 'product-details')))
    parametrics.update(self.parse_table(soup.find('td', 'attributes-table-main')))
  
    return parametrics
  
if __name__ == '__main__':
  dksi = DigiKeyCrawlerInterface()
  #print(dksi.get_component_parameters('NDP7060-ND'))
  pprint.pprint(dksi.get_component_parameters('IPD040N03LGINCT-ND'))
  