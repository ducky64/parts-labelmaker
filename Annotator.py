import argparse
import csv
import os

import Common
import SupplierConfig

OUTPUT_POSTFIX = "_annotated"

class AnnotatorError(Exception):
  pass

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""
  Annotates an input CSV file with part parametric data from various sources.
  CSV must have these columns:
    Supplier: determines the data source (like DigiKey)
    SupplierPartNumber: self-explanatory
  Other columns are passed through to the output file untouched.
  The output will have an additional column, SupplierParametrics, which contain
  a key:value; mapping of parametric data from the supplier's site.
  If the output file already exists, parametric data (if nonempty) will be taken
  from there first to avoid making unnecessary web queries and allowing manual
  editing. OTHER DATA FROM THE OUTPUT IS NOT KEPT.
  """)
  parser.add_argument('--filename', '-f', required=True,
                      help="Input filename, without the .csv extension")
  args = parser.parse_args()
  
  # dict of (Supplier, SupplierPartNumber) to part parametrics dict
  parametric_data = {}
  
  output_filename = args.filename + OUTPUT_POSTFIX + '.csv'
  input_filename = args.filename + '.csv'
  
  if os.path.isfile(output_filename):
    print("Existing parametric CSV file detected, reading in data")
    with open(output_filename) as csvfile:
      reader = csv.DictReader(csvfile)
      fields = reader.fieldnames
      if 'Supplier' not in fields or 'SupplierPartNumber' not in fields:
        # This is a crash to prevent overwriting existing data
        raise AnnotatorError("Invalid existing parametric CSV")
      for row in reader:
        parametric_data[(row['Supplier'], row['SupplierPartNumber'])] = row['SupplierParametrics']
  else:
    print("Existing parametric CSV file not detected")
    
  if not os.path.isfile(input_filename):
    raise AnnotatorError("Input CSV '%s' not found" % input_filename)
    
  with open(input_filename) as csvfile, open(output_filename, 'w') as outfile:
    reader = csv.DictReader(csvfile)
    fields = reader.fieldnames
    if 'Supplier' not in fields:
      raise AnnotatorError("Supplier not in input CSV '%s'" % input_filename)
    if 'SupplierPartNumber' not in fields:  
      raise AnnotatorError("SupplierPartNumber not in input CSV '%s'" % input_filename)
    if 'SupplierParametrics' in fields:
      raise AnnotatorError("SupplierParametrics in input CSV '%s'" % input_filename)
    
    fields.append('SupplierParametrics')
    writer = csv.DictWriter(outfile, fieldnames=fields)
    writer.writeheader()
    for row in reader:
      supplier = row['Supplier']
      supplierpn = row['SupplierPartNumber']
      parametric_key = (supplier, supplierpn)
      if parametric_key in parametric_data:
        row['SupplierParametrics'] = parametric_data[parametric_key]
      else:
        if supplier in SupplierConfig.SupplierConfig:
          print("Fetching '%s' from '%s'" % (supplierpn, supplier))
          fetcher = SupplierConfig.SupplierConfig[supplier][0]
          parametrics = fetcher.get_component_parametrics(supplierpn)
          row['SupplierParametrics'] = Common.parametric_to_string(parametrics)
          
      writer.writerow(row)
      
print("Done")