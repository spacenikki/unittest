import unittest
import readfile
from process_log import LogAnalysis  # the class
# from process_log import find_failed_login, add_to_block, calculate_ts_diff, convert_to_timestamp

class TestLogAnalysis(unittest.TestCase):
	def test_top10_IPs(self):
		# hard set the input "log"
		# self.log = readfile.read_file("../log_input/nikki_sample.txt") 
		# log = readfile.read_file("../log_input/nikki_sample.txt") 
		# init the class, pass what it expects - "log"
		filename = '../log_input/nikki_sample.txt'
		log = readfile.read_file(filename)  
		my_analysis = LogAnalysis(log)

		# call this class' function!
		my_analysis.top10_IPs()
		# say what u expect in the RESULT
		for line in my_analysis:

			self.assertIn('219.156.97.12', "../log_output/hosts.txt")
			self.assertNotIn('unicomp6.unicomp.net', "../log_output/hosts.txt")


unittest.main()

/Users/nikkilacey/Documents/github/unittest/src/test_process_log.py