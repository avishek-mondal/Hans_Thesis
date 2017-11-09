file = open('current_ases.txt', 'w')
f = open('list02','r')
ases = []
for line in f:
	info = line.split('|')
	ases.append(info[0])
setOfAses = set(ases)
for item in setOfAses:
	file.write(item) 
	file.write('\n')
file.close()
