import java.util.ArrayList;
import java.util.Arrays;
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

    public LinkedList<Nodo> generarSucesores(String estadoActual, String estadoObjetivo, int tipoCalculoCosto) {
        LinkedList<Nodo> sucesores = new LinkedList<>();

        final int COLS = 5;

        int indice = estadoActual.indexOf('_');

        // Calculo del costo de acuerdo a selección del usuario
        int costo = calcularHeuristica(estadoObjetivo, tipoCalculoCosto);

        int fila = indice / COLS;
        int col = indice % COLS;

        if (fila > 0)
            sucesores.add(new Nodo(intercambiar(estadoActual, indice, indice - COLS), costo));

        if (fila < COLS - 1)
            sucesores.add(new Nodo(intercambiar(estadoActual, indice, indice + COLS), costo));

        if (col > 0)
            sucesores.add(new Nodo(intercambiar(estadoActual, indice, indice - 1), costo));

        if (col < COLS - 1)
            sucesores.add(new Nodo(intercambiar(estadoActual, indice, indice + 1), costo));

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

    private int calcularCostoDiferenciaAbsoluta(String estadoObjetivo) {
        int costo = 0;

        for (int i = 0; i < estadoObjetivo.length(); i++) {
            costo += estadoObjetivo.charAt(i) != estado.charAt(i) ? 1 : 0;
        }

        return costo;
    }

    private int calcularCostoBordes(String estadoObjetivo) {
        int costo = 0;

        ArrayList<Integer> itemsNoRevisados = new ArrayList<>(
                Arrays.asList(7, 8, 9, 12, 13, 14, 17, 18, 19));

        for (int i = 0; i < estadoObjetivo.length(); i++) {
            if (itemsNoRevisados.contains(i))
                continue; // Se omiten los elementos del centro
            costo += estadoObjetivo.charAt(i) != estado.charAt(i) ? 1 : 0;
        }

        return costo;
    }

    private int calcularCostoManhattan(String estadoObjetivo) {
        int costo = 0;

        for (int i = 0; i < estado.length(); i++) {
            char pieza = estado.charAt(i);
            if (pieza == '_')
                continue; // El espacio vacío no se cuenta

            int j = estadoObjetivo.indexOf(pieza);

            int filaActual = i / 5;
            int colActual = i % 5;
            int filaObjetivo = j / 5;
            int colObjetivo = j % 5;

            costo += Math.abs(filaActual - filaObjetivo) + Math.abs(colActual - colObjetivo);
        }

        return costo;
    }

    private int calcularCostoManhattanPenalizacion(String estadoObjetivo) {
        final int COLS = 5;
        int costo = calcularCostoManhattan(estadoObjetivo);
        int penalizacion = 0;

        /*
         * Conflicto lineal por filas:
         * Dos piezas (a, b) generan conflicto cuando ambas están en la misma fila
         * actual Y ambas tienen su posición objetivo en esa misma fila, pero su
         * orden relativo actual es inverso al esperado en el objetivo.
         */
        for (int fila = 0; fila < COLS; fila++) {
            for (int col1 = 0; col1 < COLS; col1++) {
                int i = fila * COLS + col1;
                char piezaA = estado.charAt(i);
                if (piezaA == '_') continue;

                int goalI = estadoObjetivo.indexOf(piezaA);
                if (goalI / COLS != fila) continue; // A no pertenece a esta fila en el objetivo

                for (int col2 = col1 + 1; col2 < COLS; col2++) {
                    int j = fila * COLS + col2;
                    char piezaB = estado.charAt(j);
                    if (piezaB == '_') continue;

                    int goalJ = estadoObjetivo.indexOf(piezaB);
                    if (goalJ / COLS != fila) continue; // B no pertenece a esta fila en el objetivo

                    // col1 < col2 en el estado actual, pero A debe ir después de B en el objetivo
                    if (goalI % COLS > goalJ % COLS) penalizacion++;
                }
            }
        }

        /*
         * Conflicto lineal por columnas:
         * Igual que el de filas pero evaluando columnas.
         */
        for (int col = 0; col < COLS; col++) {
            for (int fila1 = 0; fila1 < COLS; fila1++) {
                int i = fila1 * COLS + col;
                char piezaA = estado.charAt(i);
                if (piezaA == '_') continue;

                int goalI = estadoObjetivo.indexOf(piezaA);
                if (goalI % COLS != col) continue; // A no pertenece a esta columna en el objetivo

                for (int fila2 = fila1 + 1; fila2 < COLS; fila2++) {
                    int j = fila2 * COLS + col;
                    char piezaB = estado.charAt(j);
                    if (piezaB == '_') continue;

                    int goalJ = estadoObjetivo.indexOf(piezaB);
                    if (goalJ % COLS != col) continue; // B no pertenece a esta columna en el objetivo

                    // fila1 < fila2 en el estado actual, pero A debe ir después de B en el objetivo
                    if (goalI / COLS > goalJ / COLS) penalizacion++;
                }
            }
        }

        return costo + penalizacion;
    }

    public int calcularHeuristica(String estadoObjetivo, int tipoCalculoCosto) {
        return switch (tipoCalculoCosto) {
            case 1 -> calcularCostoDiferenciaAbsoluta(estadoObjetivo);
            case 2 -> calcularCostoBordes(estadoObjetivo);
            case 3 -> calcularCostoManhattan(estadoObjetivo);
            case 4 -> calcularCostoManhattanPenalizacion(estadoObjetivo);
            default -> 0;
        };
    }

    @Override
    public int compareTo(Nodo n) {
        return this.costo - n.costo;
    }
}
