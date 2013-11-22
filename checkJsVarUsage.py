import re
import sys

lines = []		#variabile globale
script_file = ''	#variabile globale

#elimino i commenti in formato C e C++ (doppio slash e slash-asterisco)
#il file originale (diviso in righe) e' in script_file, quello pulito (diviso in righe) e' in lines
def strip_comments():
	is_cpp_comment = False
	double_slash = re.compile('\\b//\\b')
	cpp_comment_a = re.compile('\\b/[*]\\b')
	cpp_comment_b = re.compile('\\b[*]/\\b')
	#elimino tutte le righe commentate e memorizzo quelle valide in lines
	for line in script_file:
		curr_line = line.strip()
		m_slash = double_slash.search(curr_line)
		m_cpp_a = cpp_comment_a.search(curr_line)
		m_cpp_b = cpp_comment_b.search(curr_line)
		#cerco i commenti nei vari formati; se li trovo, rimuovo la parte commentata
		if m_cpp_a:
			is_cpp_comment = True
			tmp_str = curr_line[0:m_cpp_a.start()]
			if len(tmp_str) > 0:
				lines.append(tmp_str)
		if m_cpp_b:
			is_cpp_comment = False
			tmp_str = curr_line[m_cpp_b.end():]
			if len(tmp_str) > 0:
				lines.append(tmp_str)
		if is_cpp_comment == False:
			if m_slash:
				#ho trovato un commento che inizia con il doppio slash, salvo la riga che lo contiene escludendo tutto quello che lo segue
				tmp_str = curr_line[0:m_slash.start()]
				if len(tmp_str) > 0:
					lines.append(tmp_str)
			if m_cpp_a == None and m_cpp_b == None and m_slash == None:
				lines.append(curr_line)

#conto le varie funzioni ed il numero di volte in cui sono chiamate - OK se per ogni funzione trovo almeno 2 occorrenze (definizione e 1 chiamata)
def count_functions_usage(filename):
	global script_file
	global lines
	fnc = []	#contiene l'elenco delle funzioni
	fnc_counter = []	#conta le occorrenze delle funzioni trovate

	p = re.compile('\\bfunction\\b')
	
	f = open(filename, 'r')
	script_file = f.readlines()	#memorizzo tutte le righe nell'array, una riga per elemento
	f.close()
	#rimuovo i commenti e salvo le righe ripulite in lines
	strip_comments()
	
	#identifico le funzioni nello script e salvo i loro nomi in fnc
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
	#se trovo una sola occorrenza, la funzione non e' mai usata
	for fun in fnc:
		fun_counter = 0
		p = re.compile('\\b'+fun+'\\b')
		for line in lines:
			m = p.search(line)
			if m:
				fun_counter +=1
		fnc_counter.append(fun_counter)
		if fun_counter < 2:
			print 'KO - Occorrenze per', fun, ':', fun_counter
		#else:
			#print 'OK - Occorrenze per', fun, ':', fun_counter
			
#conto le varie variabili ed il numero di volte in cui sono chiamate - OK se per ogni variabile trovo almeno 2 occorrenze (definizione e 1 uso)
def count_variables_usage():
	global_vars = []	#variabili globali
	local_vars = []		#variabili locali
	p = re.compile('\\bfunction\\b')
	vr = re.compile('\\bvar\\b')
	block_start = re.compile('{')
	block_end = re.compile('}')
	is_function = False		#true o false
	tmp_local_vars = []
	tmp_function_list = []
	gvar_counter = []
	lvar_counter = []	
	function_list = []	#lista di liste che contengono le righe delle funzioni che hanno almeno 1 variabile locale
	local_var_cnt = 0	#conto quante variabili locali ho per ogni funzione
	parenthesis_stack = []	#tengo conto delle parentesi graffe aperte e chiuse per capire quando finisce una funzione

	#cerco le variabili dichiarate
	for line in lines:
		curr_line = line.strip()	#rimuovo spazi
		#cerco una varibile o l'inizio o la fine di una funzione
		#l'idea e' di salvare in function_list tutte le funzioni che hanno almeno una variabile locale e in local_vars le variabili locali
		#quando ho l'elenco delle variabili locali, ricontrollo lines per controllare quante volte si usano le variabili: per le locali
		#cerco se la lista i-esima di function_list (cioe' la i-esima funzione) contiene almeno 2 occorrenze delle varibili nella lista i-esima
		#di local_vars, cioe' le varibili locali di quella funzione
		m_var = vr.search(curr_line)
		m_function = p.search(curr_line)
		m_blockstart = block_start.search(curr_line)
		m_blockend = block_end.search(curr_line)
		if is_function == True:
			tmp_function_list.append(curr_line)	#per ora salvo la funzione, poi copiata nella lista (di liste) function_list
		if m_blockstart:
			parenthesis_stack.append('{')	#aggiungo una parentesi; a fine funzione, la lista deve essere vuota, altrimenti problema di bilanciamento
		if m_function:
			#da qui trovero' variabili locali
			is_function = True
			local_var_cnt = 0
			del tmp_local_vars[:]	#pulisco la lista
			del tmp_function_list[:]
			tmp_function_list.append(curr_line)
		if m_blockend:
			parenthesis_stack.pop()
			if(len(parenthesis_stack) == 0):
				#fine variaibli locali per una certa funzione, copio quelle che ho trovato in un elemento della lista (avro' una lista di liste)
				is_function = False
				if len(tmp_local_vars) > 0:
					local_vars.append(list(tmp_local_vars))	#aggiungo alla lista la lista delle variabili locali di una funzione
				if local_var_cnt > 0:
					function_list.append(list(tmp_function_list))	#aggiungo la funzione solo se ha almeno 1 variabile locale
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
							if is_function == False:
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
					if is_function == False:
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

#______________________________

count_functions_usage(sys.argv[1])
print '******************'
count_variables_usage()

#______________________________


