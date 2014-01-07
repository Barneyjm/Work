import argparse
import csv

"""
CSV reader for a bunch of facebook profiles and their likes. 
Turns ugly, humongus csvs into something more managable. 

@author James Barney
@version 1.0 12/19/13

"""

class CsvParser():
	def __init__(self, args):
		self.all_likes = set()
		self.filename = args.filename
		
	def read(self, args):
		"""
		Reads the given CSV file and prepares the set of organized tuples 
		for saving to the new CSV file. 
		"""
		with open(self.filename, 'rb') as csvfile:
			filereader = csv.reader(csvfile)
			for row in filereader:			#reads the csv line by line
				for num in row:				#reads each entry in the csv
					if num != 'NA' and not num.startswith('V'): 	#cuts out the crap we don't care about
						self.all_likes.add((row[0],num))			#adds a tuple to the set 'all_likes' with (<IDnum>, <likedIDnum>)
					else:
						continue
						
	def write(self, args):
		"""
		Writes the pre-prepared set of tuples from the read() method to 
		a new CSV for other programs to digest easier. 
		"""
		newcsvfile = self.filename[:len(self.filename)-4] + "NEW.csv" #clever naming MIGHT NEED TO CHANGE THIS LATER/OVERWRITE OLD FILE?
		with open(newcsvfile, 'wb') as f:
			writer = csv.writer(f)
			writer.writerows(self.all_likes)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='process facebook likers from ugly csvs')
    parser.add_argument('--filename', '-f', help='specify filename', type = str)
    
    args = parser.parse_args()
    
    csv_parser = CsvParser(args)
    
    # does all the dirty work below
    csv_parser.read(args)
    csv_parser.write(args)
