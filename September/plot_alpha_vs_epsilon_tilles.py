import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go

ases_to_ips = {}
asIP_to_reslience = {}
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
alpha = .5
def check_resilince_for_tille(ip_to_resilience):
	for ip in ip_to_resilience:
		if ip_to_resilience[ip] > 1:
			return True 
	return False 

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step
alphas = []
epsilons = []
for alpha in my_range(0.00,1,.005):
	alphas.append(alpha)
	with open("tille_resiliences.json") as data_file: 
		data = json.load(data_file)
		weights = {}
		for key, values in data.items():
			client_as_weights = {}
			ipResilience[key] = dict()
			while values:
				to_ip, resilience = values.popitem()
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

	ip_weights = {}
	ip_probabilities = {}
	ip_epsilons = {}
	ovh_data = []
	num_values = 0
	num_key_values =0
	as_data = dict()
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
			if key in as_data:
				as_data[key].append([ip,weight])
			else:
				as_data[key] = [[ip,weight]]
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
	print("Graph of OVH")
	total_epsilon_per_choice = 0
	total_ip_weight = 0
	graph_pairs = {}
	num_weights = 0
	max_epsilon = 0
	max_epsilon_per_choice = 0
	min_epsilon = 10
	num_ases = 0
	average_epsilson = 0
	max_epsilon_As = 0
	max_epsilon_IP = ""
	for key in as_data:
		num_ases += 1 
		total_ip_weight = 0 
		total_epsilon_per_choice = 0
		for pair in as_data[key]:
			ip = pair[0]
			weights = pair[1]
			for weight in weights:
				if ip_epsilons[ip] *weight != 0:
					graph_pairs[ip] = ip_epsilons[ip]
					if ip_epsilons[ip] > max_epsilon_per_choice:
						max_epsilon_per_choice = ip_epsilons[ip]
						max_epsilon_As = key
						max_epsilon_IP = ip

					#print(graph_pairs[ip])
					# Still need the particular probability that this as picks this guard
					total_ip_weight += weight
					total_epsilon_per_choice += (ip_epsilons[ip] *weight)
		if total_ip_weight != 0:
			total_epsilon_per_choice = total_epsilon_per_choice/total_ip_weight
		if total_epsilon_per_choice > max_epsilon:
			max_epsilon = total_epsilon_per_choice
		if total_epsilon_per_choice < min_epsilon:
			min_epsilon = total_epsilon_per_choice
		average_epsilson += total_epsilon_per_choice
	average_epsilson = average_epsilson/num_ases
	print("Epsilons")
	print(max_epsilon_IP)
	print(max_epsilon_As)
	print (max_epsilon_per_choice)
	print(min_epsilon)
	epsilons.append(max_epsilon_per_choice)

graph_data = [go.Scatter(x=alphas,y=epsilons)]
py.plot(graph_data,filename='alphas-vs-epsilons.html')
