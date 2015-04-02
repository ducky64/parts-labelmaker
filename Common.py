def parametric_to_string(parametric_dict):
  out = ""
  for key, val in parametric_dict.items():
    key = key.replace('=', '').replace(';', '')
    val = val.replace('=', '').replace(';', '')
    if out:
      out += ";"
    out += key + "=" + val
  return out
