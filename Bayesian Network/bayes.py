import sys
import itertools
import copy
from sys import argv

def compute_probability(j,test_result):
	prior = float(prior_prob[j])
	trueDisease = prior
	falseDisease = 1-prior
	num_sym=int(m[j])
	
	for l in range(num_sym):
		if test_result[l] == 'T':
			trueDisease = trueDisease*float(true_prob_list[j][l])
			falseDisease = falseDisease*float(false_prob_list[j][l])
		elif test_result[l] == 'F':
			trueDisease = trueDisease*(1-float(true_prob_list[j][l]))
			falseDisease = falseDisease*(1-float(false_prob_list[j][l]))
		
	return format(trueDisease / (trueDisease + falseDisease),'.4f')
	
def compute_minmax_probability(i,j):
	num_sym=int(m[j])
	Ucount = 0
	test_data = copy.deepcopy(patient_data[i][j])
	prob_list=[]
	
	for l in range(num_sym):
		if patient_data[i][j][l] == 'U':
			Ucount = Ucount + 1
			
	assignBool = ["".join(seq) for seq in itertools.product("FT", repeat=Ucount)]
	
	for index1 in range(len(assignBool)):
		index2=0
		for l in range(num_sym):
			if patient_data[i][j][l] == 'U':
				test_data[l] = assignBool[index1][index2]
				index2 = index2 + 1
		
		probability = compute_probability(j,test_data)
		prob_list.append(probability)
		
	return min(prob_list),max(prob_list)
	
def compute_best_probability(i,j):
	num_sym=int(m[j])
	list1=[]
	prob_list=[]
	result_list=[]
	boolValues = ['T','F']
	Ucount = 0
	
	actual_prob = compute_probability(j,patient_data[i][j])
	for l in range(num_sym):
		if patient_data[i][j][l] == 'U':
			Ucount = Ucount + 1
			
	if Ucount == 0:
		return ['none','N','none','N']
	
	for l in range(num_sym):
		test_data = copy.deepcopy(patient_data[i][j])
		if patient_data[i][j][l] == 'U':
			for index in range(2):
				test_data[l] = boolValues[index]
				probability = compute_probability(j,test_data)
				temp = []
				temp.append(symptoms_list[j][l])
				temp.append(boolValues[index])
				list1.append(temp)
				prob_list.append(probability)
				
	maxValue = max(prob_list)
	indices1 = [i for i, x in enumerate(prob_list) if x == maxValue]
	max_index = indices1[0]
	for i in range(1, len(indices1)):
		if list1[indices1[i]][0] < list1[max_index][0]:
			max_index = indices1[i]
	
	#maxIndex = prob_list.index(maxValue)
	minValue = min(prob_list)
	indices2 = [i for i, x in enumerate(prob_list) if x == minValue]
	min_index = indices2[0]
	for i in range(1, len(indices2)):
		if list1[indices2[i]][0] < list1[min_index][0]:
			min_index = indices2[i]
	
	#minIndex = prob_list.index(minValue)
	if(actual_prob == prob_list[max_index]):
		result_list.extend(['none','N'])
	else:
		result_list.extend(list1[max_index])
	
	if(actual_prob == prob_list[min_index]):
		result_list.extend(['none','N'])
	else:
		result_list.extend(list1[min_index])
	
	return result_list
	
filename = argv[2]
if(argv[1] == "-i"):
	fr=open(filename,"r")
output_filename = filename[:filename.find('.')] + "_inference" + filename[filename.find('.'):]
fw=open(output_filename,"w")

line=fr.readlines()
input=line[0].split()
n=int(input[0])
k=int(input[1])
disease_name=[]
m=[]
prior_prob=[]
symptoms_list=[]
true_prob_list=[]
false_prob_list=[]

for i in range(n):
	for j in range(1,5):
		no=4*i+j
		if j==1:
			input=line[no].split()
			disease_name.append(input[0])
			m.append(input[1])
			prior_prob.append(input[2])
		elif j==2:
			symptoms_list.append(eval(line[no]))
		elif j==3:
			true_prob_list.append(eval(line[no]))
		elif j==4:
			false_prob_list.append(eval(line[no]))


patient_data=[]
remaining=line[4*n+1:]
for i in range(k):
	test=[]
	for j in range(n):
		test.append(eval(remaining[n*i+j]))
	patient_data.append(test)
	
"""for i in range(k):
	fw.write(str(patient_data[i]))	
	fw.write("\n")"""

#output_order = [1,3,2,0,4]
result=""	
for i in range(k):
	result+="Patient-"+str(i+1)+":"+"\n{"
	for j in range(n):
		prob = compute_probability(j,patient_data[i][j])
		result+="'"+disease_name[j]+"': '"+str(prob)+"'"
		if j!=n-1:
			result+=", "
	result+="}\n{"
	for j in range(n):
		minProb , maxProb = compute_minmax_probability(i,j)
		result+="'"+disease_name[j]+"': "+"['"+str(minProb)+"' , '"+str(maxProb)+"']"
		if j!=n-1:
			result+=", "
	result+="}\n{"
	for j in range(n):
		best = compute_best_probability(i,j)
		result+="'"+disease_name[j]+"': "+str(best)
		if j!=n-1:
			result+=", "
	result+="}\n"
	

print result
fw.write(result)

"""print "No of diseases : ",n
print "No of patients : ",k
print "Disease Names : ", disease_name
print "No of symptoms : ", m
print "Prior Probabilities : ", prior_prob
print "List of symptoms : ", symptoms_list
print "List of True Probabilities : ",true_prob_list
print "List of False Probabilities : ",false_prob_list"""


fw.close()
fr.close()
