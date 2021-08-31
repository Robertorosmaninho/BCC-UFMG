import numpy as np

def setCoverPrimalDual(n, m, c, a):
    cover_sets = np.zeros(m, dtype=np.int64)
    cover, dual_sol = np.zeros(n, dtype=np.int64), np.zeros(n, dtype=np.int64) 
    a_t = np.transpose(a)
    
    for i in range(n):
        aux = np.zeros(n, dtype=np.int64) 
        # Se o vértice já estiver na cobertura não devemos fazer nada
        if (1 not in a[i]) or (cover[i] != 0): continue 
		
        # aumenta x_i ao máximo de modo que x permaneça viável
        while np.all(a_t.dot(aux) <= c): aux[i] += 1
        aux[i] -= 1
        dual_sol[i] = aux[i]
        
        # Linhas de igualdade a_t*x = c
        check_constraint = np.where((a_t.dot(aux) == c))[0]

        # Pega a primeira linha em que ocorreu a igualdade (conjunto S)
        cover_idx = check_constraint[0] 
        cover_sets[cover_idx] = 1

		# Identifica os elementos já cobertos
        covered_vertex = list(np.where(a_t[cover_idx] == 1)[0])
        for vertex in covered_vertex: cover[vertex] = 1
			
		# Reduz os valores de c pela restrição igualada
        equal = list(np.where(np.array(a[i]) == 1)[0])
        for x in equal: c [x] -= dual_sol[i]

        # Para evitar conflitos a solução encontrada vira infinito
        c = [x if x > 0 else np.Inf for x in c]
        
    return dual_sol, cover_sets

def read():
    N, M = map(int, input().split())
    C = list(map(float, input().split()))
    A = [[0 for _ in range(M)] for _ in range(N)]
    
    for i in range(N):
        line = list(map(float, input().split()))
        for j, x in enumerate(line):
            A[i][j] = x

    return M, N, C, A


if __name__ == '__main__':
    m, n, c, a = read()
    sol, cover_sets = setCoverPrimalDual(n, m, c,a) 
    print(*cover_sets)
    print(*sol)