import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go

file1_bandwidth = open('guard_ips_with_bandwidth', 'r')
file2_as= open('list02','r')
ases_to_ips = {}
ips_to_bandwidth= {}
ip_weighted_prob = {}
epsilon_dict = {}
alpha = .5
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
with open("cg_resilience.json") as data_file: 
	data = json.load(data_file)
	weights = {}
	for key, values in data.items():
		if key == 3:
			print (key)
		client_as_weights = {}
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
					client_as_weights[to_ip] = raptor_weight
			else:
				print("sorry we cannot find the to client asn %s ips" % to_as)
		weights[key] = deepcopy(client_as_weights)
file_out = open('tor_guard_weight.json', 'w+')
json.dump(weights, file_out)
file_out.close()
ip_weights = {}
ip_probabilities = {}
ip_selection_epsilson = open('ip_selection_epsilson.txt', 'w+')
ip_epsilons = {}
ovh_data = []
with open("tor_guard_weight.json") as tor_weight_file: 
	data = json.load(tor_weight_file)
	for key, values in data.items():
		while values:
			ip, weight = values.popitem()
			if ip in ip_weights:
				ip_weights[ip].append(weight)
			else:
				ip_weights[ip] = [weight]
			if float(key) == 3:
				if len(ovh_data) > 0:
					ovh_data.append([ip,weight])
				else:
					ovh_data = [[ip,weight]]
	for ip in ip_weights:
		max_ip_weight = 0
		min_ip_weight = 1
		total_ip_weight = 0
		ip_weight_list = ip_weights[ip]
		for weight in ip_weight_list:
			total_ip_weight += weight
			if weight > max_ip_weight:
				max_ip_weight = weight
			if weight < min_ip_weight:
				min_ip_weight = weight
		if total_ip_weight != 0:
			min_ip_weight = min_ip_weight/total_ip_weight
			max_ip_weight = max_ip_weight/total_ip_weight
		num_ases = 0
		for index, weight in enumerate(ip_weights[ip]):
			if total_ip_weight != 0:
				ip_weights[ip][index] = weight/total_ip_weight
				num_ases +=1
			#print(ip_weights[ip][index])
		if min_ip_weight != 0  and max_ip_weight!= 0:
			ip_epsilon = math.log(max_ip_weight/min_ip_weight)
		elif min_ip_weight == 0 and max_ip_weight == 0:
			ip_epsilon = 0
		elif max_ip_weight != 0 and min_ip_weight == 0:
			#print(ip)
			ip_epsilon = 10000000000
		ip_epsilons[ip] = ip_epsilon
		ip_selection_epsilson.write(str(ip))
		ip_selection_epsilson.write(": ")
		ip_selection_epsilson.write(str(ip_epsilon))
		ip_selection_epsilson.write(": ")
		ip_selection_epsilson.write("\n")


file_prob_out = open('tor_guard_probabilities.json', 'w+')
json.dump(ip_weights, file_prob_out)
file_prob_out.close()
print("Graph of OVH")
total_epsilon_per_choice = 0
total_ip_weight = 0
graph_pairs = {}
for pair in ovh_data:
	ip = pair[0]
	weight = pair[1]
	if ip_epsilons[ip] *weight != 0:
		graph_pairs[ip] = (ip_epsilons[ip] *weight)
	#print(graph_pairs[ip])
	# Still need the particular probability that this as picks this guard
	total_ip_weight += weight
	total_epsilon_per_choice += (ip_epsilons[ip] *weight)
total_epsilon_per_choice = total_epsilon_per_choice/total_ip_weight
print(total_epsilon_per_choice)

## Graph of epsilon values versus Ip Addresses for Given AS
graph_ips = graph_pairs.keys()
graph_epsilons = []
graph_ips = sorted(graph_ips)
for key in graph_ips:
	graph_epsilons.append(graph_pairs[key])
print(graph_epsilons)

graph_data = [go.Bar(x=graph_ips,y=graph_epsilons)]
py.plot(graph_data,filename='basic-bar.html')
print("Hello")
