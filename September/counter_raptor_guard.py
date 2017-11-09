#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##################################################
# counter_raptor_guard.py
# compute resilience probability
# Input:
# List of Tor client ASes (--client_file, default="../data/top400client.txt")
# Tor guard relay bandwidth (--guard_file, default="../data/guard_as_bw.json")
# Tor client to guard resiliences (--resil_file, default="../data/cg_resilience.json")
# Output:
# Resilience probabilities for each client AS of each alpha value (al[alpha]_cl[clientAS].txt)
##################################################


import sys
import json
import math
import argparse


def helper_calc(lst,k):
    s = sum(lst)
    for i in range(0,len(lst)):
        lst[i] = (lst[i]*k)/s
    return lst

def recalcprob(lst,k):
    tmplst = helper_calc(lst,k)
    finallst = [0] * len(tmplst)
    counter = 0
    while max(tmplst) > 1:
        for i in range(0,len(tmplst)):
            if tmplst[i] > 1:
                finallst[i] = 1
                tmplst[i] = 0
                counter += 1
        if max(tmplst) > 0:
            tmplst = helper_calc(tmplst,k-counter)
        else:
            break
    for i in range(0,len(tmplst)):
        if tmplst[i] != 0:
            finallst[i] = tmplst[i]
    return [i/k for i in finallst]

def calc_origin(args):
    guard_as_bw = json.load(open(args.guard_file,'r'))
    asn_lst = []
    bw_lst = []

    for asn in guard_as_bw:
        asn_lst.append(asn)
        bw_lst.append(guard_as_bw[asn])

    #normalize bandwidth
    s = sum([int(i) for i in bw_lst])
    bw_lst = [float(i)/s for i in bw_lst]

    client_dict = json.load(open(args.resil_file,'r'))
    alphalst = [1,0.75,0.5,0.25,0]
    sample_size = max(int(math.floor(len(guard_as_bw)*args.sample_size)),1)

    for alpha in alphalst:
        glst = []
        for cl in client_dict:
            plst = []
            curdict = client_dict[cl]
            if sum(curdict.values()) == 0:
                continue
            d_keys = list(curdict.keys())
            d_vals = recalcprob(list(curdict.values()),sample_size)
            lst_w = []
            for i in range(0,len(asn_lst)):
                a = asn_lst[i]
                r = d_vals[d_keys.index(a)]
                b = bw_lst[i]
                weight = alpha * r + (1 - alpha) * float(b)
                lst_w.append(weight)
            total_w = sum(lst_w)
            norm_w = [i/total_w for i in lst_w]
            for i in range(0,len(norm_w)):
                a = asn_lst[i]
                pr = norm_w[i] * float(curdict[a])
                plst.append(pr)
            gval = sum(plst)
            glst.append(gval)
        #print alpha
        with open('../results/origin/%f.txt' % alpha,'w+') as fout:
            for g in glst:
                fout.write(str(g) + '\n')

def calc_mobile(args):
    guard_as_bw = json.load(open(args.guard_file,'r'))
    asn_lst = []
    bw_lst = []
    
    for asn in guard_as_bw:
        asn_lst.append(asn)
        bw_lst.append(guard_as_bw[asn])

    #normalize bandwidth
    s = sum([int(i) for i in bw_lst])
    bw_lst = [float(i)/s for i in bw_lst]

    client_dict = json.load(open(args.resil_file,'r'))
    alphalst = [1,0.75,0.5,0.25,0]
    sample_size = max(int(math.floor(len(guard_as_bw)*args.sample_size)),1)
    topclient = [line.strip() for line in open(args.client_file, 'r')][:args.num_top]

    #perform randomization
    for cl in client_dict:
        d_keys = list(client_dict[cl].keys())
        if sum(client_dict[cl].values()) == 0:
            d_vals = [0] * len(d_keys)
        else:
            d_vals = recalcprob(list(client_dict[cl].values()),sample_size)
        for k, v in zip(d_keys, d_vals):
            client_dict[cl][k] = (client_dict[cl][k], v)

    for alpha in alphalst:
        for clientas in topclient:
            glst = []
            lst_w = []
            for i in range(0,len(asn_lst)):
                a = asn_lst[i]
                r = client_dict[clientas][a][1] # new value
                b = bw_lst[i]
                weight = alpha * r + (1 - alpha) * float(b)
                lst_w.append(weight)
            total_w = sum(lst_w)
            norm_w = [i/total_w for i in lst_w]

            # now, for this client, we have norm_w with probability for each AS
            remain_client = list(client_dict.keys())
            remain_client.remove(clientas)
            for rc in remain_client:
                plst = []
                for i in range(0,len(norm_w)):
                    pr_guard = norm_w[i]
                    a = asn_lst[i]
                    pr = norm_w[i] * float(client_dict[rc][a][0])
                    plst.append(pr)
                gval = sum(plst)
                glst.append(gval)
            with open('../results/mobile/al%s_cl%s.txt' % (str(alpha),clientas), 'w+') as fout:
                for g in glst:
                    fout.write(str(g) + '\n')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--guard_file",
                        default="../data/guard_as_bw.json")
    parser.add_argument("--resil_file",
                        default="../data/cg_resilience.json")
    parser.add_argument("--client_file",
                        default="../data/top400client.txt")
    parser.add_argument("--sample_size", type=float, default=0.1)
    parser.add_argument("--num_top", type=int, default=10)
    parser.add_argument("--mobile", action="store_true")
    return parser.parse_args()

def main(args):
    if args.mobile:
        calc_mobile(args)
    else:
        calc_origin(args)


if __name__ == '__main__':
    main(parse_args())

