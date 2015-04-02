def draw_text(c, text, x=0, y=0, clipx=None, anchor='cc', 
              font='Helvetica', size=8, hscale=1):
  t = c.beginText()
  t.setTextOrigin(0, 0)
  t.setHorizScale(hscale*100)
  t.setFont(font, size)
  t.textOut(text)

  c.saveState()
  c.translate(x, y)
  if clipx is not None:
    p = c.beginPath()
    if anchor[0] == 'l':
      p.rect(0, -10000, clipx, 20000)
    elif anchor[0] == 'c':
      p.rect(-clipx/2, -10000, clipx, 20000)
    elif anchor[0] == 'r':
      p.rect(-clipx, -10000, clipx, 20000)
    else:
      assert(False)
    c.clipPath(p, stroke=0)
      
  if anchor[0] == 'l':
    c.translate(0, 0)
  elif anchor[0] == 'c':
    c.translate(-t.getX()/2*hscale, 0)
  elif anchor[0] == 'r':
    c.translate(-t.getX()*hscale, 0)
  else:
    assert(False)
    
  if anchor[1] == 't':
    c.translate(0, 0)
  elif anchor[1] == 'c':
    c.translate(0, size/3.2)
  elif anchor[1] == 'b':
    c.translate(0, size/1.6)
  else:
    assert(False)
    
  c.drawText(t)
  c.restoreState()
  
  return (t.getX(), size/1.6)
  
def draw_smallcaps(c, text, scale_lower=0.8, scale_upper=1, **kwargs):
  pass  # INTEGRATE WITH DRAW_TEXXT
#   t = c.beginText()
#   t.setTextOrigin(0, 0)
#   t.setHorizScale(hscale*100)
#   for char in text:
#     if char.isalpha() and not char.isupper():
#       t.setFont(font, size*scale_lower)
#     else:
#       t.setFont(font, size*scale*upper
#     t.textOut(char.upper())
#     
#   c.saveState()
#   c.translate(x, y)
#   c.translate(-t.getX()/2*hscale, -t.getY()/2)
#   c.drawText(t)
#   c.restoreState()
  
def draw_rotated_text(c, text, x=0, y=0, rot=-90, **kwargs):
  c.saveState()
  c.translate(x, y)
  c.rotate(rot)
  draw_smallcaps(c, text, **kwargs)
  c.restoreState()
