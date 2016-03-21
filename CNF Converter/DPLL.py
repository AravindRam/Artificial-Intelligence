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

def make_clauses(sentence):
	""" Function to form clauses from the given input and return a list of all clauses"""
	clauses=[]
	for i in range(1,len(sentence)):
		if(sentence[0] == NOT):	# for negative clauses or symbols
			clauses.append([NOT,sentence[i]])
		else:					# for positive clauses or symbols
			clauses.append(sentence[i])
	return clauses

def extract_symbols(clauses):
	"""Function to extract only the symbols from each clause in a given input and
	   return a list of symbols for each input"""
	symbols=[]
	symbols_without_not=[]
	symbols_with_not=[]
	for i in range(len(clauses)):
		if is_positive_symbol(clauses[i]) and clauses[i] not in symbols:	# add symbol to list if symbol is positive and not already in list
			symbols.extend(clauses[i])
			symbols_without_not.extend(clauses[i])
		elif is_negative_symbol(clauses[i]) and clauses[i][1] not in symbols_with_not:	
			if clauses[i][1] not in symbols:				# add symbol to list if symbol is negative and not already in list
				symbols.extend(clauses[i][1]) 
			symbols_with_not.append(clauses[i][1])
		elif isinstance(clauses[i],list):		# if clause is a list, iterate through list and add the positive or negative symbols to list
			for j in range(1,len(clauses[i])):
				if is_positive_symbol(clauses[i][j]) and clauses[i][j] not in symbols:
					symbols.extend(clauses[i][j])
					symbols_without_not.extend(clauses[i][j])
				elif is_negative_symbol(clauses[i][j]) and clauses[i][j][1] not in symbols_with_not and clauses[i][j][1] not in symbols:
					if is_symbol(clauses[i][j][1]):
						symbols.extend(clauses[i][j][1])
						symbols_with_not.append(clauses[i][j][1])
					elif isinstance(clauses[i][j][1],list):
						symbols.extend(clauses[i][j][1])
						symbols_with_not.append(clauses[i][j][1])
					
	symbols_list=[]
	symbols_list.append(symbols_without_not)
	symbols_list.append(symbols_with_not)
	return symbols,symbols_list

def find_pure_symbols(symbols,clauses,model):
	model=[]
	if len(symbols[0]) == 0 and len(symbols[1]) !=0:
		model.extend(["true"])
		for i in range(len(symbols[1])):
			model.extend([""+symbols[1][i]+"=false"])
	
	elif len(symbols[0]) != 0 and len(symbols[1]) ==0:
		model.extend(["true"])
		for i in range(len(symbols[0])):
			model.extend([""+symbols[0][i]+"=true"])
	
	elif len(symbols[0]) != 0 and len(symbols[1]) !=0:
		model.extend(["true"])
		for i in range(len(symbols[0])):
			if symbols[0][i] not in symbols[1]:
				model.extend([""+symbols[0][i]+"=true"])
			else:
				model=["false"]
		for i in range(len(symbols[1])):
			if symbols[1][i] not in symbols[0]:
				model.extend([""+symbols[1][i]+"=false"])	
			else:
				model=["false"]
	else:
		model.extend(["false"])
	return model

def find_pure_symbol(symbols, clauses, model):
	"""Function to find if a symbol is a pure symbol and its value if it is present only a positive symbol
    or only as a negative symbol in all the clauses in a given input."""
	print symbols,clauses
	for i in range(len(symbols)):
		found_pos, found_neg = False, False
		for j in range(len(clauses)):
			if not found_pos and symbols[i] in clauses[j]:
				found_pos = True
			if not found_neg and str([NOT , symbols[i]]) in clauses[j]:
				found_neg = True
		if found_pos != found_neg: return symbols[i], found_pos
	return None, None

def find_unit_clause(clauses, model):
	""" Function to find a unit clause and its value if it is present only as a symbol and not in a list"""
	print clauses
	for i in range(len(clauses)):
		count = 0
		literals,literal_list = extract_symbols(clauses[i])
		for j in range(len(literal_list[0])):
			if literal_list[0][j] not in model:
				count += 1
				P, value = literal_list[0][j], "'true'"
		for j in range(len(literal_list[1])):
			if literal_list[1][j] not in model:
				count += 1
				P, value = literal_list[1][j], "'false'"
		if count == 1:
			return P, value
	return None, None

def pl_true(clause, model={}):
	""" Function to find if every clause in a given input is True or False """
	if clause == "TRUE":
		return True
	elif clause == "FALSE":
		return False
	elif clause[0] == NOT:
		value = pl_true(clause[1], model)
		if value is None:
			return None
		else:
			return not value
	elif clause[0] == OR:
		result = False
		for i in range(1,len(clause)):
			value = pl_true(clause[i], model)
			if value is True:
				return True
			if value is None:
				result = None
		return result
	elif clause[0] == AND:
		result = True
		for i in range(1,len(clause)):
			value = pl_true(clause[i], model)
			if value is False:
				return False
			if value is None:
				result = None
		return result
	else:
		return model.get(clause)
	
def DPLL(clauses, symbols, model):
	""" Function to find if a given input is satisfiable or not """
	unknown_clauses = []
	for i in range(len(clauses)):
		val =  pl_true(clauses[i], model)
		if val == False:
			return False
		if val != True:
			unknown_clauses.append(clauses[i])
	if not unknown_clauses:
		return model
	P, value = find_pure_symbol(symbols,unknown_clauses,model)
	if P:
		return DPLL(clauses, symbols.remove(P),model.extend([""+P+"="+str(value)]))
	P, value = find_unit_clause(clauses, model)
	if P:
		return DPLL(clauses, symbols.remove(P),model.extend([""+P+"="+str(value)]))
	P = symbols[0]
	rest = symbols[1:]
	return (DPLL(clauses, rest, model.extend([""+P+"=true"])) or DPLL(clauses, rest, model.extend([""+P+"=false"])))

""" Main Function to get the inputs from the file,parse it,retrieve symbols and clauses
	and call the DPLL algorithm to find the satisfiability of the CNF sentence """
if(argv[1] == "-i"):
	fr=open(argv[2],"r")

fw=open("CNF_satisfiability.txt","w")

line=fr.readlines()
length = int(line[0])
i=1
while i<=length:
	mylist=eval(line[i])
	clauses = make_clauses(mylist)
	symbols,symbols_list = extract_symbols(clauses)
	model=[]
	result = DPLL(clauses,symbols,model)
	output_tuple=[]
	if result == True:
		output_tuple=["true"]
	elif result == False:
		output_tuple=["false"]
	output_tuple.extend(model)
	print output_tuple
	fw.write(str(output_tuple))	
	fw.write("\n")
	i=i+1
fw.close()
fr.close()
