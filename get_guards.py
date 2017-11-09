import re
guards = []
guard_examined =""
guard_info = ""
guard_only_ips_bandwidth = {}
guard_exit_ips_bandwidth = {}
file = open('guard_ips_with_bandwidth.txt', 'w')
ip_regex = r'(?:\d{1,3}\.)+(?:\d{1,3})'
wgg = 0
wgd = 0
wgd_index =0
num_guards =0
f = open('2017-10-14-02-00-00-consensus.txt','r')
guard_ips_weighted = {}
for line in f:
	if line[0] == 'r':
		guard_examined = line
	elif line[0] == 's':
		guard_info = line
	elif line[0] == 'w':
		if 'Guard' in guard_info:
			guard_ip = str(re.search(ip_regex,guard_examined).group(0))
			if Guard
			bandwidth = line.split(" ")
			bandwidth = bandwidth[1].split('=')
			num_guards += 1
			if guard_ip in guard_only_ips_bandwidth:
				print(guard_ip)
			if 'Exit' in guard_info:
				guard_exit_ips_bandwidth[guard_ip] = bandwidth[1].strip('\n')
			else:
				guard_only_ips_bandwidth[guard_ip] = bandwidth[1].strip('\n')
	if 'bandwidth-weights' in line:
		# Gets the wgg utility weight  
		wgg_index = line.find('Wgg')
		weights = line[wgg_index:]
		weight = weights.split(' ')
		weight = weight[0].split('=')
		wgg = float(weight[1])
		# Gets the wgd Utility weight 
		wgd_index = line.find('Wgd')
		weights = line[wgd_index:]
		weight = weights.split(' ')
		weight = weight[0].split('=')
		wgd = float(weight[1])
print (num_guards)
max_bandwidth = 0
num_exit_guards = 0
num_guards = 0
while guard_only_ips_bandwidth: 
	num_guards +=1
	key,value = guard_only_ips_bandwidth.popitem()
	guard_ips_weighted[key] = float(value)*float(wgg)
	if float(value)*float(wgg) > max_bandwidth:
		max_bandwidth = float(value)*float(wgg)
while guard_exit_ips_bandwidth:
	num_exit_guards +=1
	key,value = guard_exit_ips_bandwidth.popitem()
	guard_ips_weighted[key] = float(value)*float(wgd)
	if float(value)*float(wgd) > max_bandwidth:
		max_bandwidth = float(value)*float(wgd)
while guard_ips_weighted:
	key,value = guard_ips_weighted.popitem()
	file.write(key)
	file.write(": ")
	file.write(str(value/float(max_bandwidth)))
	file.write('\n')
print (num_guards)
print (num_exit_guards)
file.close()


