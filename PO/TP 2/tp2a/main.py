import numpy as np
# Esse simplex foi escrito pelo aluno Breno Poggiali e eu, Roberto Rosmaninho, não
# apenas alterei sua implementação lógica, bem como a modelagem do problema na função
# read() e __main__ para que a solução do problema proposto pelo TP2A seja dada de forma
# correta e satisfatória
N = M = 0
SIMPLEX = AUXILIAR = C = []
epsilon = 1e-10

def floatToString(inputValue):
	return ('%.10f' % round(inputValue + epsilon, 5)).rstrip('0').rstrip('.')

def is_fpi():
	rows = len(SIMPLEX)
	cols = len(SIMPLEX[0])

	for i in range(1, rows):
		if round(SIMPLEX[i][cols-1], 5) < 0:
			return False
	return True

def get_c_negativo_idx(simplex):
	for idx, i in enumerate(simplex[0][:-1]):
		if round(i, 5) < 0:
			return idx
	return -1

def get_pivot_row(simplex, pivo_col):
	rows = len(simplex)
	cols = len(simplex[0])
	mini = -1
	min_row = 0
	for i in range(1, rows):
		if round(simplex[i][pivo_col], 5) > 0:
			aux = np.round(simplex[i][cols-1] / simplex[i][pivo_col], 5)
			if mini == -1 or aux < mini:
				mini = aux
				min_row = i
	if mini == -1:
		print_ilimitada(simplex, pivo_col)
		return -1
	return min_row

def execute_pivot(simplex, pivo_row, pivo_col):
	rows = len(simplex)
	cols = len(simplex[0])

	multiply_factor = 1 / simplex[pivo_row][pivo_col]
	# print(pivo_row, pivo_col, multiply_factor, simplex[pivo_row][pivo_col])
	for j in range(cols):
		simplex[pivo_row][j] *= multiply_factor

	for i in range(rows):
		if i != pivo_row:
			aux = -simplex[i][pivo_col]
			for j in range(cols):
				simplex[i][j] += aux * simplex[pivo_row][j]
	
	return simplex

def col_is_base(simplex, col, ignore):
	rows = len(simplex)
	if round(simplex[0][col], 5) != 0 and not ignore:
		return 0
	
	rows_one = 0
	for i in range(1, rows):
		if round(simplex[i][col], 5) == 1:
			if rows_one:
				return 0
			else:
				rows_one = i
		elif round(simplex[i][col], 5) != 0:
			return 0
	
	return rows_one

def print_ilimitada(simplex, pivo_col):
	rows = len(simplex)
	cols = len(simplex[0])
	
	print("ilimitada")
	solution_size = print_solucao(simplex, rows-1, cols-rows)

	certificado = [0 for _ in range(cols+rows)]
	certificado[pivo_col] = 1
	for j in range(cols-rows):
		if j != pivo_col:
			rows = col_is_base(simplex, j, False)
			if rows:
				certificado[j] = -simplex[rows][pivo_col]
			else:
				certificado[j] = 0

	certificado = certificado[:solution_size]
	certificado = " ".join(map(floatToString, certificado))
	print(certificado)


def print_solucao(simplex, n, m):
	global SOLUCAO
	cols = len(simplex[0])
	solucao = [0 for _ in range(m)]
	base_utilizada = [0 for _ in range(n)]

	for j in range(m):
		col_base = col_is_base(simplex, j, False)
		if col_base and base_utilizada[col_base-1] == 0:
			solucao[j] = simplex[col_base][cols-1]
			base_utilizada[col_base-1] = 1
		else:
			solucao[j] = 0
	
	
	print(" ".join(map(floatToString, solucao)))
	SOLUCAO = solucao
	return len(solucao)


def print_certificado(simplex, n, m):
	global VERO
	certificado = simplex[0][m:m+n]
	VERO = [int(i) for i in certificado]
	#print(" ".join(map(floatToString, certificado)))


def solve_fpi_primal(simplex, is_original):
	pivo_row = -1
	pivo_col = get_c_negativo_idx(simplex)

	while pivo_col != -1:
		pivo_row = get_pivot_row(simplex, pivo_col)
		if pivo_row == -1:
			return
		simplex = execute_pivot(simplex, pivo_row, pivo_col)
		pivo_col = get_c_negativo_idx(simplex)


	if is_original:
		#print("otima")
		global FN_OTIMO
		FN_OTIMO = simplex[0][len(simplex[0])-1]
		print(floatToString(simplex[0][len(simplex[0])-1]))
		print_solucao(simplex, N, M)
		print_certificado(simplex, N, M)

	
def get_auxiliar():
	global AUXILIAR, SIMPLEX
	AUXILIAR = [[0 for _ in range(M+2*N+1)] for __ in range(N+1)]
	rows = len(AUXILIAR)
	cols = len(AUXILIAR[0])
	for i in range(N+M, cols-1):
		AUXILIAR[0][i] = 1
	
	for i in range(1, N+1):
		aux = 1
		if SIMPLEX[i][N+M] < 0:
			aux *= -1
		
		# simplex com sinal invertido
		for j in range(N+M):
			AUXILIAR[i][j] = aux * SIMPLEX[i][j]
		
		# B
		AUXILIAR[i][cols-1] = aux * SIMPLEX[i][N+M]

		# Identidade das variáveis de folga
		AUXILIAR[i][N+M+i-1] = 1
	
	return rows, cols

def initial_auxiliar_sum(rows, cols):
	global AUXILIAR
	for j in range(cols):
		soma = 0
		for i in range(1, rows):
			soma += -AUXILIAR[i][j]
		AUXILIAR[0][j] += soma


def popular_original_pl(simplex, auxiliar, n, m):
	for i in range(1, n+1):
		for j in range(n + m):
			simplex[i][j] = auxiliar[i][j]
		simplex[i][n+m] = auxiliar[i][len(auxiliar[0])-1]
	return simplex
	


def print_solucao_original(simplex, auxiliar, n, m):
	simplex = popular_original_pl(simplex, auxiliar, n, m)
	
	for j in range(n + m):
		
		row_one = col_is_base(simplex, j, True)

		if row_one:
			aux = - simplex[0][j]
			for i in range(n+m+1):
				simplex[0][i] += aux * simplex[row_one][i]

	solve_fpi_primal(simplex, True)



def resposta_auxiliar():
	global AUXILIAR, SIMPLEX, N, M
	resultado = AUXILIAR[0][-1]
	if round(resultado, 5) < 0:
		print("inviavel")
		print_certificado(AUXILIAR, N, M)
		return
	print_solucao_original(SIMPLEX, AUXILIAR, N, M)


def solve_not_fpi():
	global AUXILIAR
	rows, cols = get_auxiliar()
	initial_auxiliar_sum(rows, cols)
	solve_fpi_primal(AUXILIAR, False)
	resposta_auxiliar()

def read():
	global N, M, C, SIMPLEX
	global A, CAPACIDADES
	N, M = map(int, input().split())
	global N_rows
	N_rows = N 
	B_temp = list(map(float, input().split()))
	CAPACIDADES = B_temp
	SIMPLEX = [[0 for _ in range(2*M+N-1)] for __ in range(N+M-1)]

	B =  [0] * (N - 2) + B_temp
	C = list(map(float, input().split()))
	A = [[0 for _ in range(M)] for _ in range(N_rows)]
	# -C
	for idx, c in enumerate(C):
		SIMPLEX[0][idx] = c
		A[0][idx] = c
	#print()

	# Identidade das variáveis de folga
	for i in range(1, N+M-1):
		SIMPLEX[i][M+i-1] = 1

	# Arestas
	for i in range(N-1, N+M-1):
		SIMPLEX[i][i-N+1] = 1	

	# A e B
	
	for i in range(1, N):
		line = list(map(float, input().split()))
		for j, x in enumerate(line):
			if i < N-1:
				SIMPLEX[i][j] = x
			A[i][j] = x


	for i in range(1,N+M-1):	
		SIMPLEX[i][-1] = B[i-1]

	#print(np.array(A))
	

	N = N + M - 2 

def solve():
	if is_fpi():
		solve_fpi_primal(SIMPLEX, True)
	else:
		solve_not_fpi()

def check_capacidades(capacidades, x):
	#print("cap: ", capacidades)
	#print("x", x)
	for i in range(len(capacidades)):
		if x[i] > capacidades[i]:
			return False
	return True

def check_min_cut_value(capacidades, incidence_matrix, valor_objetivo, y):
	min_cut_value = 0
	for aresta in range(incidence_matrix.shape[1]):
		count = 0
		for vertice in range(incidence_matrix.shape[0]):
			if (y[vertice] == 1 and incidence_matrix[vertice, aresta] == -1) or (y[vertice] == 0 and incidence_matrix[vertice, aresta] == 1):
				count += 1
		if count == 2:
			min_cut_value += capacidades[aresta]
	
	if min_cut_value == valor_objetivo:
		return True
	else:
		return False

if __name__ == '__main__':
	read()
	solve()
	v_set = [1] + VERO[:N_rows-2] + [0]
	sol = SOLUCAO
	print(*v_set)
	#print(check_capacidades(CAPACIDADES,sol))
	#print(check_min_cut_value(CAPACIDADES, np.array(A), FN_OTIMO, v_set))

