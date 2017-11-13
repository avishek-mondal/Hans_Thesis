import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go

file1_bandwidth_normalized = open('guard_ips_with_bandwidth_normalized.txt', 'r')
file1_bandwidth= open('guard_ips_with_bandwidth.txt', 'r')

file2_as= open('list02','r')
ases_to_ips = {}
ips_to_bandwidthN= {}
ips_to_bandwidth= {}
ip_weighted_prob = {}
epsilon_dict = {}
alpha = .5
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
total_as_weight = 0
zeroes =set()
with open("cg_resilience.json") as data_file: 
	data = json.load(data_file)
	weights = {}
	for key, values in data.items():
		client_as_weights = {}
		while values:
			to_as, resilience = values.popitem()
			if to_as in ases_to_ips:
				to_ips_in_as = ases_to_ips[to_as]
				for to_ip in to_ips_in_as:
					raptor_weight = 0
					if ips_to_bandwidthN[to_ip] != 0:
						raptor = (resilience*alpha)+ (1-alpha)*(ips_to_bandwidthN[to_ip])
						if (raptor > 1):
							print(raptor)
						raptor_weight = math.exp(1.3*raptor)
					else:
						raptor_weight = 1
						zeroes.add(to_ip)
					if to_ip in client_as_weights:
						client_as_weights[to_ip].append(raptor_weight)
					else:
						client_as_weights[to_ip] = [raptor_weight]
			else:
				print("sorry we cannot find the to client asn %s ips" % to_as)
		weights[key] = deepcopy(client_as_weights)
file_out = open('tor_guard_weight.json', 'w+')
json.dump(weights, file_out)
file_out.close()
ip_weights = {}
ip_selection_epsilson = open('ip_selection_epsilson.txt', 'w+')
ip_epsilons = {}
ovh_data = []
num_values = 0
num_key_values =0
while weights:
	key, values = weights.popitem()
	while values:
		num_values +=1
		ip, weight = values.popitem()
		if ip not in ip_weights:
			ip_weights[ip] = [weight[0]]
			for wei in weight[1:]:
				ip_weights[ip].append(wei)
		else:
			for wei in weight[0:]:
				ip_weights[ip].append(wei)
		if float(key) == 3:
			if len(ovh_data) > 0:
				ovh_data.append([ip,weight])
			else:
				ovh_data = [[ip,weight]]
for ip in ip_weights:
	max_ip_weight = 0
	min_ip_weight = 3
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
average_bandwidth_selected = 0
total_ip_weight = 0
graph_pairs = {}
num_weights = 0
for pair in ovh_data:
	ip = pair[0]
	weights = pair[1]
	total_weight = 0
	graph_pairs[ip] = 0 
	for weight in weights:
		total_weight += weight
		graph_pairs[ip] += ip_epsilons[ip]*weight 
		#print(graph_pairs[ip])
		# Still need the particular probability that this as picks this guard
		total_ip_weight += weight
		total_epsilon_per_choice += (ip_epsilons[ip] *weight)
		average_bandwidth_selected += (ips_to_bandwidth[ip] *weight)
	if total_weight > 0:
		graph_pairs[ip] =graph_pairs[ip]/total_weight
average_bandwidth_selected = average_bandwidth_selected/total_ip_weight
total_epsilon_per_choice = total_epsilon_per_choice/total_ip_weight
print(average_bandwidth_selected)
print(total_epsilon_per_choice)
#for ip in graph_pairs:
#	graph_pairs[ip] = graph_pairs[ip]/total_ip_weight

## Graph of epsilon values versus Ip Addresses for Given AS
graph_ips = graph_pairs.keys()
graph_epsilons = []
graph_ips = sorted(graph_ips)
for key in graph_ips:
	graph_epsilons.append(graph_pairs[key])

graph_data = [go.Bar(x=graph_ips,y=graph_epsilons)]
py.plot(graph_data,filename='basic-bar.html')
