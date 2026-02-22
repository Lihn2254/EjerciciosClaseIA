import java.util.Scanner;

public class Main {
    public static void main(String[] args) throws Exception {
        Arbol arbol = new Arbol(new Nodo("_12345678"));
        String estadoObjetivo = "12345678_";
        Nodo n;

        Scanner sc = new Scanner(System.in);

        boolean continuar = true;
        while (continuar) {
            System.out.println("1. Anchura\n2. Profundidad\n3. Prioridad\n0. Salir\n");
            System.out.print("Indique método de búsqueda: ");
            int res = sc.nextInt();
            
            switch (res) {
                case 0:
                    continuar = false;
                    sc.close();
                    break;
                case 1:
                    System.out.println("\n--- Búsqueda por anchura ---\n");
                    n = arbol.busquedaxAnchura(estadoObjetivo);
                    System.out.println("\nNivel de la solución: " + n.nivel + "\n-------------------\n");
                    break;
                case 2:
                    System.out.println("\n--- Búsqueda por profundidad ---\n");
                    n = arbol.busquedaxProfundidad(estadoObjetivo);
                    System.out.println("\nNivel de la solución: " + n.nivel + "\n-------------------\n");
                    break;
                case 3:
                    System.out.println("\n--- Búsqueda por prioridad ---\n");
                    n = arbol.busquedaxPrioridad(estadoObjetivo);
                    System.out.println("\nNivel de la solución: " + n.nivel + "\n-------------------\n");
                    break;
                default:
                    System.out.println("Opción inválida\n");
                    break;
            }
        }
    }
}
