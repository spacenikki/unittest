import unittest
import readfile
from process_log import LogAnalysis  # the class
# from process_log import find_failed_login, add_to_block, calculate_ts_diff, convert_to_timestamp

class TestLogAnalysis(unittest.TestCase):
	def test_top10_IPs(self):
		# 1. input something
		# init the class, pass what it expects - "log"
		filename = '../log_input/nikki_sample.txt'
		log = readfile.read_file(filename)  
		my_analysis = LogAnalysis(log)

		#  2. proceed it - gain result
		# call this class' function!
		my_analysis.top10_IPs()   #create a file called hosts.txt
		
		#  3. Build a result for unittest to look at, add assert statement to check
		# say what u expect in the RESULT
		# open the file, and read that line by line

		with open("../log_output/hosts.txt", 'r') as top10_host:
			content = top10_host.readlines()  # list - ['210.238.40.43, 6\n', '199.72.81.56, 2\n']
			# print content
			ips = []
			for line in content:
				ip = line.split(", ")[0]
				ips.append(line.split(", ")[0])

			# print ips  # ['210.238.40.43', '199.72.81.56', '207.237.55.38', '207.237.55.28', '211.237.55.28', '199.72.81.55', '219.156.97.12', '199.72.81.57', '199.72.81.58', '219.156.97.22']

			self.assertIn('219.156.97.12', ips)
			self.assertNotIn('unicomp6.unicomp.net', ips)


# code below does not work
		# top_10host_count = "../log_output/hosts.txt"
		# f = open(top_10host_count, "r")
		# self.assertIn('219.156.97.12', f)


unittest.main()

# /Users/nikkilacey/Documents/github/unittest/src/test_process_log.py






















