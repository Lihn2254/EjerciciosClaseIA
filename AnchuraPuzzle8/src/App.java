public class App {
    public static void main(String[] args) throws Exception {
        Arbol arbol = new Arbol(new Nodo("_12345678"));
        Nodo n = arbol.busquedaxAnchura("12345678_");
        System.out.println("\nNivel de la solución: " + n.nivel);
    }
}
