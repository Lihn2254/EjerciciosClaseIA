import java.util.Scanner;

public class Main {
    static Arbol arbol;
    static String estadoObjetivo;
    static Nodo n;

    static volatile boolean cargando = false;

    static Thread iniciarCarga() {
        cargando = true;
        Thread t = new Thread(() -> {
            String[] frames = { "\tCalculando.  ", "\tCalculando.. ", "\tCalculando..." };
            int i = 0;
            while (cargando) {
                System.out.print("\r" + frames[i % frames.length]);
                System.out.flush();
                i++;
                try {
                    Thread.sleep(400);
                } catch (InterruptedException e) {
                    break;
                }
            }

            System.out.print("\r" + " ".repeat(12) + "\r");
            System.out.flush();
        });
        t.setDaemon(true);
        t.start();
        return t;
    }

    static void detenerCarga(Thread t) {
        cargando = false;
        try {
            t.join();
        } catch (InterruptedException ignored) {
        }
    }

    public static void main(String[] args) throws Exception {
        Scanner sc = new Scanner(System.in);

        System.out.print("Ingrese el estado inicial (25 caracteres, espacio en blanco = _ ): ");
        String estadoInicial = sc.nextLine();
        arbol = new Arbol(new Nodo(estadoInicial));

        System.out.print("\nIngrese el estado final (25 caracteres, espacio en blanco = _ ): ");
        estadoObjetivo = sc.nextLine();

        menu(sc);
    }

    public static void menu(Scanner sc) throws OutOfMemoryError {
        boolean continuar = true;
        while (continuar) {
            System.out.println("\n---------------------------\n\tPUZZLE 24\n---------------------------\n");
            System.out.println("1. Anchura\n2. Profundidad\n3. Prioridad\n4. IDA (Iterative Deepening A*)\n0. Salir\n");
            System.out.print("Indique método de búsqueda: ");
            int res = sc.nextInt();
            sc.nextLine(); // consumir el salto de línea restante

            switch (res) {
                case 0:
                    continuar = false;
                    sc.close();
                    break;
                case 1:
                    System.out.println("\n--- Búsqueda por anchura ---\n");
                    Thread lt1 = iniciarCarga();
                    long inicio1 = System.nanoTime();
                    try {
                        n = arbol.busquedaxAnchura(estadoObjetivo);
                        detenerCarga(lt1);
                        System.out.println("\nNivel de la solución: " + n.nivel);
                        System.out.println("Nodos expandidos: " + arbol.getNodosExpandidos());
                        System.out.printf("Tiempo de ejecución: %.3f ms%n", arbol.getTiempoEjecucion());
                    } catch (OutOfMemoryError e) {
                        detenerCarga(lt1);
                        System.out.println("\nError: Memoria insuficiente.");
                        System.out.println("Nodos expandidos hasta el error: " + arbol.getNodosExpandidos());
                        System.out.printf("Tiempo hasta el error: %.3f ms%n",
                                (System.nanoTime() - inicio1) / 1_000_000.0);
                    }
                    System.out.println("-------------------\n");
                    break;
                case 2:
                    System.out.println("\n--- Búsqueda por profundidad ---\n");
                    Thread lt2 = iniciarCarga();
                    long inicio2 = System.nanoTime();
                    try {
                        n = arbol.busquedaxProfundidad(estadoObjetivo);
                        detenerCarga(lt2);
                        System.out.println("\nNivel de la solución: " + n.nivel);
                        System.out.println("Nodos expandidos: " + arbol.getNodosExpandidos());
                        System.out.printf("Tiempo de ejecución: %.3f ms%n", arbol.getTiempoEjecucion());
                    } catch (OutOfMemoryError e) {
                        detenerCarga(lt2);
                        System.out.println("\nError: Memoria insuficiente.");
                        System.out.println("Nodos expandidos hasta el error: " + arbol.getNodosExpandidos());
                        System.out.printf("Tiempo hasta el error: %.3f ms%n",
                                (System.nanoTime() - inicio2) / 1_000_000.0);
                    }
                    System.out.println("-------------------\n");
                    break;
                case 3:
                    System.out.println("\n--- Búsqueda por prioridad ---\n");
                    System.out.println(
                            "1. Diferencia absoluta\n2. Diferencia de bordes\n3. Distancia Manhattan\n4. Distancia Manhattan con penalización\n");
                    System.out.print("Indique método de cálculo de costo: ");
                    int resCosto = sc.nextInt();
                    Thread lt3 = iniciarCarga();
                    long inicio3 = System.nanoTime();
                    try {
                        n = arbol.busquedaxPrioridad(estadoObjetivo, resCosto);
                        detenerCarga(lt3);
                        System.out.println("\nNivel de la solución: " + n.nivel);
                        System.out.println("Nodos expandidos: " + arbol.getNodosExpandidos());
                        System.out.printf("Tiempo de ejecución: %.3f ms%n", arbol.getTiempoEjecucion());
                    } catch (OutOfMemoryError e) {
                        detenerCarga(lt3);
                        System.out.println("\nError: Memoria insuficiente.");
                        System.out.println("Nodos expandidos hasta el error: " + arbol.getNodosExpandidos());
                        System.out.printf("Tiempo hasta el error: %.3f ms%n",
                                (System.nanoTime() - inicio3) / 1_000_000.0);
                    }
                    System.out.println("-------------------\n");
                    break;
                case 4:
                    System.out.println("\n--- Búsqueda IDA (Iterative Deepening A*) ---\n");
                    System.out.println(
                            "1. Diferencia absoluta\n2. Diferencia de bordes\n3. Distancia Manhattan\n4. Distancia Manhattan con penalización\n");
                    System.out.print("Indique método de cálculo de costo: ");
                    resCosto = sc.nextInt();
                    Thread lt4 = iniciarCarga();
                    long inicio4 = System.nanoTime();
                    try {
                        n = arbol.busquedaIDA(estadoObjetivo, resCosto);
                        detenerCarga(lt4);
                        System.out.println("\nNivel de la solución: " + n.nivel);
                        System.out.println("Nodos expandidos: " + arbol.getNodosExpandidos());
                        System.out.printf("Tiempo de ejecución: %.3f ms%n", arbol.getTiempoEjecucion());
                    } catch (OutOfMemoryError e) {
                        detenerCarga(lt4);
                        System.out.println("\nError: Memoria insuficiente.");
                        System.out.println("Nodos expandidos hasta el error: " + arbol.getNodosExpandidos());
                        System.out.printf("Tiempo hasta el error: %.3f ms%n",
                                (System.nanoTime() - inicio4) / 1_000_000.0);
                    }
                    System.out.println("-------------------\n");
                    break;
                default:
                    System.out.println("Opción inválida\n");
                    break;
            }
        }
    }
}
