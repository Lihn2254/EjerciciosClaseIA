import java.util.LinkedList;

public class Nodo implements Comparable<Nodo> {
    String estado;
    int nivel, costo;
    Nodo padre;

    public Nodo(String estado) {
        this.estado = estado;
    }

    public Nodo(String estado, int costo) {
        this.estado = estado;
        this.costo = costo;
    }

    LinkedList<Nodo> generarSucesores(String estadoActual, String estadoObjetivo) {
        LinkedList<Nodo> sucesores = new LinkedList<>();
        /* Aquí se busca la posición del vacío */
        int indice = estadoActual.indexOf('_');
        /* Se calcula el costo una sola vez para todos los sucesores */
        int costo = calcularCostoBordes(estadoObjetivo);

        switch (indice) {
            case 0:
                // Puede ir a 1 (derecha) y 3 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 0, 1), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 0, 3), costo));
                break;

            case 1:
                // Puede ir a 0 (izq), 2 (der), 4 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 1, 0), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 1, 2), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 1, 4), costo));
                break;

            case 2:
                // Puede ir a 1 (izq) y 5 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 2, 1), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 2, 5), costo));
                break;

            case 3:
                // Puede ir a 0 (arriba), 4 (der), 6 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 3, 0), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 3, 4), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 3, 6), costo));
                break;

            case 4:
                // Puede ir a 1 (arriba), 3 (izq), 5 (der), 7 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 4, 1), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 4, 3), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 4, 5), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 4, 7), costo));
                break;

            case 5:
                // Puede ir a 2 (arriba), 4 (izq), 8 (abajo)
                sucesores.add(new Nodo(intercambiar(estadoActual, 5, 2), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 5, 4), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 5, 8), costo));
                break;

            case 6:
                // Puede ir a 3 (arriba) y 7 (der)
                sucesores.add(new Nodo(intercambiar(estadoActual, 6, 3), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 6, 7), costo));
                break;

            case 7:
                // Puede ir a 4 (arriba), 6 (izq), 8 (der)
                sucesores.add(new Nodo(intercambiar(estadoActual, 7, 4), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 7, 6), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 7, 8), costo));
                break;

            case 8:
                // Puede ir a 5 (arriba) y 7 (izq)
                sucesores.add(new Nodo(intercambiar(estadoActual, 8, 5), costo));
                sucesores.add(new Nodo(intercambiar(estadoActual, 8, 7), costo));
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

    public int calcularCostoDiferenciaAbsoluta(String estadoObjetivo) {
        int costo = 0;

        for (int i = 0; i < estadoObjetivo.length(); i++) {
            costo += estadoObjetivo.charAt(i) != estado.charAt(i) ? 1 : 0;
        }

        return costo;
    }

    public int calcularCostoBordes(String estadoObjetivo) {
        int costo = 0;

        for (int i = 0; i < estadoObjetivo.length(); i++) {
            if (i == 4) continue; // Se omite el centro
            costo += estadoObjetivo.charAt(i) != estado.charAt(i) ? 1 : 0;
        }

        return costo;
    }

    public int calcularCostoManhattan(String estadoObjetivo) {
        int costo = 0;

        for (int i = 0; i < estado.length(); i++) {
            char pieza = estado.charAt(i);
            if (pieza == '_') continue; // El espacio vacío no se cuenta

            int j = estadoObjetivo.indexOf(pieza);

            int filaActual  = i / 3;
            int colActual   = i % 3;
            int filaObjetivo = j / 3;
            int colObjetivo  = j % 3;

            costo += Math.abs(filaActual - filaObjetivo) + Math.abs(colActual - colObjetivo);
        }

        return costo;
    }

    @Override
    public int compareTo(Nodo n) {
        return this.costo - n.costo;
    }
}

