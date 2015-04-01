# parts-labelmaker
Label generator for electronic parts. Complete spreadsheet-to-labels functionality.

Dependent Python packages:
For DigiKey SWS Interface (to get component data):
  pysimplesoap
  httplib2
  A magical, not-documented-at-all PartnerID. Come on, DigiKey, if you're going to have web services, at least document it properly and open it up. In the mean time, we'll just hog your bandwidth by requesting the whole component webpage. Good job, guys.