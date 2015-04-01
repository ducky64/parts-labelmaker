import argparse

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
  editing.
  """)
  parser.add_argument('--filename', '-f', required=True,
                      help="Input filename, without the .csv extension")
  args = parser.parse_args()
  
  