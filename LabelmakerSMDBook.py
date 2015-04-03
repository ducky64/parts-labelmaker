import argparse
import csv 

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader

import Code128
import Common
import PdfCommon

PAGE_MARGIN_WIDTH = 1*cm
PAGE_MARGIN_HEIGHT = 11*inch - 1*cm

PAGE_ROWS = 12
PAGE_COLS = 6

LABEL_WIDTH = 5*cm
LABEL_HEIGHT = 1.45*cm

LABEL_MAIN_WIDTH = 3*cm
LABEL_SEC_WIDTH = LABEL_WIDTH - LABEL_MAIN_WIDTH

LABEL_TEXT_MARGIN = 0.025*inch
LABEL_TWIDTH = LABEL_WIDTH - 2*LABEL_TEXT_MARGIN
LABEL_MAIN_TWIDTH = LABEL_MAIN_WIDTH - 2*LABEL_TEXT_MARGIN
LABEL_SEC_TWIDTH = LABEL_SEC_WIDTH - 2*LABEL_TEXT_MARGIN
LABEL_THEIGHT = LABEL_HEIGHT - 2*LABEL_TEXT_MARGIN

FONT_LARGE = 9
FONT_MAIN = 7
FONT_SMALL = 5
HSCALE = 0.85

def draw_set(c, desc, package, parametrics, mfrdesc, mfrpn, barcode, notes,
             border=False):
  c.saveState()
  
  PdfCommon.draw_text(c, desc, LABEL_TEXT_MARGIN, 0.2*cm, 
                      clipx=LABEL_TWIDTH, anchor='lc',
                      font='Helvetica-Bold', size=FONT_MAIN, hscale=HSCALE)
  
  PdfCommon.draw_text(c, package, LABEL_TWIDTH+LABEL_TEXT_MARGIN, 0.2*cm, 
                      clipx=LABEL_TWIDTH, anchor='rc',
                      size=FONT_MAIN, hscale=HSCALE)
  
  c.saveState()
  p = c.beginPath()
  p.rect(LABEL_TEXT_MARGIN, 0.3*cm, LABEL_MAIN_TWIDTH, 1.2*cm)
  c.clipPath(p, stroke=0)
  
  x_pos = LABEL_TEXT_MARGIN
  for param_key, param_val in parametrics.items():
    kxinc, _ = PdfCommon.draw_text(c, param_key, x_pos, 0.45*cm, anchor='lc', 
                                   size=FONT_SMALL, hscale=HSCALE)     
    vxinc, _ = PdfCommon.draw_text(c, param_val, x_pos, 0.7*cm, anchor='lc', 
                                   size=FONT_MAIN, hscale=HSCALE)
    x_pos += max(kxinc, vxinc) + LABEL_TEXT_MARGIN*2
    
  c.restoreState()

  c.line(0, 0.9*cm, LABEL_MAIN_WIDTH, 0.9*cm)

  PdfCommon.draw_text(c, mfrpn, LABEL_TEXT_MARGIN, 1.05*cm, 
                      clipx=LABEL_MAIN_TWIDTH, anchor='lc', 
                      font='Courier-Bold', size=FONT_MAIN, hscale=HSCALE)
  
  PdfCommon.draw_text(c, mfrdesc, LABEL_TEXT_MARGIN, 1.3*cm, 
                      clipx=LABEL_MAIN_TWIDTH, anchor='lc', 
                      font='Courier', size=FONT_MAIN, hscale=HSCALE)
  


  c.translate(LABEL_MAIN_WIDTH, 0)
  
  c.line(0, 0.4*cm, LABEL_SEC_WIDTH, 0.4*cm)
  c.line(0, 0.4*cm, 0, LABEL_HEIGHT)
  
  barcode_img = Code128.code128_image(barcode)
  c.drawImage(ImageReader(barcode_img), 
              LABEL_TEXT_MARGIN, LABEL_TEXT_MARGIN + 0.4*cm, 
              width=LABEL_SEC_TWIDTH, height=LABEL_THEIGHT - 0.2*cm - 0.4*cm)
  
  PdfCommon.draw_text(c, barcode, 
                      LABEL_TEXT_MARGIN + LABEL_SEC_TWIDTH / 2, 
                      LABEL_TEXT_MARGIN + LABEL_THEIGHT - 0.08*cm,
                      clipx=LABEL_SEC_TWIDTH, anchor='cc', 
                      font='Courier', size=FONT_MAIN)

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
    c.rotate(-90)
    c.saveState()
    
    c.line(0, 0, 0, LABEL_HEIGHT * PAGE_ROWS)
    
    rownum = 0 # x position
    colnum = 0 # y position

    for row in reader:
      print("Generating %s='%s'" % (row['Barcode'], row['Desc']))
      notes = ""
      if 'Notes' in row:
        notes = row['Notes']
      c.line(0, 0, LABEL_WIDTH, 0)
      draw_set(c, row['Desc'], row['Package'],
               Common.string_to_parametric(row['Parameters']),
               row['MfrDesc'], row['MfrPartNumber'],
               row['Barcode'], notes,
               border=args.border)
      
      c.translate(0, LABEL_HEIGHT)
      
      rownum += 1
      if rownum >= PAGE_ROWS:
        c.line(0, 0, LABEL_WIDTH, 0)
        c.restoreState()
        c.line(LABEL_WIDTH, 0, LABEL_WIDTH, LABEL_HEIGHT * PAGE_ROWS)
        c.translate(LABEL_WIDTH, 0)
        c.saveState()
        rownum = 0
        colnum += 1
      if colnum >= PAGE_COLS:
        c.showPage()
        c.translate(PAGE_MARGIN_WIDTH, PAGE_MARGIN_HEIGHT)
        c.rotate(-90)
        c.saveState()
        colnum = 0

    c.showPage()
    c.save()
