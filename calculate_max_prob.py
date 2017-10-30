import json
import math
file = open('as_epsilon_values.txt', 'w')
with open("cg_resilience.json") as data_file: 
	data = json.load(data_file)
	as_remax_dict = {}
	as_remin_dict = {}
	epsilon_values = {}
	as_one_zeros = []
	as_two_zeros =[]
	for values in data.values():
		if isinstance(values, dict):
			while values:
				key, value = values.popitem()
				if key in as_remax_dict:
					if as_remax_dict[key] < value:
						as_remax_dict[key] = value 
				else: 
					as_remax_dict[key] = value 
				if key in as_remin_dict:
					if as_remin_dict[key] > value:
						as_remin_dict[key] = value 
				else: 
					as_remin_dict[key] = value 
	for key in as_remax_dict:
		if as_remax_dict[key] != 0 and as_remin_dict[key] != 0:
			epsilon =  math.log(float(as_remax_dict[key])/(float(as_remin_dict[key])))
			epsilon_values[key] = epsilon
			file.write(key)
			file.write(": ")
			file.write(str(epsilon))
			file.write("\n")
		elif as_remax_dict[key] == 0 and as_remin_dict[key] == 0:
			as_two_zeros.append(key)
		else:
			as_one_zeros.append(key)

	print (epsilon_values)
	print(len(as_two_zeros))
	print(len(as_one_zeros))
	print (len(epsilon_values))
