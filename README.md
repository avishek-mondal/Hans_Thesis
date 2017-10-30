# Thesis
Contains code for 2017- 2018 ELE Thesis 

To Begin:
1. Download Updated Tor Consensus 
2. Download Updated Network Topology 
3. Extract Guard Ips and Bandwidths using getguard.py
4. Use 
```
 netcat whois.cymru.com 43 < guard_ips.txt | sort -n > list02
 ```
 with a the list of ips that starts with begin, noasname, and ends with end

5. Extract Ases of guard relays using getas.py with list 
6. Run 
```
python counter_raptor_resilience.py
```
7. Run 
```
python calculate_prob.py
```


