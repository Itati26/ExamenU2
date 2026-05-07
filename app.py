from flask import Flask, render_template, request
from arbol import Nodo

app = Flask(__name__)

# =========================
# CONEXIONES BFS y DFS
# =========================

conexiones = {
    'Jiloyork': {'Celaya', 'CDMX', 'Queretaro'},
    'Sonora': {'Zacatecas', 'Sinaloa'},
    'Guanajuato': {'Aguascalientes'},
    'Oaxaca': {'Queretaro'},
    'Sinaloa': {'Celaya', 'Sonora', 'Jiloyork'},
    'Queretaro': {'Monterrey', 'Tamaulipas', 'Zacatecas', 'Sinaloa', 'Jiloyork', 'Oaxaca'},
    'Celaya': {'Jiloyork', 'Sinaloa'},
    'Zacatecas': {'Sonora', 'Monterrey', 'Queretaro'},
    'Monterrey': {'Zacatecas', 'Sinaloa'},
    'Tamaulipas': {'Queretaro'}
}

# =========================
# CONEXIONES UCS
# =========================

conexiones_ucs = {
    'JILOYORK':{'CDMX': 125, 'QRO': 513},
    'MORELOS':{'QRO': 524},
    'CDMX':{'JILOYORK': 125, 'QRO': 423, 'HGO': 491},
    'HGO':{'CDMX': 491, 'QRO': 356, 'MEXICALI': 309, 'MTY': 346},
    'QRO':{'SLP': 203, 'MORELOS': 514, 'JILOYORK': 513, 'CDMX': 423,'MTY': 603,'SONORA': 437, 'HGO': 356,
           'MEXICALI': 313, 'AGS': 599},
    'SLP':{'AGS': 390, 'QRO': 599},
    'AGS':{'SLP': 390, 'QRO': 203},
    'SONORA':{'QRO': 437, 'MEXICALI': 394},
    'MEXICALI':{'MTY': 296, 'HGO': 309, 'QRO': 313},
    'MTY':{'MEXICALI': 296, 'QRO': 603, 'HGO': 346}
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

        dato_nodo = nodo.get_datos()

        for un_hijo in conexiones.get(dato_nodo, []):

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
# RUTA
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

@app.route("/", methods=["GET", "POST"])
def index():

    resultado = None
    costo = None

    if request.method == "POST":

        algoritmo = request.form["algoritmo"]
        inicio = request.form["inicio"]
        destino = request.form["destino"]

        # ================= UCS =================

        if algoritmo == "ucs":

            inicio = inicio.upper()
            destino = destino.upper()

            nodo_inicial = Nodo(inicio)

            nodo_solucion = buscar_solucion_ucs(
                conexiones_ucs,
                nodo_inicial,
                destino
            )

            if nodo_solucion:

                resultado = obtener_ruta(
                    nodo_solucion,
                    inicio
                )

                costo = nodo_solucion.get_costo()

        # ================= BFS =================

        elif algoritmo == "bfs":

            nodo_solucion = buscar_solucion_BFS(
                conexiones,
                inicio,
                destino
            )

            if nodo_solucion:
                resultado = obtener_ruta(
                    nodo_solucion,
                    inicio
                )

        # ================= DFS =================

        elif algoritmo == "dfs":

            nodo_inicial = Nodo(inicio)

            nodo_solucion = DFS_prof_iter(
                nodo_inicial,
                destino
            )

            if nodo_solucion:
                resultado = obtener_ruta(
                    nodo_solucion,
                    inicio
                )

    return render_template(
        "index.html",
        resultado=resultado,
        costo=costo
    )

if __name__ == "__main__":
    app.run(debug=True)