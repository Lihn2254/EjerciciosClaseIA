import java.util.*;

public class Arbol {
    Nodo raiz;

    /** Contador de nodos expandidos en la última búsqueda ejecutada. */
    private int nodosExpandidos = 0;

    public int getNodosExpandidos() {
        return nodosExpandidos;
    }

    /** Tiempo de ejecución de la última búsqueda en milisegundos. */
    private double tiempoEjecucion = 0;

    public double getTiempoEjecucion() {
        return tiempoEjecucion;
    }

    public Arbol(Nodo raiz) {
        this.raiz = raiz;
        if (this.raiz != null) {
            this.raiz.nivel = 0;
        }
    }

    public Nodo busquedaxAnchura(String estadoObjetivo) {
        if (raiz == null)
            return null;

        nodosExpandidos = 0;
        long inicio = System.nanoTime();
        Nodo resultado = null;

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

            /* Si es el estado objetivo, guardamos y salimos del bucle */
            if (actual.estado.equals(estadoObjetivo)) {
                resultado = actual;
                break;
            }

            nodosExpandidos++;

            /* Genereamos los sucesores y los agregamos a la lista */
            List<Nodo> sucesores = actual.generarSucesores(actual.estado, estadoObjetivo, -1);
            for (Nodo hijo : sucesores) {
                if (!visitados.contains(hijo.estado)) {
                    hijo.padre = actual;
                    hijo.nivel = actual.nivel + 1;
                    // hijo.costo = actual.costo + 1;
                    visitados.add(hijo.estado);
                    cola.add(hijo);
                }
            }
        }
        tiempoEjecucion = (System.nanoTime() - inicio) / 1_000_000.0;
        if (resultado != null) imprimirCaminoSolucion(resultado);
        return resultado;
    }

    public Nodo busquedaxProfundidad(String estadoObjetivo) {
        if (raiz == null)
            return null;

        nodosExpandidos = 0;
        long inicio = System.nanoTime();
        Nodo resultado = null;

        /* Guardamos los nodos visitados */
        HashSet<String> visitados = new HashSet<>();
        /* Lista de estados a visitar */
        Stack<Nodo> cola = new Stack<>();

        /* Inicio */
        cola.add(raiz);
        visitados.add(raiz.estado);

        while (!cola.isEmpty()) {
            /* Lo sacamos de la lista y lo guardamos en "actual" */
            Nodo actual = cola.pop();

            /* Si es el estado objetivo, guardamos y salimos del bucle */
            if (actual.estado.equals(estadoObjetivo)) {
                resultado = actual;
                break;
            }

            nodosExpandidos++;

            /* Genereamos los sucesores y los agregamos a la lista */
            List<Nodo> sucesores = actual.generarSucesores(actual.estado, estadoObjetivo, -1);
            for (Nodo hijo : sucesores) {
                if (!visitados.contains(hijo.estado)) {
                    hijo.padre = actual;
                    hijo.nivel = actual.nivel + 1;
                    // hijo.costo = actual.costo + 1;
                    visitados.add(hijo.estado);
                    cola.add(hijo);
                }
            }
        }
        tiempoEjecucion = (System.nanoTime() - inicio) / 1_000_000.0;
        if (resultado != null) imprimirCaminoSolucion(resultado);
        return resultado;
    }

    public Nodo busquedaxPrioridad(String estadoObjetivo, int tipoCalculoCosto) throws IllegalArgumentException {
        if (raiz == null)
            return null;

        if (estadoObjetivo.length() != 25) throw new IllegalArgumentException("String estadoObjetivo debe tener una longitud de 25");

        nodosExpandidos = 0;
        long inicio = System.nanoTime();
        Nodo resultado = null;

        /* Guardamos los nodos visitados */
        HashSet<String> visitados = new HashSet<>();
        /* Lista de estados a visitar */
        PriorityQueue<Nodo> cola = new PriorityQueue<>();

        /* Inicio */
        cola.add(raiz);
        visitados.add(raiz.estado);

        while (!cola.isEmpty()) {
            /* Lo sacamos de la lista y lo guardamos en "actual" */
            Nodo actual = cola.poll();

            /* Si es el estado objetivo, guardamos y salimos del bucle */
            if (actual.estado.equals(estadoObjetivo)) {
                resultado = actual;
                break;
            }

            nodosExpandidos++;

            /* Genereamos los sucesores y los agregamos a la lista */
            List<Nodo> sucesores = actual.generarSucesores(actual.estado, estadoObjetivo, tipoCalculoCosto);
            for (Nodo hijo : sucesores) {
                if (!visitados.contains(hijo.estado)) {
                    hijo.padre = actual;
                    hijo.nivel = actual.nivel + 1;
                    // hijo.costo = actual.costo + 1;
                    visitados.add(hijo.estado);
                    cola.add(hijo);
                }
            }
        }
        tiempoEjecucion = (System.nanoTime() - inicio) / 1_000_000.0;
        if (resultado != null) imprimirCaminoSolucion(resultado);
        return resultado;
    }

    public Nodo busquedaIDA(String estadoObjetivo, int tipoCalculoCosto) throws IllegalArgumentException {
        if (raiz == null)
            return null;

        if (estadoObjetivo.length() != 25)
            throw new IllegalArgumentException("String estadoObjetivo debe tener una longitud de 25");

        nodosExpandidos = 0;
        long inicio = System.nanoTime();
        Nodo resultado = null;

        /* El umbral inicial es h(raíz) */
        int umbral = raiz.calcularHeuristica(estadoObjetivo, tipoCalculoCosto);

        while (true) {
            /* minExcedido[0] acumula el menor f que superó el umbral en esta iteración */
            int[] minExcedido = { Integer.MAX_VALUE };

            Nodo solucion = idaStar_buscar(raiz, 0, umbral, estadoObjetivo, tipoCalculoCosto, minExcedido);

            if (solucion != null) {
                resultado = solucion;
                break;
            }

            /* Si ningún nodo superó el umbral con un f finito, no hay solución */
            if (minExcedido[0] == Integer.MAX_VALUE)
                break;

            /* Nuevo umbral = mínimo f que excedió el anterior */
            umbral = minExcedido[0];
        }
        tiempoEjecucion = (System.nanoTime() - inicio) / 1_000_000.0;
        if (resultado != null) imprimirCaminoSolucion(resultado);
        return resultado;
    }

    private Nodo idaStar_buscar(Nodo actual, int g, int umbral,
            String estadoObjetivo, int tipoCalculoCosto, int[] minExcedido) {

        int h = actual.calcularHeuristica(estadoObjetivo, tipoCalculoCosto);
        int f = g + h;

        /* Poda: este camino ya es demasiado costoso */
        if (f > umbral) {
            minExcedido[0] = Math.min(minExcedido[0], f);
            return null;
        }

        /* Comprobación de objetivo */
        if (actual.estado.equals(estadoObjetivo))
            return actual;

        nodosExpandidos++;

        List<Nodo> sucesores = actual.generarSucesores(actual.estado, estadoObjetivo, tipoCalculoCosto);
        for (Nodo hijo : sucesores) {
            /* Evitar ciclos revisando los ancestros del nodo actual */
            if (!estaEnCamino(actual, hijo.estado)) {
                hijo.padre = actual;
                hijo.nivel = actual.nivel + 1;

                Nodo resultado = idaStar_buscar(hijo, g + 1, umbral, estadoObjetivo, tipoCalculoCosto, minExcedido);
                if (resultado != null)
                    return resultado;
            }
        }
        return null;
    }

    private boolean estaEnCamino(Nodo nodo, String estado) {
        while (nodo != null) {
            if (nodo.estado.equals(estado))
                return true;
            nodo = nodo.padre;
        }
        return false;
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
            System.out.print("\n" + i + " - Estado:\t" + nodo.estado);
            i++;
        }
    }
}
