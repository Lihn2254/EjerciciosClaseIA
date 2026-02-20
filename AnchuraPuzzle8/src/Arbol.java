import java.util.*;

public class Arbol {
    Nodo raiz;

    public Arbol(Nodo raiz) {
        this.raiz = raiz;
        if (this.raiz != null) {
            this.raiz.nivel = 0;
        }
    }

    Nodo busquedaxAnchura(String estadoObjetivo) {
        if (raiz == null) return null;

        /* Guardamos los nodos visitados */
        HashSet<String> visitados = new HashSet<>();
        /* Lista de estados a visitar */
        Queue<Nodo> cola = new LinkedList<>();

        /* Inicio */
        cola.add(raiz);
        visitados.add(raiz.estado);

        while (!cola.isEmpty()) {
            /* Lo sacamos de la lista y lo guardamos en "actual" */
            Nodo actual = cola.poll();

            /* Si es el estado objetivo, lo devolvemos */
            if (actual.estado.equals(estadoObjetivo)) {
                imprimirCaminoSolucion(actual);
                return actual;
            }

            /* Genereamos los sucesores y los agregamos a la lista */
            List<Nodo> sucesores = actual.generarSucesores(actual.estado);
            for (Nodo hijo : sucesores) {
                if (!visitados.contains(hijo.estado)) {
                    hijo.padre = actual;
                    hijo.nivel = actual.nivel + 1;
                    visitados.add(hijo.estado);
                    cola.add(hijo);
                }
            }
        }
        return null;
    }

    private void imprimirCaminoSolucion(Nodo objetivo) {
        LinkedList<Nodo> camino = new LinkedList<>();
        Nodo actual = objetivo;
        while (actual != null) {
            camino.addFirst(actual);
            actual = actual.padre;
        }

        int i = 0;
        for (Nodo nodo : camino) {
            System.out.println(i + " - Estado:\t" + nodo.estado);
            i++;
        }
    }
}
