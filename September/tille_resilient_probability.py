import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go

ases_to_ips = {}
asIP_to_resilience = {}
ips_to_bandwidthN= {}
ips_to_bandwidth= {}
ipResilience = {}
file1_bandwidth_normalized = open('guard_ips_with_bandwidth_normalized.txt', 'r')
file1_bandwidth= open('guard_ips_with_bandwidth.txt', 'r')
file2_as= open('list02','r')

for line in file1_bandwidth:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidth[key] = float(value)
file1_bandwidth.close()

for line in file1_bandwidth_normalized:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidthN[key] = float(value)

for line in file2_as:
	info = line.split('|')
	key = info[0].strip(' ')
	value = info[1].strip('\n').strip(' ')
	if key in ases_to_ips:
		ases_to_ips[key].append(value)
	else:
		ases_to_ips[key] = [value]
file2_as.close()

g = .1 
N = 2075
alpha = 0

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step
ipResilience = dict()


with open("cg_resilience.json") as data_file: 
		data = json.load(data_file)
		weights = {}
		for key, values in data.items():
			asIP_to_resilience[key] = dict()
			while values:
				to_as, resilience = values.popitem()
				if to_as in ases_to_ips:
					to_ips_in_as = ases_to_ips[to_as]
					for ip in to_ips_in_as:
						if ip in asIP_to_resilience[key]:
							asIP_to_resilience[key][ip].append(resilience)
						else:
							asIP_to_resilience[key][ip] = [resilience]

with open("tille_resiliences.json") as data_file: 
	data = json.load(data_file)
	weights = {}
	for key, values in data.items():
		client_as_weights = {}
		ipResilience[key] = dict()
		while values:
			to_ip, resilience = values.popitem()
			ipResilience[key][to_ip] = resilience
			raptor_weight = 0
			if ips_to_bandwidthN[to_ip] != 0:
				raptor_weight = resilience*alpha + (1-alpha)*ips_to_bandwidthN[to_ip]
			else:
				raptor_weight = 0
			if to_ip in client_as_weights:
				client_as_weights[to_ip].append(raptor_weight)
				ipResilience[key][to_ip].append(reslience)
			else:
				client_as_weights[to_ip] = [raptor_weight]
				ipResilience[key][to_ip] = [resilience]
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
			total_resilience+= weight*asIP_to_resilience[key][ip][index]
			resilience += weight*asIP_to_resilience[key][ip][index]
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










