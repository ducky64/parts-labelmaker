import collections
import re
import pprint
from urllib.parse import quote

import httplib2
from bs4 import BeautifulSoup

import Common

class DigiKeyCrawlerInterface(object):
  URL_PREFIX = 'http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail?name='

  def parse_table(self, soup_table):
    elements = collections.OrderedDict()
    for row in soup_table.findChildren('tr'):
      header = row.find('th')
      value = row.find('td')
      if (header is not None) and (value is not None):
        elements[header.get_text().strip()] = value.get_text().strip()
    return elements
    
  def get_component_parametrics(self, component):
    h = httplib2.Http('.cache')
    resp_headers, content = h.request(self.URL_PREFIX + quote(component))
    content = content.decode('utf-8')
    
    # The part attributes table has a hanging </a> tag. Fail...
    content = re.sub(r'</a>', '', content)
    content = re.sub(r'<a[^>]*>', '', content)
    content = content.replace('&nbsp;', '')
    content = content.replace('\n', '')
    content = content.replace('\t', '')

    soup = BeautifulSoup(content)
    parametrics = collections.OrderedDict()

    parametrics.update(self.parse_table(soup.find('table', 'product-details')))
    parametrics.update(self.parse_table(soup.find('td', 'attributes-table-main')))
  
    return parametrics

def simplify_value(value, preferred=[]):
  split = value.split(',')
  first = None
  for elt in split:
    if elt.find('(') != -1:
      elt = elt[:elt.find('(')]
    if elt.find('@') != -1:
      elt = elt[:elt.find('@')]
    elt = elt.strip()
    if first is None:
      first = elt
    if elt in preferred:
      return elt
  return first

def rewrite_gen(desc_fmt, parameter_key_rewrite, parameter_value_map):
  def inner(params):
    rewritten_params = {}
    parameter_key_map = {elt[0]: elt[1] for elt in parameter_key_rewrite}
    
    new_value_map = {}

    # TODO: refactor rewrite rules
    for key, val in parameter_value_map.items():
      if type(key) is tuple:
        new_value_map[key[1]] = val
        parameter_key_map[key[0]] = key[1]
      else:
        new_value_map[key] = val

    for param_key, param_value in params.items():
      if param_key in parameter_key_map:
        param_key = parameter_key_map[param_key]
      if param_key in new_value_map and param_value in new_value_map[param_key]:
        param_value = new_value_map[param_key][param_value]
      # TODO: make this preferred-agnostic
      rewritten_params[param_key] = simplify_value(param_value, package_preferred)
      
    out_dict = {}
    out_dict['Desc'] = desc_fmt % rewritten_params
    if '_rewrite_package' in rewritten_params:
      out_dict['Package'] = rewritten_params['_rewrite_package']
    elif 'Package / Case' in rewritten_params:
      out_dict['Package'] = rewritten_params['Package / Case']
    else:
      out_dict['Package'] = ""
      
    out_dict['MfrDesc'] = rewritten_params['Description']
    out_dict['MfrPartNumber'] = rewritten_params['Manufacturer Part Number']
    params_dict = collections.OrderedDict()
    for param in parameter_key_rewrite:
      param = param[1]
      if param in rewritten_params:
        params_dict[param] = rewritten_params[param]
      else:
        params_dict[param] = "??"
    out_dict['Parameters'] = Common.parametric_to_string(params_dict)
    return out_dict
  return inner
    
# A mapping from a category or family (trying the more specific family first)
# to a rewrite rule (function) which generates the needed dict 
category_rewrite = {
'Integrated Circuits (ICs)': rewrite_gen(
  "%(Manufacturer Part Number)s",
  [],
  {}),
'PMIC - Voltage Regulators - Linear (LDO)': rewrite_gen(
  "LDO, %(Voltage - Output)s, %(Current - Output)s",
  [('Voltage - Input', 'Vin')],
  {}),
                   
'Diodes, Rectifiers - Single': rewrite_gen(
  "Diode, %(Voltage - DC Reverse (Vr) (Max))s, %(Current - Average Rectified (Io))s",
  [('Diode Type', 'Type'),
   ('Voltage - Forward (Vf) (Max) @ If', 'Vf')],
  {}), 
'Diodes - Zener - Single': rewrite_gen(
  "Zener, %(Voltage - Zener (Nom) (Vz))s",
  [('Tolerance', 'Tol'),
   ('Power - Max', 'Pmax')],
  {}),
                    
'FETs - Single': rewrite_gen(
  "%(FET Type)s, %(Drain to Source Voltage (Vdss))s, %(Current - Continuous Drain (Id) @ 25\u00b0C)s",
  [('Vgs(th) (Max) @ Id', 'Vth')],
  { 'FET Type': {
      'MOSFET N-Channel, Metal Oxide': 'NMOS',
      'MOSFET P-Channel, Metal Oxide': 'PMOS',
    },
  }),
                    
'Resistors': rewrite_gen(
  "Resistor, %(Resistance (Ohms))s\u03A9",
  [('Tolerance', 'Tol'),
   ('Power (Watts)', 'Pmax')],
  {}),
'Potentiometers, Variable Resistors': rewrite_gen(
  "Pot, %(Resistance (Ohms))s\u03A9",
  [('Tolerance', 'Tol'),
   ('Power (Watts)', 'Pmax')],
  {}),
'Capacitors': rewrite_gen(
  "Capacitor, %(Capacitance)s",
  [('Tolerance', 'Tol'),
   ('Voltage - Rated', 'Vmax')],
  {}),
'Fixed Inductors': rewrite_gen(
  "Inductor, %(Inductance)s, %(Current Rating)s",
  [('Tolerance', 'Tol'),
   ('DC Resistance (DCR)', 'Rdc')],
  {}),
                    
'LED Indication - Discrete': rewrite_gen(
  "LED, %(Color)s",
  [('Voltage - Forward (Vf) (Typ)', 'Vf'),
   ('Current - Test', 'Imax'),
   ('Wavelength - Dominant', '\u03bb'),
   ('Millicandela Rating', 'Intensity')],
  {('Lens Style/Size', '_rewrite_package'): {
      'Round with Domed Top, 5mm (T-1 3/4), 5.00mm': '5mm'
    }
  }),
                    
'Test Points': rewrite_gen(
  "Test Point",
  [],
  {}),
                    
'Rectangular Connectors - Headers, Male Pins': rewrite_gen(
  "Header, %(Series)s, %(Number of Positions)sP",
  [('Pitch', 'Pitch'),
   ],
  {}),
'Rectangular Connectors - Free Hanging, Panel Mount': rewrite_gen(
  "Cnctr, %(Series)s, %(Number of Positions)sP",
  [('Cable Termination', 'Style'),
   ('Wire Gauge', 'Wire'),
   ('Pitch', 'Pitch'),
   ],
  {}),
'Sockets for ICs, Transistors': rewrite_gen(
  "Socket, %(Type)s %(Number of Positions or Pins (Grid))s",
  [('Pitch - Mating', 'Pitch')
   ],
  {}),
}

package_preferred = [
'TO-220',
'TO-92',
'DPak',
'D\u00b2Pak',
'DO-35',
'DO-201',
]

class DigiKeyRewrite(object):
  def rewrite_parametrics(self, params):
    family = params['Family']
    category = params['Category']
    if family in category_rewrite:
      return category_rewrite[family](params)
    elif category in category_rewrite:
      return category_rewrite[category](params)
    raise Exception("Unknown category '%s' / family '%s'" 
                    % (category, family))

if __name__ == '__main__':
  # Simple demo and test script
  dksi = DigiKeyCrawlerInterface()
  pprint.pprint(dksi.get_component_parametrics('LM3940IT-3.3/NOPB'))
  