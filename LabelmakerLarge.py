import argparse
import csv 

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

import Code128
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

LABEL_SPACING_WIDTH = 0.125*inch
LABEL_SPACING_HEIGHT = 0 * inch

# Drawable area
LABEL_DWIDTH = LABEL_WIDTH - 2*LABEL_MARGIN # 2.5
LABEL_DHEIGHT = LABEL_HEIGHT - 2*LABEL_MARGIN # 0.875

LABEL_MAIN_WIDTH = 1.5*inch
LABEL_SEC_WIDTH = LABEL_DWIDTH - LABEL_MAIN_WIDTH

LABEL_TEXT_MARGIN = 0.025*inch
LABEL_TWIDTH = LABEL_DWIDTH - 2*LABEL_TEXT_MARGIN
LABEL_MAIN_TWIDTH = LABEL_MAIN_WIDTH - 2*LABEL_TEXT_MARGIN
LABEL_SEC_TWIDTH = LABEL_SEC_WIDTH - 2*LABEL_TEXT_MARGIN

FONT_LARGE = 13
FONT_MAIN = 7
FONT_SMALL = 5
HSCALE = 0.75

BARCODE_SCALE = 0.0025*inch

def draw_set(c, desc, package, parametrics, mfrdesc, mfrpn, barcode, notes,
             border=False):
  c.saveState()
  if border:
    c.roundRect(0, 0, LABEL_WIDTH, LABEL_HEIGHT, LABEL_RADIUS)
    
  c.translate(LABEL_MARGIN, LABEL_MARGIN)
  c.roundRect(0, 0, LABEL_DWIDTH, LABEL_DHEIGHT, LABEL_RADIUS)
  
  c.setLineWidth(0.5)
  
  barcode_img = Code128.code128_image(barcode)
  barcode_width, _ = barcode_img.size
  c.drawImage(ImageReader(barcode_img), 
              LABEL_TEXT_MARGIN, LABEL_TEXT_MARGIN, 
              width=barcode_width*BARCODE_SCALE, height=0.125*inch - 2*LABEL_TEXT_MARGIN)
  
  PdfCommon.draw_text(c, barcode, 
                      LABEL_DWIDTH - LABEL_TEXT_MARGIN, 0.0625*inch, 
                      clipx=LABEL_TWIDTH, anchor='rc', 
                      font='Courier', size=FONT_MAIN, hscale=HSCALE)

  c.line(0, 0.125*inch, LABEL_DWIDTH, 0.125*inch)

  w, _ = PdfCommon.draw_text(c, mfrpn, LABEL_TEXT_MARGIN, 0.1875*inch, 
                      clipx=LABEL_TWIDTH, anchor='lc', 
                      font='Courier-Bold', size=FONT_MAIN, hscale=HSCALE)
   
  PdfCommon.draw_text(c, mfrdesc, w + 4*LABEL_TEXT_MARGIN + LABEL_TEXT_MARGIN, 0.1875*inch, 
                      clipx=LABEL_TWIDTH - w - 4*LABEL_TEXT_MARGIN, anchor='lc', 
                      font='Courier', size=FONT_MAIN, hscale=HSCALE)
   
  c.line(0, 0.25*inch, LABEL_DWIDTH, 0.25*inch)
  
  c.saveState()
  p = c.beginPath()
  p.rect(LABEL_TEXT_MARGIN, 0.25*inch, LABEL_MAIN_TWIDTH, 0.375*inch)
  c.clipPath(p, stroke=0)
  
  x_pos = LABEL_TEXT_MARGIN
  for param_key, param_val in parametrics.items():
    kxinc, _ = PdfCommon.draw_text(c, param_key, x_pos, 0.3125*inch, anchor='lc', 
                                   size=FONT_SMALL, hscale=HSCALE)     
    vxinc, _ = PdfCommon.draw_text(c, param_val, x_pos, 0.4375*inch, anchor='lc', 
                                   size=FONT_MAIN, hscale=HSCALE)
    x_pos += max(kxinc, vxinc) + LABEL_TEXT_MARGIN*2
    
  c.restoreState()
    
  PdfCommon.draw_text(c, notes, LABEL_TEXT_MARGIN, 0.5625*inch, anchor='lc', 
                      size=FONT_MAIN, hscale=HSCALE)     
    
  c.line(0, 0.625*inch, LABEL_MAIN_WIDTH, 0.625*inch)
  
  PdfCommon.draw_text(c, desc, LABEL_TEXT_MARGIN, 0.75*inch, 
                      clipx=LABEL_MAIN_TWIDTH, anchor='lc',
                      font='Helvetica-Bold', size=FONT_LARGE, hscale=HSCALE)
  
  c.translate(LABEL_MAIN_WIDTH, 0)
  c.line(0, 0.25*inch, 0, LABEL_DHEIGHT)
  
  PdfCommon.draw_text(c, package, LABEL_SEC_TWIDTH + LABEL_TEXT_MARGIN, 
                      LABEL_DHEIGHT - 0.0625*inch,
                      clipx=LABEL_SEC_TWIDTH,
                      anchor='rc', size=FONT_MAIN, hscale=HSCALE)

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
    
    rownum = 0 # y position
    colnum = 0 # x position

    for row in reader:
      print("Generating %s='%s'" % (row['Barcode'], row['Desc']))
      
      if 'Directive' in row:
        if row['Directive'] == 'NOLABEL':
          continue
      
      notes = ""
      if 'Notes' in row:
        notes = row['Notes']
      
      c.saveState()
      c.translate(colnum*LABEL_WIDTH, rownum*LABEL_HEIGHT)
        
      draw_set(c, row['Desc'], row['Package'],
               Common.string_to_parametric(row['Parameters']),
               row['MfrDesc'], row['MfrPartNumber'],
               row['Barcode'], notes,
               border=args.border)
      
      c.restoreState()
      
      rownum += 1
      if rownum >= PAGE_ROWS:
        rownum = 0
        colnum += 1
      if colnum >= PAGE_COLS:
        c.showPage()
        c.translate(PAGE_MARGIN_WIDTH, PAGE_MARGIN_HEIGHT)
        c.saveState()
        colnum = 0

    c.showPage()
    c.save()
