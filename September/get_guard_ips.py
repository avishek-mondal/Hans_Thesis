import re
guard_examined =""
file = open('guard_ips.txt', 'w')
ip_regex = r'(?:\d{1,3}\.)+(?:\d{1,3})'
consensus = open('2017-09-14-21-00-00-consensus','r')
guard_ips_weighted = {}
#TODO: Add port to guard ips to handle ips with multiple
#guards in the ip
for line in consensus:
	if line[0] == 'r' and line[1] == ' ':
		guard_examined = line
	elif line[0] == 's' and len(guard_examined) > 0 :
		if 'Guard' in line:
			guard_ip = str(re.search(ip_regex,guard_examined).group(0)) 
			file.write(guard_ip)
			file.write('\n')
file.close()


