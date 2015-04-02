import argparse
import csv 

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

import Common
import PdfCommon

PAGE_MARGIN_WIDTH = (3./16)*inch
PAGE_MARGIN_HEIGHT = 0.5*inch

PAGE_ROWS = 10
PAGE_COLS = 3

LABEL_WIDTH = 2.625*inch
LABEL_HEIGHT = 1*inch
LABEL_RADIUS = 0.0625*inch
LABEL_MARGIN = 0.0625*inch

# Drawable area
LABEL_DWIDTH = LABEL_WIDTH - 2*LABEL_MARGIN # 2.5
LABEL_DHEIGHT = LABEL_HEIGHT - 2*LABEL_MARGIN # 0.875

LABEL_MAIN_WIDTH = 1.5*inch

def draw_set(c, desc, package, parametrics, mfrdesc, mfrpn, barcode, 
             border=False):
  c.saveState()
  if border:
    c.roundRect(0, 0, LABEL_WIDTH, LABEL_HEIGHT, LABEL_RADIUS)
    
  c.translate(LABEL_MARGIN, LABEL_MARGIN)
  c.roundRect(0, 0, LABEL_DWIDTH, LABEL_DHEIGHT, LABEL_RADIUS)
  
  PdfCommon.draw_text(c, desc, LABEL_MARGIN, 0.125*inch, anchor='lc', size=10)
  c.line(0, 0.25*inch, LABEL_MAIN_WIDTH, 0.25*inch)
  
  c.line(0, 0.625*inch, LABEL_MAIN_WIDTH, 0.625*inch)
  PdfCommon.draw_text(c, mfrdesc, LABEL_MARGIN, 0.6875*inch, anchor='lc', 
                      font='Courier', size=6)
  c.line(0, 0.75*inch, LABEL_MAIN_WIDTH, 0.75*inch)
  PdfCommon.draw_text(c, mfrpn, LABEL_MARGIN, 0.8125*inch, anchor='lc', 
                      font='Courier-Bold', size=6)
  
  c.translate(LABEL_MAIN_WIDTH, 0)
  c.line(0, 0, 0, LABEL_DHEIGHT)
  
  PdfCommon.draw_text(c, package, LABEL_MARGIN, 0.0625*inch, anchor='lc')
  
  # Draw left side summary
  #draw_rotated_text(c, "UCB EE192", 0, height/2)
  #draw_centered_text(c, summary, summary_width/2, height*.5, size=48, hscale=.75)
  #draw_centered_text(c, date, summary_width/2, height*0.95, font="Courier", size=9)
  
  # Draw separator
  #c.line(summary_width, 0, summary_width, height)
  
  # Draw right side barcode

  
  #c128.getImage(code, 50).save("bar-%s.png" % code)
  #c.drawImage("bar-%s.png" % code, 0.125*inch, 0.1*inch, width=barcode_width-0.125*inch, height=height*0.8-0.1*inch)
  #draw_centered_text(c, code, barcode_width/2, height*0.95, font="Courier", size=9)
  
  c.restoreState()
  
INPUT_POSTFIX = "_labeled"
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""
  Generates the PDF label sheet from the output of Fieldgen.
  """)
  parser.add_argument('--filename', '-f', required=True,
                      help="Input filename, without the .csv extension")
  parser.add_argument('--border', '-b', type=bool, default=False,
                      help="Generate borders around each label (for debugging)")
  args = parser.parse_args()
  
  input_filename = args.filename + INPUT_POSTFIX + '.csv'
  output_filename = args.filename + '.pdf'
  
  with open(input_filename, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    
    c = canvas.Canvas(output_filename, pagesize=letter, bottomup=0)
    c.translate(PAGE_MARGIN_WIDTH, PAGE_MARGIN_HEIGHT)
    c.saveState()
    
    rownum = 0 # x position
    colnum = 0 # y position

    for row in reader:
      print("Generating %s='%s'" % (row['Barcode'], row['Desc']))
      draw_set(c, row['Desc'], row['Package'],
               Common.string_to_parametric(row['Parameters']),
               row['MfrDesc'], row['MfrPartNumber'],
               row['Barcode'],
               border=args.border)
      
      c.translate(0, LABEL_HEIGHT)
      
      rownum += 1
      if rownum >= PAGE_ROWS:
        c.restoreState()
        c.translate(LABEL_WIDTH, 0)
        c.saveState()
        rownum = 0
        colnum += 1
      if colnum >= PAGE_COLS:
        c.showPage()
        c.translate(PAGE_MARGIN_WIDTH, PAGE_MARGIN_HEIGHT)
        colnum = 0
        # TODO implement multiple pages
            
    c.showPage()
    c.save()
