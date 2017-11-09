import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step


file1_bandwidth = open('guard_ips_with_bandwidth.txt', 'r')
file2_as= open('list02','r')
ases_to_ips = {}
ips_to_bandwidth= {}
ip_weighted_prob = {}
epsilon_dict = {}
alpha = .01
epsilons =[]
alphas = []
test_as =3
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
for alpha in my_range(0.00,1,.01):
	alphas.append(alpha)
	with open("cg_resilience.json") as data_file: 
		data = json.load(data_file)
		weights = {}
		for key, values in data.items():
			if float(key) == test_as:
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
	ip_probabilities = {}
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
			if float(key) == test_as:
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
	total_epsilon_per_choice =0
	total_ip_weight = 0
	for pair in ovh_data:
		ip = pair[0]
		weights = pair[1]
		for weight in weights:
			#print(graph_pairs[ip])
			# Still need the particular probability that this as picks this guard
			total_ip_weight += weight
			total_epsilon_per_choice += (ip_epsilons[ip] *weight)
	total_epsilon_per_choice = total_epsilon_per_choice/total_ip_weight
	epsilons.append(total_epsilon_per_choice)

graph_data = [go.Scatter(x=alphas,y=epsilons)]
py.plot(graph_data,filename='alphas-vs-epsilons.html')


