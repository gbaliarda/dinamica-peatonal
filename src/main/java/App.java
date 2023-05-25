import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.stream.Stream;

public class App {
    public static void main( String[] args ) throws IOException {
        Path filePath = Paths.get(Config.getOutputFile());
        // Create any non-existent directories in the output path
        Files.createDirectories(filePath.getParent());
        // Delete old output file
        Files.deleteIfExists(filePath);

        File file = new File(Config.getOutputFile());
        FileWriter outputWriter = new FileWriter(file, true);

        List<Particle> particles = parseParticles();
        System.out.println(particles.size());

        PedestrianSystem pedestrianSystem = new PedestrianSystem(particles);
        int timeSteps = 0;

        // Run the simulation
        while (pedestrianSystem.hasNextStep()) {
            pedestrianSystem.nextStep();

            if (timeSteps++ % Config.getOutputInterval() == 0) {
                StringBuilder stringBuilder = new StringBuilder();
                stringBuilder.append(pedestrianSystem.getTime()).append("\n");
                pedestrianSystem.getParticles().forEach(particle -> stringBuilder.append(String.format(Locale.US, "%f %f %f %f\n", particle.getX(), particle.getY(), particle.getV(), particle.getRadius())));

                outputWriter.write(stringBuilder.toString());
            }
        }
    }

    static List<Particle> parseParticles() throws IOException {
        List<Particle> particles = new ArrayList<>();

        Stream<String> stream = Files.lines(Paths.get(Config.getStaticFile()));

        // Load static inputs
        stream.forEach(line -> {
            String[] values = line.split(" ");
            double[] doubles = new double[values.length];
            for (int i = 0; i < values.length; i++)
                doubles[i] = Double.parseDouble(values[i]);
            double x = doubles[0];
            double y = doubles[1];
            double minRadius = Config.getMinRadius();
            double maxRadius = Config.getMaxRadius();
            double vdMax = Config.getVdMax();
            double beta = Config.getBeta();
            Particle p = new Particle(minRadius, maxRadius, minRadius, 0, vdMax, x, y, beta);
            particles.add(p);
        });

        return particles;
    }
}
