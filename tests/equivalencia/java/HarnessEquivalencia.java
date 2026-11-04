import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import principal.ComparaRegistros;

/** Uma chamada por JVM; o chamador deve definir cwd para a pasta das tabelas. */
public final class HarnessEquivalencia {
    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            throw new IllegalArgumentException("Uso: HarnessEquivalencia pares.csv frequencias saida_sem_extensao");
        }
        Path entrada = Path.of(args[0]).toRealPath();
        Path frequencias = Path.of(args[1]).toRealPath();
        if (!Path.of("").toRealPath().equals(frequencias)) {
            throw new IllegalArgumentException("Execute a JVM com cwd igual ao diretorio das seis tabelas");
        }
        // DecimalFormat e minusculas nao devem depender da localidade da maquina.
        Locale.setDefault(Locale.ROOT);
        Path saida = Path.of(args[2]).toAbsolutePath();
        ComparaRegistros.inicia(entrada.toString(), saida.toString(), 0, 1, 2, 3, 4, 5);
        // inicia captura IOException internamente: nao aceitar sucesso sem artefato.
        if (!Files.isRegularFile(Path.of(saida + ".csv"))) {
            throw new IllegalStateException("O legado nao produziu o CSV esperado");
        }
    }
}
