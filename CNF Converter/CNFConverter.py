"""Importing argv to get the filename of the input"""
import sys
from sys import argv

"""Assigning the possible connectives to variables which can be
   further used to implement each module"""
IFF = "iff"
IMPLIES = "implies"
AND = "and"
OR = "or"
NOT = "not"

def is_positive_symbol(s):
	""" Function to find if s is a positive symbol by checking if its not a list and
		length of the string s is equal to 1 """
	return (not isinstance(s, list)) and len(s) == 1

def is_negative_symbol(s):
	""" Function to find if s is a negative symbol by checking if its a list,
		length of the list s is equal to 2, first element in the list is not and 
		the length of second element in the list is equal to 1"""
	return isinstance(s, list) and len(s) == 2 and s[0] == NOT and len(s[1]) == 1

def is_symbol(s):
	""" Function to find if s is a symbol by checking if its either a positive or a negative symbol """
	return is_positive_symbol(s) or is_negative_symbol(s)

def special_case(input):
	"""	Function to handle special cases like ["and","A","A"] , ["or",["not","A"],["not","A"]] """
	if input[0] in [AND,OR] and is_symbol(input[1]) and is_symbol(input[2]) and input[1] == input[2]:
		return True
	else:
		return False

def recursive_call(input,flag):
	""" Helper function to simplify recursion calls which adds the outputing clauses or symbols to the output list """
	output = [] ;
	output.append(input[0]);
	for i in range(1,len(input)):
		if flag == 1:
			output.append(eliminate_biconditional(input[i]))
		elif flag == 2:
			output.append(eliminate_implication(input[i]))
		elif flag == 3:
			output.append(inner_demorgan(input[i]))
		elif flag == 4:
			output.append(outer_demorgan(input[i]))
		elif flag == 5:
			output.append(eliminate_double_negation(input[i]))
	return output

def eliminate_biconditional(input):
	""" Function to eliminate biconditionals and to replace them with their implication equivalents """
	if is_symbol(input):	# check if its a symbol then return as it is
		return input
	if input[0] in [AND, OR, NOT, IMPLIES]:		# append the clauses to the output if the connective is not a biconditional
		return recursive_call(input,1)
	if input[0]==IFF:		# input - ["iff","A","B"] then convert it to ["and", ["implies","A","B"], ["implies","B","A"]]
		input[0] = AND
		input[1] = [IMPLIES, eliminate_biconditional(input[1]), eliminate_biconditional(input[2])]
		input[2] = [IMPLIES, eliminate_biconditional(input[2]), eliminate_biconditional(input[1])]
		return input

def eliminate_implication(input):
	""" Function to eliminate implications and to replace them with their not and or equivalents """
	if is_symbol(input):	# check if its a symbol then return as it is
		return input
	if input[0] in [AND, OR, NOT, IFF]:		# append the clauses to the output if the connective is not an implication
		return recursive_call(input,2)
	if input[0] == IMPLIES:		# input - ["implies","A","B"] then convert it to ["or", ["not","A"],"B"] 
		input[0] = OR
		input[1] = eliminate_implication([NOT,input[1]])
		input[2] = eliminate_implication(input[2])
		return input

def inner_demorgan(input):
	""" Function to move not inwards in the inner clauses """
	for i in range(len(input)):		
		if is_symbol(input):		# check if its a symbol then return as it is
			return input
		elif input[i][0] in [AND,OR]:		# append the clauses to the output if the connective is AND or OR
			return recursive_call(input,3)
		elif input[i][0] == NOT  and input[i][1][0] in [AND,OR]:	
				output = []						# input - ["and" ,["not",["or","A","B"]],"A" ] then convert it to ["and", ["and",["not","A"],["not","B"]],"A" 
				if(input[i][1][0] == AND):	
					output.append(OR)
				elif(input[i][1][0] == OR):
					output.append(AND)
				for j in range(1,len(input[i][1])):
					output.append(inner_demorgan([NOT,input[i][1][j]]))
				return output
		else:
			return input

def outer_demorgan(input):
	""" Function to move not inwards in the outermost clause """
	if is_symbol(input):	# check if its a symbol then return as it is
		return input
	elif input[0] in [AND,OR]:		# append the clauses to the output if the connective is AND or OR
		return recursive_call(input,4)
	elif input[0] == NOT  and input[1][0] in [AND,OR]:
			output = []				# input - ["not",["or","A","B"]] then convert it to ["and", ["not","A"],["not","B"]] 
			if(input[1][0] == AND):
				output.append(OR)
			elif(input[1][0] == OR):
				output.append(AND)
			for i in range(1,len(input[1])):
				output.append(outer_demorgan([NOT,input[1][i]]))
			return output
	else:
		return input

def eliminate_double_negation(input):
	""" Function to remove negation """
	if is_symbol(input):	# check if its a symbol then return as it is
		return input
	if input[0] in [AND,OR,IMPLIES,IFF] or (input[0]==NOT and not(input[1][0]==NOT)) :
		return recursive_call(input,5)		# append the clauses to the output if the connective is not NOT or 2 consecutive NOTs are not present
	if input[0]==NOT  :
		if input[1][0]==NOT:	# input - ["not",["not","A"]] then convert it to 'A' 
			input = input[1]
			input = input[1]
			return eliminate_double_negation(input)
			
def distributivity(clause1,clause2): 
	""" Function to distribute OR over AND """
	if isinstance(clause1, list) and clause1[0] == AND:
		output = [AND, distributivity(clause1[1],clause2), distributivity(clause1[2],clause2)]
	elif  isinstance(clause2, list) and clause2[0] == AND:
		output = [AND, distributivity(clause1,clause2[1]), distributivity(clause1,clause2[2])]
	else :
		output = [OR, clause1, clause2]
	return output

def associativity(input):
	""" Function to associate OR and OR, AND and AND """
	if is_symbol(input):			# check if its a symbol then return as it is
		return input
	elif input[0] in [AND,OR]:
		temp1=[]
		temp2=[]
		for index in range(1,len(input)):
			if input[0] == input[index][0]:
				temp1.extend(input[index][1:])
				temp2.append(input[index])
		for element in temp2:
			input.remove(element)
		input.extend(temp1)
		return input
	else:
		return input

def inner_associativity(input):
	""" Function to associate OR and OR, AND and AND for the inner clauses"""
	for i in range(len(input)):
		if(len(input[i])>1) and (input[i] not in [AND,OR,NOT,IMPLIES,IFF]):
			associativity(input[i])
			for j in range(len(input[i])):
				if input[i][0]!=NOT and input[i][0]==input[i][j][0]:
					temp=[]
					for index in range(len(input[i][j])):
						if index>0:
							temp.append(input[i][j][index])
					input[i].pop(j)
					for index in range(len(temp)):
						input[i].insert(j,temp[index])
						
def outer_associativity(input):
	""" Function to associate OR and OR, AND and AND for the outer clauses"""
	for j in range(len(input)):
		if input[0]!=NOT and input[0]==input[j][0]:
			temp=[]
			for index in range(len(input[j])):
				if index>0:
					temp.append(input[j][index])
			if isinstance(input,list):
				input.pop(j)
			for index in range(len(temp)):
				input.insert(j,temp[index])
				
def duplicate_check(element):
	""" Function to check for duplication """
	if isinstance(element, str):
		return hash(element)
	temp = []
	count = 0
	for index in element:
		if not isinstance(i, list):
			temp.append(duplicate_check(index))
		else:
			temp.append(duplicate_check(index))
	temp = sorted(temp)
	for value in temp:
		count = count + value
	return count

def remove_duplication(input):
	""" Function to remove duplication """
	if isinstance(input, str):
		return input
	temp1 = []
	temp2 = []
	for index in range(len(input)):
		element = remove_duplication(input[index])
		count = duplicate_check(element)
		if count not in temp1:
			temp1.append(count)
			temp2.append(element)
	return temp2
		
""" Main Function to get the inputs from the file,parse it and convert to CNF format
	by calling the corresponding methods to eliminate biconditional,implication,negation and also remove 
	duplicate clauses from the output after applying distributivity and associativity techniques"""
				
if(argv[1] == "-i"):
	fr=open(argv[2],"r")

fw=open("sentences_CNF.txt","w")

line=fr.readlines()
length = int(line[0])
i=1
while i<=length:
	mylist=eval(line[i])
	value = special_case(mylist)
	if value == True:
		print "'"+str(mylist[1])+"'"
		fw.write("'"+str(mylist[1])+"'")
		fw.write("\n")
	else:
		mylist = eliminate_biconditional(mylist)
		mylist = eliminate_implication(mylist)
		mylist = inner_demorgan(mylist)
		mylist = outer_demorgan(mylist)
		mylist = eliminate_double_negation(mylist)
		if mylist[0] == OR:
			mylist = distributivity(mylist[1],mylist[2])
		inner_associativity(mylist)	
		outer_associativity(mylist)
		associativity(mylist)
		#mylist = remove_duplication(mylist)
		print mylist
		fw.write(str(mylist))	
		fw.write("\n")
	i=i+1
fw.close()
fr.close()
