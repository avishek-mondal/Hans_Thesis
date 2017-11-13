import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go



def my_range(start, end, step):
    while start <= end:
        yield start
        start += step

bandwidths = []
file1_bandwidth_normalized = open('guard_ips_with_bandwidth_normalized.txt', 'r')
file1_bandwidth= open('guard_ips_with_bandwidth.txt', 'r')
file2_as= open('list02','r')
ases_to_ips = {}
ips_to_bandwidthN= {}
ips_to_bandwidth = {}
ip_weighted_prob = {}
epsilon_dict = {}
ip_to_resilience = {}
asIP_to_resilience = {}
alpha = 0
epsilon = 5
test_as = 3
for line in file1_bandwidth_normalized:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidthN[key] = float(value)
file1_bandwidth_normalized.close()
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


#Create dictionary of client weights given as 
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
total_graph = []



'''
Non differentially private Alpha = 0

'''

# Determine the probabilities of selecting a given ip
total_as_resilience = 0
as_to_ip_probability = {}
weights_copy = deepcopy(weights)
while weights_copy:
	key, values = weights_copy.popitem()
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
bandwidth = 0
as_bandwidths = dict()
for key in as_to_ip_probability:
	number_ases+=1
	resilience = 0 
	as_bandwidths[key] = 0
	for ip in as_to_ip_probability[key]:
		num_in_list = 0 
		for index,weight in enumerate(as_to_ip_probability[key][ip]):
			num_in_list += 1
			total_resilience+= weight*asIP_to_resilience[key][ip][index]
			resilience += weight*asIP_to_resilience[key][ip][index]
			as_bandwidths[key]+= weight*ips_to_bandwidth[ip]
		as_to_resilience[key] = resilience
average_bandwidth = 0
for key in as_bandwidths:
	average_bandwidth += as_bandwidths[key]
average_bandwidth = average_bandwidth/number_ases
bandwidths.append(average_bandwidth)

res = []
cdf = []
for x in my_range(0,1,.001):
	res.append(x)
	num_as = 0
	for key in as_to_resilience:
		if as_to_resilience[key] <= x:
			num_as+=1
	cdf.append(num_as/number_ases)
graph_data = go.Scatter(x=res,y=cdf)
total_graph.append(graph_data)

'''
Non differentially private Alpha =.5 

'''
alpha = .5
#Create dictionary of client weights given as 
with open("tille_resiliences.json") as data_file: 
	data = json.load(data_file)
	weights = {}
	for key, values in data.items():
		client_as_weights = {}
		while values:
			to_ip, resilience = values.popitem()
			raptor_weight = 0
			if ips_to_bandwidthN[to_ip] != 0:
				raptor_weight = ((resilience*alpha)+ ((1-alpha)*ips_to_bandwidthN[to_ip]))
			else:
				raptor_weight = 0
			if to_ip in client_as_weights:
				client_as_weights[to_ip].append(raptor_weight)
			else:
				client_as_weights[to_ip] = [raptor_weight]
		weights[key] = deepcopy(client_as_weights)
data_file.close()

# Determine the probabilities of selecting a given ip
total_as_resilience = 0
as_to_ip_probability = {}
weights_copy = deepcopy(weights)
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

# For each As determine what the the total resilience given
# the particular alpha
total_resilience = 0
number_ases = 0
num_below_fifty = 0 
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
			num_in_list += 1
			total_resilience+= weight*asIP_to_resilience[key][ip][index]
			resilience += weight*asIP_to_resilience[key][ip][index]
			as_bandwidths[key]+= weight*ips_to_bandwidth[ip]
		as_to_resilience[key] = resilience
average_bandwidth = 0
for key in as_bandwidths:
	average_bandwidth += as_bandwidths[key]
average_bandwidth = average_bandwidth/number_ases
bandwidths.append(average_bandwidth)

res = []
cdf = []
for x in my_range(0,1,.001):
	res.append(x)
	num_as = 0
	for key in as_to_resilience:
		if as_to_resilience[key] <= x:
			num_as+=1
	cdf.append(num_as/number_ases)
graph_data = go.Scatter(x=res,y=cdf)
total_graph.append(graph_data)


'''
Alpha = .5  and epsilon = 1 for 2*epsilon Differential Privacy


'''

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
					if ips_to_bandwidthN[to_ip] != 0:
						raptor_weight = (((resilience*alpha)+ ((1-alpha)*ips_to_bandwidthN[to_ip])))
						#print(raptor_weight)
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

for eps in my_range(2,2,1):
	print(eps)
	# Determine the probabilities of selecting a given ip from each as
	total_as_resilience = 0
	as_to_ip_probability = {}
	weights_copy = deepcopy(weights)
	while weights_copy:
		# Get the AS (key) and respective raptor weights (values)
		key, values = weights_copy.popitem()
		as_to_ip_probability[key] = dict()
		total_weight = 0 
		while values:
			ip, weight = values.popitem()
			# Each ip may have more than one relay located at it and 
			# therefore multiple raptor weights
			for wei in weight:
				total_weight += math.exp((wei)*eps)
			as_to_ip_probability[key][ip] = [math.exp((weight[0])*eps)]
			for wei in weight[1:]:
				as_to_ip_probability[key][ip].append(math.exp((wei)*eps))
		for ip in as_to_ip_probability[key]:
			for index,weight in enumerate(as_to_ip_probability[key][ip]):
				as_to_ip_probability[key][ip][index] = weight/total_weight

	# For each As determine what the the total resilience given
	# the particular alpha
	total_resilience = 0
	number_ases = 0
	num_below_fifty = 0 
	as_to_resilience = {}
	as_bandwidths = dict()
	for key in as_to_ip_probability:
		number_ases+=1
		resilience = 0 
		as_bandwidths[key] =0
		for ip in as_to_ip_probability[key]:
			num_in_list = 0 
			for index,weight in enumerate(as_to_ip_probability[key][ip]):
				num_in_list += 1
				total_resilience+= weight*asIP_to_resilience[key][ip][index]
				resilience += weight*asIP_to_resilience[key][ip][index]
				as_bandwidths[key]+= weight*ips_to_bandwidth[ip]
		as_to_resilience[key] = resilience
	average_bandwidth = 0
	for key in as_bandwidths:
		average_bandwidth += as_bandwidths[key]
	average_bandwidth = average_bandwidth/number_ases
	bandwidths.append(average_bandwidth)
	res = []
	cdf = []
	for x in my_range(0,1,.0001):
		res.append(x)
		num_as = 0
		for key in as_to_resilience:
			if as_to_resilience[key] <= x:
				num_as+=1
		cdf.append(num_as/number_ases)
	graph_data = go.Scatter(x=res,y=cdf)
	total_graph.append(graph_data)

py.plot(total_graph,filename='cdf.html')
print(bandwidths)

alpha_string = "Alapha = " +str(alpha)
private_string0 = alpha_string + " " +str(0/2)+ "-Epsilon"
private_string1 = alpha_string + " " +str(1/2)+ "-Epsilon"
private_string2 = alpha_string + " " +str(2/2)+ "-Epsilon"
private_string3 = alpha_string + " " +str(3/2)+ "-Epsilon"
private_string4 = alpha_string + " " +str(4/2)+ "-Epsilon"

data = [go.Bar(
            x=['Alpha = 0', alpha_string,private_string0],
            y=bandwidths
    )]

py.plot(data, filename='basic-bar.html')
