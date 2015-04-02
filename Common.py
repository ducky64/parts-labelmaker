import collections
import csv

def parametric_to_string(parametric_dict):
  out = ""
  for key, val in parametric_dict.items():
    key = key.replace('=', '').replace(';', '')
    val = val.replace('=', '').replace(';', '')
    if out:
      out += ";"
    out += key + "=" + val
  return out

def string_to_parametric(parametric_string):
  out_dict = collections.OrderedDict()
  parameters = parametric_string.split(";")
  for parameter in parameters:
    parameter_split = parameter.split('=')
    if len(parameter_split) != 2:
      continue
    out_dict[parameter_split[0]] = parameter_split[1]
  return out_dict

class CsvSanityError(Exception):
  pass

class CsvRewriter(object):
  def __init__(self, key_fields, value_fields, process_fn):
    self.fieldnames = None
    self.key_fields = key_fields
    self.value_fields = value_fields
    self.process_fn = process_fn
    
    self.in_data = [] # raw rowdict from input
    self.out_keyed_data = {} # key_fields tuple to {value_key: value_value} dict 
    
  def read_input_csv(self, csv_filename):
    with open(csv_filename, encoding='utf-8') as csvfile:
      reader = csv.DictReader(csvfile)
      fields = reader.fieldnames
      if self.fieldnames is None:
        self.fieldnames = fields
      else:
        assert(self.fieldnames == fields)
        
      if not all([elt in fields for elt in self.key_fields]):
        raise CsvSanityError("Input '%s' missing key fields" % csv_filename)
      for row in reader:
        self.in_data.append(row)
      
  def read_output_csv(self, csv_filename):
    with open(csv_filename, encoding='utf-8') as csvfile:
      reader = csv.DictReader(csvfile)
      fields = reader.fieldnames
      if not all([elt in fields for elt in self.key_fields]):
        raise CsvSanityError("Output '%s' missing key fields" % csv_filename)
      if not all([elt in fields for elt in self.value_fields]):
        raise CsvSanityError("Output '%s' missing value fields" % csv_filename)
      for row in reader:
        keys = tuple([row[key_field] for key_field in self.key_fields])
        values = {key: row[key] for key in self.value_fields}
        assert keys not in self.out_keyed_data
        self.out_keyed_data[keys] = values
              
  def write_output_csv(self, csv_filename):
    existing_count = 0
    processed_count = 0
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
      writer = csv.DictWriter(csvfile,
                              fieldnames=self.fieldnames+self.value_fields)
      writer.writeheader()
      
      for row in self.in_data:
        keys = tuple([row[key_field] for key_field in self.key_fields])
        keys_dict = dict(zip(self.key_fields, keys))
        if keys in self.out_keyed_data:
          values = self.out_keyed_data[keys]
          existing_count += 1
        else:
          values = self.process_fn(keys_dict)
          processed_count += 1
        row.update(values)
        writer.writerow(row)
        
      print("%i existing entries, %i newly processed entries" 
            % (existing_count, processed_count))
      