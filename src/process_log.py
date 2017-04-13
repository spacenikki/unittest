import readfile
from operator import itemgetter
from collections import Counter
import datetime
import time
import re
from collections import defaultdict
import operator


# filename = '../log_input/log.txt'
filename = '../log_input/nikki_sample.txt'
log = readfile.read_file(filename)  

class LogAnalysis():
	def __init__(self, log):
		self.log = log

	# Feature 1 -  find the top 10 ips
	def top10_IPs(self):
		ips_list = []
		for line in log:
			host = line.host
			if host is not None:
				ips_list.append(host)
		
		unqiue_ips_with_counts = Counter(ips_list)

		#  sort the dict
		top_10_host = sorted(unqiue_ips_with_counts.items(), key=operator.itemgetter(1), reverse=True)[:10]
		

		# for (host, count) in top_10_host:
		# 	print "%s\t%d" % (host, count)

		host_rst = "../log_output/hosts.txt"
		with open(host_rst, 'w') as file_object:
			for (host, count) in top_10_host:
				file_object.write(host + ', ')
				file_object.write(str(count) + '\n')

	# # Feature 2: Identify the top 10 resources on the site that consume the most bandwidth. Bandwidth consumption can be extrapolated from bytes sent over the network and the frequency by which they were accessed.
	def top10_resources(self):
		
		line_no = 0 
		path_list = [] 
		path_bytes = {}
		
		for line in log:
			line_no += 1
			path = line.path 
			bytes = line.bytes

			if path is not None:
				path_list.append(path) 
				if path not in path_bytes:  
					path_bytes[path] = int(bytes)
				else:
					path_bytes[path] += int(bytes)
			
		path_counts = Counter(path_list)  # return unqiue path with occurence - dict form
		
		unique_path = path_counts.keys()
		
		total_bw_tuple = []

		# loop through it, calculate counts/ min & bytes/ mins
		for path in unique_path:
			counts_pm = path_counts[path]/ 60.0
			bytes_pm = path_bytes[path] / 60.0
			# add (path ,  counts/ min * bytes/ mins) - to a tuple - easier to sort!
			total_bw_tuple.append((path, counts_pm*bytes_pm))

		#  sort tuple:
		sorted_bw_tuple = sorted(total_bw_tuple, key=itemgetter(1), reverse=True)
		top_10_resource = sorted_bw_tuple[:10]

		 # top 10 should be added to the new file
		resources_rst = "../log_output/resources.txt"
		with open(resources_rst, 'w') as file_object:
			for (path, count) in top_10_resource:
				file_object.write(path + '\n' )


	# feature 3 - 
	def top10_60mins(self):
		top60mins = []
		dt_array = []
		dt_tup_array = []  # tuple to hold (time, count)
		ct = 1

		for line in log:

			date_time = line.datetime  # 01/Jul/1995:00:00:14 -0400
			
			if date_time is not None:

				# add each date_time to an array -sorted
				dt_array.append(date_time)   # "01/Jul/1995:00:03:47 -0400"
				dt_array.sort()

		# go through each element in array, compare if == same, then ct += 1, if not, .append( time , ct)
		ct = 1 
		for i in xrange(len(dt_array)):
			if i == len(dt_array) - 1: # avoid out of range
				dt_tup_array.append((dt_array[i], ct))

			elif dt_array[i] == dt_array[i+1]:
				ct += 1

			else:
				dt_tup_array.append((dt_array[i], ct))
				ct = 1

		# return a SORTED tuple that has (unique time, counts)
		# print dt_tup_array  # already sorted by DATE 0 [('01/Jul/1995:00:00:14 -0400', 2), ('01/Jul/1995:00:00:18 -0400', 1), ('01/Jul/1995:00:00:20 -0400', 1)]

		if len(dt_tup_array) < 2:
			print "append each line to a new file"
		else:  # > 10 lines
			s = 0
			e = 1

			while e < len(dt_tup_array):  # exit when > 60mins  or e hits the end
				# keep comparing the ts_diff
				diff_ts = calculate_ts_diff(e, s, dt_tup_array) # return diff_ts
				# 60mins block - 60sec/min * 60 mins - total seconds
				sixtymins_block = 60*60

				if diff_ts == 0:  # all are unique record - so if it's no diff - means s==e, then e needs to move 1 up
					e += 1

				elif diff_ts <= sixtymins_block: # enter when > 60  
					e += 1
						
				elif diff_ts > sixtymins_block:  # enter - when diff_ts > 60 
					count = 0
					for i in xrange(e - s):
						count += dt_tup_array[s+i][1]
					top60mins.append((dt_tup_array[s][0], count))
					s += 1  # e stays				
			
			# if exit because of e == len(tup)
			if e == len(dt_tup_array):
				print "entering e hit the end"
				count = 0 
				for i in xrange(e - s):
					count += dt_tup_array[s+i][1]
				top60mins.append((dt_tup_array[s][0], count))

		# sort top60mins by "count"
		top_60mins_sorted = sorted(top60mins, key=itemgetter(1), reverse = True)[:10]
		
		hours_rst = "../log_output/hours.txt"
		with open (hours_rst, 'w') as file_object:
			for (time_info, count) in top_60mins_sorted:
				file_object.write(time_info + ', ' + str(count) + '\n')

	def blocked_log(self):
		blocked_rst = "../log_output/blocked.txt"
		with open(blocked_rst, 'w') as file_object:  	
			file_object.write("If there is no content here, that means none of the entry has 3 consecutive failed login within 20 seconds window \n")

		record_by_host = defaultdict(list)
		
		for r in log:
			if r.host not in record_by_host:
				record_by_host[r.host] = [(r.datetime, r.path, r.code, r.line)]
			else:
				record_by_host[r.host].append((r.datetime, r.path, r.code, r.line))

		# print "record_by_host is ", len(record_by_host) , record_by_host
		# {'freenet.edmonton.ab.ca': [('01/Jul/1995:00:00:12 -0400', '/images/dual-pad.gif', '200'), ('01/Jul/1995:00:00:16 -0400', '/love/dual-pad.gif', '200')], '210.238.40.43': [('01/Jul/1995:00:00:09 -0400', '/', '200')], '199.72.81.55': [('01/Jul/1995:00:00:01 -0400', '/history/apollo/', '200')]}

		for host, allrecord in record_by_host.viewitems():
			#  sort the tuple inside array under each host - =allrecord by time!
			record_by_host[host] = sorted(allrecord, key=itemgetter(0))
			# before sorted: {'199.72.81.55': [('01/Jul/1995:00:00:11 -0400', '/history/apollo/', '200'), ('01/Jul/1995:00:00:05 -0400', '/', '200'), ('01/Jul/1995:00:00:09 -0400', '/shuttle/technology/images/sts_spec_6-small.gif', '200')]})
			# after sort: {'199.72.81.55': [('01/Jul/1995:00:00:05 -0400', '/', '200'), ('01/Jul/1995:00:00:09 -0400', '/shuttle/technology/images/sts_spec_6-small.gif', '200'), ('01/Jul/1995:00:00:11 -0400', '/history/apollo/', '200')]})
		
		for host, allrecord in record_by_host.viewitems():

			#  this block is just going to find where s is 
			first_attempt_index = find_failed_login(0, allrecord)  # return the index 

			if first_attempt_index is None:
				print "first_attemp_index is None - no failed login is found! inside, host is", host
				
			else:
				 # None is returned because no failed login found!			
				e = first_attempt_index + 1
				count = 1

				while e < len(allrecord): 
					# if count ==3  begins
					if count == 3:
						last_attempt_time = convert_to_timestamp(allrecord[e-1][0])
						five_mins_block = last_attempt_time + 60*5
						
						p = add_to_block(e, allrecord, five_mins_block)  # return "p" 6
						
						# p will be where "si" @ func find_failed_login() -> that return "s"
						# check if p is out of range
						if p == len(allrecord):
							e = p   #  infinite loop when e never got updated
							# print "It reaches the end of the allrecord of current host, should work on the next host"
						else: # p max is last index or less
							# start at where p is and loo for the next login failed attempt
							count = 0 # reset count as - same host next entry > 5mins block that it may have next +ve OR -ve find_failed_login!

							first_attempt_index = find_failed_login(p, allrecord)
							# record the time when failed login attempt occurs

							if first_attempt_index is None:  # exit if no more failed attempt
								break  # to exit the allrecord of current host
							
							else: # a new failed attempt is found
								print "count after coming back from adding to block", count
								e = first_attempt_index + 1
								count = 1 # as 1 failed login is found @ s !
									# ************** choose only one to set a!! ****************
								print "****  "
								print "e is inside while e < len(allrecord) to start ", e
					
					elif e >= len(allrecord) - 1 :  # if e is @ last index or >1 after coming out from count ==3 
						return   # not sure if I use break/ pass correctly
						
					elif e < len(allrecord):  # if e is before last index means not end yet
						a = calculate_ts_diff(e, first_attempt_index, allrecord) 

						# check calculate_ts_diff begins
						if calculate_ts_diff(e, first_attempt_index, allrecord) > 20:
							if (allrecord[e][1] == "/login" and not(allrecord[e][2].startswith("2"))) or (allrecord[e][1] != "/login") or ((allrecord[e][1] == "/login") and (allrecord[e][2].startswith("2"))): # failed login 
								
								count = 0

								first_attempt_index = find_failed_login(e, allrecord)  # return the index - #  find the next failed login again

								if first_attempt_index is None:
									break  # no more failed attempt under this host
								else:
									#  call to find the next failed login first attempt index
									# that index comes back, will be where e should be
									e = first_attempt_index + 1
									count = 1 

						elif calculate_ts_diff(e, first_attempt_index, allrecord) <= 20:
							#  failed attempt
							if allrecord[e][1] == "/login" and not(allrecord[e][2].startswith("2")): # failed login 
								count += 1
								e += 1 # first failed attempt time unchanged

							elif allrecord[e][1] != "/login": # request is sth else, doesnt get to reset count!
								e += 1

							elif allrecord[e][1] == "/login" and (allrecord[e][2].startswith("2")): 
								count = 0 # sucess login get to reset count = 0
								first_attempt_index = find_failed_login(e, allrecord)  # return the index - #  find the next failed login again

								if first_attempt_index is None:
									break  # no more failed attempt under this host
								else:
									# only if first_attem index != none, then do below
									e = first_attempt_index + 1
									count = 1 
					
					else:  
						print "e didn't get filtered ... something is wrong", e

				if e == len(allrecord): # end of "while e < len(allrecord): "
					print "There is not enough record to be blocked for this host", host
					exit


def find_failed_login(startindex, allrecord):
	# it stops running when hitting the last index!
	for record in allrecord[startindex:]: # record[2]  # 300  #record[1]  # /path
		if record[1] == "/login" and not (record[2].startswith("2")): # if failed login
			return startindex    # where s is returned - should be the LINE that says "failed login!"
		else:
			startindex += 1
			# e return None if not found

def add_to_block(startindex, allrecord, five_mins_block):
	blocked_rst = "../log_output/blocked.txt"
	
	with open(blocked_rst, 'a') as file_object:  # or "a"?	
		while startindex < len(allrecord):
			if convert_to_timestamp(allrecord[startindex][0]) < five_mins_block:
				file_object.write(allrecord[startindex][3])   # whole thing is -> (r.datetime, r.path, r.code, r.line)
				startindex += 1
			else:
				return startindex
		# exit when 1. >5mins or p == len(allrecord)
		file_object.write("\n")
		return startindex



def calculate_ts_diff(e, s, dt_tup_array):
	e_ts = convert_to_timestamp(dt_tup_array[e][0])  #  need to be convert
	s_ts = convert_to_timestamp(dt_tup_array[s][0])  #  need to be convert
	diff_ts = abs(e_ts - s_ts)
	return diff_ts


def convert_to_timestamp(selected_time):
	# calculate timestamp of whole s1[0] - 01/Jul/1995 00:00:06 -400 - selected_time
	# use regex to break down "date_time" & "timezone"
	if re.search(r'(\d+/\w+/\d+:\d+:\d+:\d+)? (-\d.)?', selected_time, re.M|re.I): # found  # date, time, timezone!
		mytimestamp = re.search(r'(\d+/\w+/\d+:\d+:\d+:\d+)? (-\d.)?', selected_time, re.M|re.I)
		date_time = mytimestamp.group(1) # 01/Jul/1995:00:00:04
		timezone = mytimestamp.group(2)  #-04
		tz_in_sec = int(timezone)*60*60

		final_timestamp = (time.mktime(datetime.datetime.strptime(date_time, "%d/%b/%Y:%H:%M:%S").timetuple())) + (tz_in_sec)
		return final_timestamp
		




if __name__ == '__main__':
	insight = LogAnalysis(log)
	insight.top10_IPs()
	insight.top10_resources()
	insight.top10_60mins()
	insight.blocked_log()



/Users/nikkilacey/Documents/github/unittest/src/process_log.py

