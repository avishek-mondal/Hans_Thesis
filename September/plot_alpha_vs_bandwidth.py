import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step


file1_bandwidth_normalized = open('guard_ips_with_bandwidth_normalized.txt', 'r')
file1_bandwidth= open('guard_ips_with_bandwidth.txt', 'r')
file2_as= open('list02','r')
ases_to_ips = {}
ips_to_bandwidth= {}
ips_to_bandwidthN= {}
ip_weighted_prob = {}
epsilon_dict = {}
alpha = .01
epsilons =[]
bandwidths = []
alphas = []
test_as =3
for line in file1_bandwidth_normalized:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidthN[key] = float(value)

for line in file1_bandwidth:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidth[key] = float(value)
for line in file2_as:
	info = line.split('|')
	key = info[0].strip(' ')
	value = info[1].strip('\n').strip(' ')
	if key in ases_to_ips:
		ases_to_ips[key].append(value)
	else:
		ases_to_ips[key] = [value]
for alpha in my_range(0.00,1,.1):
	print(alpha)
	alphas.append(alpha)
	with open("tille_resiliences.json") as data_file: 
		data = json.load(data_file)
		weights = {}
		for key, values in data.items():
			client_as_weights = {}
			while values:
				to_ip, resilience = values.popitem()
				raptor_weight = 0
				if ips_to_bandwidthN[to_ip] != 0:
					raptor_weight = resilience*alpha + (1-alpha)*ips_to_bandwidthN[to_ip]
				else:
					raptor_weight = 0
				if to_ip in client_as_weights:
					client_as_weights[to_ip].append(raptor_weight)
				else:
					client_as_weights[to_ip] = [raptor_weight]
			weights[key] = deepcopy(client_as_weights)
	data_file.close()
	## Gets the probability of selecting a given ip for each given as 
	weights_copy = deepcopy(weights)
	as_to_ip_probability = dict()
	while weights_copy:
		key, values = weights_copy.popitem()
		as_to_ip_probability[key] = dict()
		total_weight = 0 
		while values:
			ip, weight = values.popitem()
			for wei in weight:
				total_weight += wei
			as_to_ip_probability[key][ip] = weight 
		for ip in as_to_ip_probability[key]:
			for index,weight in enumerate(as_to_ip_probability[key][ip]):
				as_to_ip_probability[key][ip][index] = weight/total_weight
	total_ip_weight = 0
	average_bandwidth_selected = 0
	number_ases = 0
	as_to_resilience = {}
	bandwidth = 0
	as_bandwidths = dict()
	for key in as_to_ip_probability:
		number_ases+=1
		resilience = 0 
		as_bandwidths[key] = 0
		for ip in as_to_ip_probability[key]:
			num_in_list = 0 
			for index,weight in enumerate(as_to_ip_probability[key][ip]):
				as_bandwidths[key]+= weight*ips_to_bandwidth[ip]
	average_bandwidth = 0
	for key in as_bandwidths:
		average_bandwidth += as_bandwidths[key]
	average_bandwidth = average_bandwidth/number_ases
	bandwidths.append(average_bandwidth)

graph_data = [go.Scatter(x=alphas,y=bandwidths)]
py.plot(graph_data,filename='alphas-vs-banwdiths.html')


