"""
    V. 2. 0. 0
    Analytical Hierarchy Process UG-Tourence
    by Stochastica Team (Programmer Rafi Mochamad Fahreza)
    Copyright 2020
"""

import numpy as np

def get_weight(x, n_criteria):
    weight = [round(sum(x[i]) / n_criteria, 3) for i in range(len(x))]
    return np.array(weight)

def transpose(x):
    transposed = [[x[j][i] for j in range(len(x))] for i in range(len(x[0]))]
    return np.array(transposed)

def norm(x):
    sum_col = [0] * len(x[0])
    norm_mat = []
    for row in range(len(x)):
        for col in range(len(x[0])):
            sum_col[row] = round(x[col][row] + sum_col[row], 3)
    
    for m in range(len(x)):
        norm_mat_col = []
        for n in range(len(x[0])):
            norm_mat_col.append(round(x[m][n] / sum_col[n], 3))
        norm_mat.append(norm_mat_col)
    return get_weight(norm_mat, len(x[0]))

def multiply(m1, m2):
    return np.matmul(m1, m2)

def getConsistency(all_alt, n_criteria, n_alt):
    allPCM = np.vstack(all_alt)
    all_consistency = []
    for criteria in range(n_criteria):
        lambdamax = np.amax(np.linalg.eigvals(allPCM[criteria * n_alt:criteria * n_alt + n_alt, 0:n_alt]).real)
        RI = [0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
        CI = (lambdamax - n_alt)/(n_alt - 1)
        CR = CI / RI[3]#n_alt - 1]
        all_consistency.append(CR)
        print("Inconsistency index of the alternatives for"
            " criterion ", (criteria + 1), ": ", CR)
        if CR > 0.1:
            print("The pairwise comparison matrix of the"
                "alternatives for criterion ", (criteria + 1), 
                "is inconsistent")
    return all_consistency

def stahp2(layers):
    all_consistent = []
    all_eig = []
    for i in range(len(layers)):
        if i == 0 :
            print("Layer 0")
            all_eig.append(norm(layers[0]))
            all_consistent.append(getConsistency(layers[0], 1, len(layers[0][1])))
            
        else:
            print("Layer "+str(i))
            eig_per_layer = []
            for j in layers[i]:
                eig_per_layer.append(norm(j))
            all_eig.append(transpose(eig_per_layer))
            all_consistent.append(getConsistency(layers[i], len(layers[i]), len(layers[i][0])))
            
    multipled = multiply(np.round(all_eig[2], 2), np.round(all_eig[1],2))
    return np.round(multiply(multipled, all_eig[0]), 2).tolist(), all_consistent


