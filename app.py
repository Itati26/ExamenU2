from flask import Flask, render_template, request
from arbol import Nodo

app = Flask(__name__)

# =====================================================
# GRAFO UNIFICADO
# =====================================================

conexiones = {
    'Jiloyork': {'CDMX', 'Queretaro'},
    'Morelos': {'Queretaro'},
    'CDMX': {'Jiloyork', 'Queretaro', 'Hidalgo'},
    'Hidalgo': {'CDMX', 'Queretaro', 'Mexicali', 'Monterrey'},
    'Queretaro': {
        'SanLuisPotosi',
        'Morelos',
        'Jiloyork',
        'CDMX',
        'Monterrey',
        'Sonora',
        'Hidalgo',
        'Mexicali',
        'Aguascalientes'
    },
    'SanLuisPotosi': {'Aguascalientes', 'Queretaro'},
    'Aguascalientes': {'SanLuisPotosi', 'Queretaro'},
    'Sonora': {'Queretaro', 'Mexicali'},
    'Mexicali': {'Monterrey', 'Hidalgo', 'Queretaro'},
    'Monterrey': {'Mexicali', 'Queretaro', 'Hidalgo'}
}

# =====================================================
# GRAFO UCS
# =====================================================

conexiones_ucs = {
    'Jiloyork': {'CDMX': 125, 'Queretaro': 513},
    'Morelos': {'Queretaro': 524},
    'CDMX': {'Jiloyork': 125, 'Queretaro': 423, 'Hidalgo': 491},
    'Hidalgo': {
        'CDMX': 491,
        'Queretaro': 356,
        'Mexicali': 309,
        'Monterrey': 346
    },
    'Queretaro': {
        'SanLuisPotosi': 203,
        'Morelos': 514,
        'Jiloyork': 513,
        'CDMX': 423,
        'Monterrey': 603,
        'Sonora': 437,
        'Hidalgo': 356,
        'Mexicali': 313,
        'Aguascalientes': 599
    },
    'SanLuisPotosi': {
        'Aguascalientes': 390,
        'Queretaro': 599
    },
    'Aguascalientes': {
        'SanLuisPotosi': 390,
        'Queretaro': 203
    },
    'Sonora': {
        'Queretaro': 437,
        'Mexicali': 394
    },
    'Mexicali': {
        'Monterrey': 296,
        'Hidalgo': 309,
        'Queretaro': 313
    },
    'Monterrey': {
        'Mexicali': 296,
        'Queretaro': 603,
        'Hidalgo': 346
    }
}

# =====================================================
# BFS
# =====================================================

def buscar_solucion_BFS(conexiones, estado_inicial, solucion):

    nodos_visitados = []
    nodos_frontera = []

    nodo_inicial = Nodo(estado_inicial)
    nodos_frontera.append(nodo_inicial)

    while len(nodos_frontera) != 0:

        nodo = nodos_frontera.pop(0)
        nodos_visitados.append(nodo)

        if nodo.get_datos() == solucion:
            return nodo

        for un_hijo in conexiones.get(nodo.get_datos(), []):

            hijo = Nodo(un_hijo)
            hijo.set_padre(nodo)

            if not hijo.en_lista(nodos_visitados) and not hijo.en_lista(nodos_frontera):
                nodos_frontera.append(hijo)

    return None

# =====================================================
# DFS ITERATIVA
# =====================================================

def DFS_prof_iter(nodo, solucion):

    for limite in range(0, 100):

        visitados = []

        sol = buscar_solucion_DFS_Rec(
            nodo,
            solucion,
            visitados,
            limite
        )

        if sol is not None:
            return sol

    return None

def buscar_solucion_DFS_Rec(nodo, solucion, visitados, limite):

    if limite > 0:

        visitados.append(nodo.get_datos())

        if nodo.get_datos() == solucion:
            return nodo

        lista_hijos = []

        for un_hijo in conexiones.get(nodo.get_datos(), []):

            if un_hijo not in visitados:

                hijo = Nodo(un_hijo)
                hijo.set_padre(nodo)

                lista_hijos.append(hijo)

        nodo.set_hijos(lista_hijos)

        for nodo_hijo in nodo.get_hijos():

            sol = buscar_solucion_DFS_Rec(
                nodo_hijo,
                solucion,
                visitados,
                limite - 1
            )

            if sol is not None:
                return sol

    return None

# =====================================================
# UCS
# =====================================================

def buscar_solucion_ucs(conexiones, nodo_inicial, solucion):

    nodos_visitados = []
    nodos_frontera = []

    nodo_inicial.set_costo(0)
    nodos_frontera.append(nodo_inicial)

    while len(nodos_frontera) != 0:

        nodos_frontera = sorted(
            nodos_frontera,
            key=lambda x: x.get_costo()
        )

        nodo = nodos_frontera.pop(0)

        nodos_visitados.append(nodo)

        if nodo.get_datos() == solucion:
            return nodo

        dato_nodo = nodo.get_datos()

        lista_hijos = []

        for un_hijo in conexiones[dato_nodo]:

            hijo = Nodo(un_hijo)

            hijo.set_padre(nodo)

            costo = conexiones[dato_nodo][un_hijo]

            hijo.set_costo(
                nodo.get_costo() + costo
            )

            lista_hijos.append(hijo)

            if not hijo.en_lista(nodos_visitados):

                if hijo.en_lista(nodos_frontera):

                    for n in nodos_frontera:

                        if n.igual(hijo) and n.get_costo() > hijo.get_costo():

                            nodos_frontera.remove(n)
                            nodos_frontera.append(hijo)

                else:
                    nodos_frontera.append(hijo)

        nodo.set_hijos(lista_hijos)

    return None

# =====================================================
# OBTENER RUTA
# =====================================================

def obtener_ruta(nodo, inicio):

    resultado = []

    while nodo.get_padre() is not None:
        resultado.append(nodo.get_datos())
        nodo = nodo.get_padre()

    resultado.append(inicio)

    resultado.reverse()

    return resultado

# =====================================================
# WEB
# =====================================================

@app.route('/', methods=['GET', 'POST'])
def index():

    resultado_bfs = None
    resultado_dfs = None
    resultado_ucs = None
    costo_ucs = None
    algoritmo = None

    if request.method == 'POST':

        algoritmo = request.form['algoritmo']
        inicio = request.form['inicio']
        destino = request.form['destino']

        # ================= BFS =================

        nodo_bfs = buscar_solucion_BFS(
            conexiones,
            inicio,
            destino
        )

        if nodo_bfs:
            resultado_bfs = obtener_ruta(
                nodo_bfs,
                inicio
            )

        # ================= DFS =================

        nodo_inicial_dfs = Nodo(inicio)

        nodo_dfs = DFS_prof_iter(
            nodo_inicial_dfs,
            destino
        )

        if nodo_dfs:
            resultado_dfs = obtener_ruta(
                nodo_dfs,
                inicio
            )

        # ================= UCS =================

        nodo_inicial_ucs = Nodo(inicio)

        nodo_ucs = buscar_solucion_ucs(
            conexiones_ucs,
            nodo_inicial_ucs,
            destino
        )

        if nodo_ucs:
            resultado_ucs = obtener_ruta(
                nodo_ucs,
                inicio
            )

            costo_ucs = nodo_ucs.get_costo()

    return render_template(
        'index.html',
        resultado_bfs=resultado_bfs,
        resultado_dfs=resultado_dfs,
        resultado_ucs=resultado_ucs,
        costo_ucs=costo_ucs,
        algoritmo=algoritmo
    )

if __name__ == '__main__':
    app.run()