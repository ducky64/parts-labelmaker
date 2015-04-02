import argparse
import os

import Common
import SupplierConfig

INPUT_POSTFIX = "_annotated"
OUTPUT_POSTFIX = "_labeled"

class AnnotatorError(Exception):
  pass

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""
  Converts supplier-specific parametric data (output of the Annotator) into a
  format for the label generator.
  Like Annotator, this adds new columns to the input CSV. However, output parts
  of pre-existing entries are untouched, making it safe to manually edit.
  """)
  parser.add_argument('--filename', '-f', required=True,
                      help="Input filename, without the .csv extension")
  args = parser.parse_args()

  input_filename = args.filename + INPUT_POSTFIX + '.csv'
  output_filename = args.filename + OUTPUT_POSTFIX + '.csv'
  
  if not os.path.isfile(input_filename):
    raise AnnotatorError("Input CSV '%s' not found" % input_filename)
  
  def process_fn(key_dict):
    supplier = key_dict['Supplier']
    supplierpn = key_dict['SupplierPartNumber']
    parametrics = Common.string_to_parametric(key_dict['SupplierParametrics'])
    
    if supplier in SupplierConfig.SupplierConfig:
      print("Rewriting '%s' from '%s'" % (supplierpn, supplier))
      rewriter = SupplierConfig.SupplierConfig[supplier][1]
      return rewriter.rewrite_parametrics(parametrics)
    else:
      return {}
          
  rewriter = Common.CsvRewriter(['Supplier', 'SupplierPartNumber', 'SupplierParametrics'], 
                                ['Desc', 'Package', 'Parameters', 'MfrDesc', 'MfrPartNumber'], 
                                process_fn)
  
  if os.path.isfile(output_filename):
    print("Existing output CSV file detected, reading in data")
    rewriter.read_output_csv(output_filename)
    
  rewriter.read_input_csv(input_filename)
  
  rewriter.write_output_csv(output_filename)  
    
  print("Done")
  