# parts-labelmaker
Label generator for electronic parts. Complete spreadsheet-to-labels functionality.

Dependent Python packages:
For the DigiKey crawler interface (to get component data):
- httplib2
- BeautifulSoup4

The actual label generation requires:
- ReportLab

There are 3 stages to generating the complete labels from a list of part numbers:
1. Annotation: this pulls relevant part data (including parametrics) from the supplier's site, outputting a CSV.
2. Field generation: this turns the supplier data into label fields, outputting another CSV.
3. PDF generation: this generates the label sheet PDF from the label fields.

To run an example with through-hole parts for 2 5/8" x 1" labels, run this:
python Annotator.py -f testset-pth && python Fieldgen.py -f testset-pth && python LabelmakerLarge.py -f testset-pth

To run an example with surface-mount parts for a surface-mount book, run this:
python Annotator.py -f testset-smd && python Fieldgen.py -f testset-smd && python LabelmakerSMDBook.py -f testset-smd
