import re

lines = []
script_file = ''	#variabile globale

def count_functions_usage(filename):
	fnc = []	#contiene l'elenco delle funzioni
	fnc_counter = []	#conta le occorrenze delle funzioni trovate
	is_cpp_comment = 0

	p = re.compile('\\bfunction\\b')
	double_slash = re.compile('\\b//\\b')
	cpp_comment_a = re.compile('\\b/[*]\\b')
	cpp_comment_b = re.compile('\\b[*]/\\b')
	f = open(filename, 'r')

	global script_file
	global lines
	script_file = f.readlines()	#memorizzo tutte le righe nell'array, una riga per elemento
	f.close()
	
	#elimino tutte le righe commentate e memorizzo quelle valide in lines
	for line in script_file:
		curr_line = line.strip()
		m_slash = double_slash.search(curr_line)
		m_cpp_a = cpp_comment_a.search(curr_line)
		m_cpp_b = cpp_comment_b.search(curr_line)
		if m_cpp_a:
			is_cpp_comment = 1
			tmp_str = curr_line[0:m_cpp_a.start()]
			if len(tmp_str) > 0:
				lines.append(tmp_str)
		if m_cpp_b:
			is_cpp_comment = 0
			tmp_str = curr_line[m_cpp_b.end():]
			if len(tmp_str) > 0:
				lines.append(tmp_str)
		if is_cpp_comment == 0:
			if m_slash:
				#ho trovato un commento che inizia con il doppio slash, salvo la riga che lo contiene escludendo tutto quello che lo segue
				tmp_str = curr_line[0:m_slash.start()]
				if len(tmp_str) > 0:
					lines.append(tmp_str)
			if m_cpp_a == None and m_cpp_b == None and m_slash == None:
				lines.append(curr_line)

	#identifico le funzioni nello script e salvo i loro nomi in fnc
	#da capire se le funzioni sono commentate o no!
	for line in lines:
		curr_line = line.strip()
		m = p.search(curr_line)
		if m:
			if curr_line[m.end()] != '(' and curr_line[m.end()] != '\n':
				tmp_string = ''
				k = m.end()
				while curr_line[k] == ' ' or curr_line[k] == '\t':
					k = k + 1
				while curr_line[k] != '(' and curr_line[k] != ' ':
					tmp_string = tmp_string + curr_line[k]
					k = k + 1
				if len(tmp_string) > 0:
					fnc.append(tmp_string)

	#cerco le varie funzioni fun in tutto il file e mi aspetto di trovare almeno 2 occorrenze (la firma della funzione e almeno una sua chiamata)
	for fun in fnc:
		fun_counter = 0
		p = re.compile('\\b'+fun+'\\b')
		for line in lines:
			m = p.search(line)
			if m:
				#print 'OK ', fun
				fun_counter +=1
		fnc_counter.append(fun_counter)
		if fun_counter < 2:
			print 'KO - Occorrenze per', fun, ':', fun_counter
		#else:
			#print 'OK - Occorrenze per', fun, ':', fun_counter
			
def count_variables_usage():
	global_vars = []
	local_vars = []
	p = re.compile('\\bfunction\\b')
	vr = re.compile('\\bvar\\b')
	block_start = re.compile('{')
	block_end = re.compile('}')
	is_function = 0		#true o false
	tmp_local_vars = []
	tmp_function_list = []
	gvar_counter = []
	lvar_counter = []
	function_list = []	#lista di liste che contengono le righe delle funzioni che hanno almeno 1 variabile locale
	local_var_cnt = 0
	parenthesis_stack = []

	#cerco le variabili dichiarate
	for line in lines:
		curr_line = line.strip()
		m_var = vr.search(curr_line)
		m_function = p.search(curr_line)
		m_blockstart = block_start.search(curr_line)
		m_blockend = block_end.search(curr_line)
		if is_function == 1:
			tmp_function_list.append(curr_line)
		if m_blockstart:
			parenthesis_stack.append('{')
		if m_function:
			#da qui trovero' variabili locali
			is_function = 1
			local_var_cnt = 0
			del tmp_local_vars[:]	#pulisco la lista
			del tmp_function_list[:]
			tmp_function_list.append(curr_line)
		if m_blockend:
			parenthesis_stack.pop()
			if(len(parenthesis_stack) == 0):
				#fine variaibli locali per una certa funzione, copio quelle che ho trovato in un elemento della lista (avro' una lista di liste)
				is_function = 0
				local_vars.append(list(tmp_local_vars))	#aggiungo alla lista la lista delle variabili locali di una funzione
				if local_var_cnt > 0:
					function_list.append(list(tmp_function_list))
		if m_var:
			#trovata una variabile, piu' avanti vedo se salvarla come variabile globale o locale (cioe' di una funzione)
			if curr_line[m_var.end()] != ';' and curr_line[m_var.end()] != '\n':
				tmp_string = ''
				k = m_var.end()
				while curr_line[k] == ' ' or curr_line[k] == '\t':
					k = k + 1
				while curr_line[k] != ';' and curr_line[k] != ' ' and curr_line[k] != '=':
					if curr_line[k] == ',':
						#ho due variabili dichiarate insieme, separate da virgola
						if len(tmp_string) > 0:
							if is_function == 0:
								#ho trovato una variabile globale
								global_vars.append(tmp_string)
							else:
								#variabile locale di una funzione
								tmp_local_vars.append(tmp_string)
								local_var_cnt += 1
							tmp_string = ''
					else:	
						#questa e' la variabile, la salvo tutta in tmp_string
						tmp_string = tmp_string + curr_line[k]
						k = k + 1
				if len(tmp_string) > 0:
					if is_function == 0:
						#ho trovato una variabile globale
						global_vars.append(tmp_string)
					else:
						#variabile locale di una funzione
						tmp_local_vars.append(tmp_string)
						local_var_cnt += 1
						
	#controllo se le variabili dichiarate sono usate
	for gvar in global_vars:
		gv_counter = 0
		p = re.compile('\\b'+gvar+'\\b')
		for line in lines:
			m = p.search(line)
			if m:
				#print 'OK ', fun
				gv_counter +=1
		gvar_counter.append(gv_counter)
		if gv_counter < 2:
			print 'KO - Occorrenze per', gvar, ':', gv_counter
		#elif gv_counter >= 2:
			#print 'OK - Occorrenze per', gvar, ':', gv_counter
	#controllo variabili locali
	for i in range(0,len(function_list)):
		for lvar in local_vars[i]:
			lv_counter = 0
			p = re.compile('\\b'+lvar+'\\b')
			for line in function_list[i]:
				m = p.search(line)	# ' '.join(function_list[i]
				if m:
					lv_counter += 1
			lvar_counter.append(lv_counter)
			if lv_counter < 2:
				print 'KO - Occorrenze per', lvar, ':', lv_counter
			#elif lv_counter >= 2:
				#print 'OK - Occorrenze per', lvar, ':', lv_counter
				
	#for i in range(0,len(function_list)):
		#print len(function_list), function_list[i]

#______________________________

count_functions_usage('d.js')
print '******************'
count_variables_usage()

#______________________________


