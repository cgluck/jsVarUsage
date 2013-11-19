import re

fnc = []	#contiene l'elenco delle funzioni
fnc_counter = []	#conta le occorrenze delle funzioni trovate
lines = []

def count_functions_usage(filename):
	is_cpp_comment = 0

	p = re.compile('function')
	double_slash = re.compile('//')
	cpp_comment_a = re.compile('/[*]')
	cpp_comment_b = re.compile('[*]/')
	f = open(filename, 'r')

	script_file = f.readlines()	#memorizzo tutte le righe nell'array, una riga per elemento
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
		p = re.compile(fun, re.M)
		for line in lines:
			m = p.search(line)
			if m:
				#print 'OK ', fun
				fun_counter +=1
		fnc_counter.append(fun_counter)
		if fun_counter < 2:
			print 'KO - Occorrenze per', fun, ':', fun_counter
		else:
			print 'OK - Occorrenze per', fun, ':', fun_counter
	f.close()
#______________________________

count_functions_usage('b.js')

