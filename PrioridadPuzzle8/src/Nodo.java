import java.util.LinkedList;

public class Nodo implements Comparable<Nodo> {
    String estado;
    int nivel;
    int costo;
    Nodo padre;

    public Nodo(String estado) {
        this.estado = estado;
    }

    LinkedList<Nodo> generarSucesores(String estadoActual) {
        LinkedList<Nodo> sucesores = new LinkedList<>();
        /* Aquí se busca la posición del vacío */
        int indice = estadoActual.indexOf('_');

        switch (indice) {
            case 0:
                // Puede ir a 1 (derecha) y 3 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 0, 1)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 0, 3)));
                break;

            case 1:
                // Puede ir a 0 (izq), 2 (der), 4 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 1, 0)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 1, 2)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 1, 4)));
                break;

            case 2:
                // Puede ir a 1 (izq) y 5 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 2, 1)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 2, 5)));
                break;

            case 3:
                // Puede ir a 0 (arriba), 4 (der), 6 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 3, 0)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 3, 4)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 3, 6)));
                break;

            case 4:
                // Puede ir a 1 (arriba), 3 (izq), 5 (der), 7 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 4, 1)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 4, 3)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 4, 5)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 4, 7)));
                break;

            case 5:
                // Puede ir a 2 (arriba), 4 (izq), 8 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 5, 2)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 5, 4)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 5, 8)));
                break;

            case 6:
                // Puede ir a 3 (arriba) y 7 (der)
                sucesores.add(new Nodo(intercambiar(estadoActual, 6, 3)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 6, 7)));
                break;

            case 7:
                // Puede ir a 4 (arriba), 6 (izq), 8 (der)
                sucesores.add(new Nodo(intercambiar(estadoActual, 7, 4)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 7, 6)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 7, 8)));
                break;

            case 8:
                // Puede ir a 5 (arriba) y 7 (izq)
                sucesores.add(new Nodo(intercambiar(estadoActual, 8, 5)));
                sucesores.add(new Nodo(intercambiar(estadoActual, 8, 7)));
                break;

            default:
                // Si no hay espacio, no genera nada
                break;
        }
        return sucesores;
    }

    private String intercambiar(String estado, int i, int j) {
        char a = estado.charAt(i);
        char b = estado.charAt(j);
        String resultado = "";
        for (int k = 0; k < estado.length(); k++) {
            if (k == i) {
                resultado += b;
            } else if (k == j) {
                resultado += a;
            } else {
                resultado += estado.charAt(k);
            }
        }
        return resultado;
    }

    @Override
    public int compareTo(Nodo n) {
        return this.costo - n.costo;
    }
}
