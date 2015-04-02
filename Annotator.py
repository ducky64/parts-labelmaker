import argparse
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
  
  input_filename = args.filename + '.csv'
  output_filename = args.filename + OUTPUT_POSTFIX + '.csv'
  
  if not os.path.isfile(input_filename):
    raise AnnotatorError("Input CSV '%s' not found" % input_filename)
  
  def process_fn(key_dict):
    supplier = key_dict['Supplier']
    supplierpn = key_dict['SupplierPartNumber']
    
    if supplier in SupplierConfig.SupplierConfig:
      print("Fetching '%s' from '%s'" % (supplierpn, supplier))
      fetcher = SupplierConfig.SupplierConfig[supplier][0]
      parametrics = fetcher.get_component_parametrics(supplierpn)
      return {'SupplierParametrics': Common.parametric_to_string(parametrics)}
    else:
      return {}
          
  rewriter = Common.CsvRewriter(['Supplier', 'SupplierPartNumber'], 
                                ['SupplierParametrics'], 
                                process_fn)
  
  if os.path.isfile(output_filename):
    print("Existing parametric CSV file detected, reading in data")
    rewriter.read_output_csv(output_filename)
    
  rewriter.read_input_csv(input_filename)
  
  rewriter.write_output_csv(output_filename)  
    
  print("Done")
  