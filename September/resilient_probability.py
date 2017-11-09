import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go



def my_range(start, end, step):
    while start <= end:
        yield start
        start += step


file1_bandwidth = open('guard_ips_with_bandwidth_normalized.txt', 'r')
file2_as= open('list02','r')
ases_to_ips = {}
ips_to_bandwidth= {}
ip_weighted_prob = {}
epsilon_dict = {}
ip_to_resilience = {}
alpha = .5
for line in file1_bandwidth:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidth[key] = float(value)
file1_bandwidth.close()
for line in file2_as:
	info = line.split('|')
	key = info[0].strip(' ')
	value = info[1].strip('\n').strip(' ')
	if key in ases_to_ips:
		ases_to_ips[key].append(value)
	else:
		ases_to_ips[key] = [value]
file2_as.close()

#Create dictionary of client weights given as 
with open("cg_resilience.json") as data_file: 
	data = json.load(data_file)
	weights = {}
	for key, values in data.items():
		client_as_weights = {}
		ip_to_resilience[key] = dict()
		while values:
			to_as, resilience = values.popitem()
			if to_as in ases_to_ips:
				to_ips_in_as = ases_to_ips[to_as]
				for to_ip in to_ips_in_as:
					raptor_weight = 0
					if ips_to_bandwidth[to_ip] != 0:
						raptor_weight = resilience*alpha + (1-alpha)*ips_to_bandwidth[to_ip]
					else:
						raptor_weight = 0
					if to_ip in client_as_weights:
						client_as_weights[to_ip].append(raptor_weight)
						ip_to_resilience[key][to_ip].append(resilience)
					else:
						client_as_weights[to_ip] = [raptor_weight]
						ip_to_resilience[key][to_ip] = [resilience]
			else:
				print("sorry we cannot find the to client asn %s ips" % to_as)
		weights[key] = deepcopy(client_as_weights)
data_file.close()

# Determine the probabilities of selecting a given ip
total_as_resilience = 0
as_to_ip_probability = {}
while weights:
	key, values = weights.popitem()
	as_to_ip_probability[key] = dict()
	total_weight = 0 
	while values:
		ip, weight = values.popitem()
		for wei in weight:
			total_weight += wei
		as_to_ip_probability[key][ip] =weight 
	for ip in as_to_ip_probability[key]:
		for index,weight in enumerate(as_to_ip_probability[key][ip]):
			as_to_ip_probability[key][ip][index] = weight/total_weight

# For each As determine what the the total resilience given
# the particular alpha
total_resilience = 0
number_ases = 0
num_below_fifty = 0 
as_to_resilience = {}
for key in as_to_ip_probability:
	number_ases+=1
	resilience = 0 
	for ip in as_to_ip_probability[key]:
		num_in_list = 0 
		for index,weight in enumerate(as_to_ip_probability[key][ip]):
			num_in_list += 1
			total_resilience+= weight*ip_to_resilience[key][ip][index]
			resilience += weight*ip_to_resilience[key][ip][index]
	as_to_resilience[key] = resilience

res = []
cdf = []
for x in my_range(0,1,.001):
	res.append(x)
	num_as = 0
	for key in as_to_resilience:
		if as_to_resilience[key] <= x:
			num_as+=1
	cdf.append(num_as/number_ases)



print (num_below_fifty)
print(number_ases)
print(total_resilience)
print(total_resilience/number_ases)

graph_data = [go.Scatter(x=res,y=cdf)]
py.plot(graph_data,filename='cdf.html')

