import argparse
import csv 

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader

import Code128
import Common
import PdfCommon

PAGE_MARGIN_WIDTH = 8.5*inch - 1*cm
PAGE_MARGIN_HEIGHT = 1*cm

PAGE_ROWS = 12
PAGE_COLS = 4

PAGE_WIDTH = 6.5*cm

LABEL_WIDTH = 5*cm
LABEL_HEIGHT = 1.42*cm

LABEL_MAIN_WIDTH = 3*cm
LABEL_SEC_WIDTH = LABEL_WIDTH - LABEL_MAIN_WIDTH

LABEL_TEXT_MARGIN = 0.025*inch
LABEL_TWIDTH = LABEL_WIDTH - 2*LABEL_TEXT_MARGIN
LABEL_MAIN_TWIDTH = LABEL_MAIN_WIDTH - 2*LABEL_TEXT_MARGIN
LABEL_SEC_TWIDTH = LABEL_SEC_WIDTH - 2*LABEL_TEXT_MARGIN
LABEL_THEIGHT = LABEL_HEIGHT - 2*LABEL_TEXT_MARGIN

FONT_HUGE = 11
FONT_LARGE = 8
FONT_MAIN = 6
FONT_SMALL = 5
HSCALE = 0.8

class SmdBookLabels():
  def __init__(self, c):
    self.c = c
    self.rownum = 0
    self.colnum = 0
    
    self.init_page()
    
  def new_col(self, col_name=""):
    if self.rownum != 0:
      self.rownum = 0
      self.colnum += 1
      c.restoreState()
      if self.colnum >= PAGE_COLS:
        self.new_page()
    self.init_col(col_name)
    
  def init_col(self, col_name=""):
    c.saveState()
    c.translate(PAGE_WIDTH * self.colnum, 0)
    c.line(0, -10000, 0, LABEL_HEIGHT * PAGE_ROWS + 10000)
    c.line(LABEL_WIDTH, 0, LABEL_WIDTH, LABEL_HEIGHT * PAGE_ROWS)
    c.line(LABEL_WIDTH + 0.5*cm, 0, LABEL_WIDTH + 0.5*cm, LABEL_HEIGHT * PAGE_ROWS)
    c.line(PAGE_WIDTH, -10000, PAGE_WIDTH, LABEL_HEIGHT * PAGE_ROWS + 10000)
    PdfCommon.draw_rotated_text(c, col_name, 
                                LABEL_WIDTH + 0.25*cm, 
                                LABEL_HEIGHT * PAGE_ROWS / 2,
                                rot=90,
                                font='Helvetica-Bold', size=FONT_HUGE)
    
    c.line(0, 0, PAGE_WIDTH, 0)
    c.line(0, LABEL_HEIGHT * PAGE_ROWS, PAGE_WIDTH, LABEL_HEIGHT * PAGE_ROWS)

  def new_page(self):
    if self.colnum == 0:
      return
    self.colnum = 0
    c.showPage()
    self.init_page()
    
  def init_page(self):
    c.translate(PAGE_MARGIN_WIDTH, PAGE_MARGIN_HEIGHT)
    c.rotate(90)
    c.setLineWidth(0.5)
    self.init_col()

  def empty_set(self):
    self.rownum += 1

  def draw_set(self, desc, package, parametrics, mfrdesc, mfrpn, barcode, notes,
               cells=1, border=False):
    if self.rownum >= PAGE_ROWS:
      self.new_col()
      
    self.c.saveState()
    self.c.translate(0, LABEL_HEIGHT * self.rownum)
    c.line(0, 0, LABEL_WIDTH, 0)
    c.line(0, LABEL_HEIGHT*cells, LABEL_WIDTH, LABEL_HEIGHT*cells)
    
    self.c.setLineWidth(0.25)
    
    PdfCommon.draw_text(self.c, desc, LABEL_TEXT_MARGIN, 0.2*cm, 
                        clipx=LABEL_MAIN_TWIDTH, anchor='lc',
                        font='Helvetica-Bold', size=FONT_LARGE, hscale=HSCALE)
    
    PdfCommon.draw_text(self.c, package, LABEL_MAIN_TWIDTH+LABEL_TEXT_MARGIN, 0.2*cm, 
                        clipx=LABEL_MAIN_TWIDTH, anchor='rc',
                        size=FONT_LARGE, hscale=HSCALE)
    
    self.c.saveState()
    p = self.c.beginPath()
    p.rect(LABEL_TEXT_MARGIN, 0.3*cm, LABEL_MAIN_TWIDTH, 1.2*cm)
    self.c.clipPath(p, stroke=0)
    
    x_pos = LABEL_TEXT_MARGIN
    for param_key, param_val in parametrics.items():
      kxinc, _ = PdfCommon.draw_text(self.c, param_key, x_pos, 0.475*cm, anchor='lc', 
                                     size=FONT_SMALL, hscale=HSCALE)     
      vxinc, _ = PdfCommon.draw_text(self.c, param_val, x_pos, 0.7*cm, anchor='lc', 
                                     size=FONT_MAIN, hscale=HSCALE)
      x_pos += max(kxinc, vxinc) + LABEL_TEXT_MARGIN*2
      
    self.c.restoreState()
  
    self.c.line(0, 0.9*cm, LABEL_MAIN_WIDTH, 0.9*cm)
  
    PdfCommon.draw_text(self.c, mfrpn, LABEL_TEXT_MARGIN, 1.03*cm, 
                        clipx=LABEL_MAIN_TWIDTH, anchor='lc', 
                        font='Courier-Bold', size=FONT_MAIN, hscale=HSCALE)
    
    PdfCommon.draw_text(self.c, mfrdesc, LABEL_TEXT_MARGIN, 1.28*cm, 
                        clipx=LABEL_TWIDTH, anchor='lc', 
                        font='Courier', size=FONT_MAIN, hscale=HSCALE)

    self.c.translate(LABEL_MAIN_WIDTH, 0)
    
    self.c.line(0, LABEL_HEIGHT-0.3*cm, LABEL_SEC_WIDTH, LABEL_HEIGHT-0.3*cm)
    self.c.line(0, 0, 0, LABEL_HEIGHT-0.3*cm)
    
    barcode_img = Code128.code128_image(barcode)
    self.c.drawImage(ImageReader(barcode_img), 
                     LABEL_TEXT_MARGIN, LABEL_TEXT_MARGIN, 
                     width=LABEL_SEC_TWIDTH, height=LABEL_THEIGHT - 0.2*cm - 0.3*cm)
    
    PdfCommon.draw_text(self.c, barcode, 
                        LABEL_TEXT_MARGIN + LABEL_SEC_TWIDTH / 2, 
                        LABEL_TEXT_MARGIN + LABEL_THEIGHT - 0.38*cm,
                        clipx=LABEL_SEC_TWIDTH, anchor='cc', 
                        font='Courier', size=FONT_MAIN)
  
    c.restoreState()
  
    self.rownum += cells
  
INPUT_POSTFIX = "_labeled"

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""
  Generates the PDF label sheet from the output of Fieldgen.
  """)
  parser.add_argument('--filename', '-f', required=True,
                      help="Input filename, without the .csv extension")
  args = parser.parse_args()
  
  input_filename = args.filename + INPUT_POSTFIX + '.csv'
  output_filename = args.filename + '.pdf'
  
  with open(input_filename, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    
    c = canvas.Canvas(output_filename, pagesize=letter, bottomup=0)
    
    labelgen = SmdBookLabels(c)

    for row in reader:
      print("Generating %s='%s'" % (row['Barcode'], row['Desc']))
      
      if 'Page' in row and row['Page']:
        labelgen.new_col(row['Page'])
      
      notes = ""
      if 'Notes' in row:
        notes = row['Notes']
        
      cells = 1
      if 'Cells' in row and row['Cells']:
        cells = int(row['Cells'])
          
      labelgen.draw_set(row['Desc'], row['Package'],
                        Common.string_to_parametric(row['Parameters']),
                        row['MfrDesc'], row['MfrPartNumber'],
                        row['Barcode'], notes, cells=cells)

    c.showPage()
    c.save()
