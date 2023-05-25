import com.moandjiezana.toml.Toml;

import java.io.File;

public class Config {
    private static long boxLength;
    private static double exitWidth;
    private static long pedestrians;
    private static double minRadius, maxRadius, vdMax;
    private static double beta;
    private static String staticFile, outputFile;
    private static double dtSimulation;
    private static long outputInterval;

    static {
        try {
            Toml toml = new Toml().read(new File("config.toml"));

            boxLength = toml.getLong("simulation.boxLength");
            exitWidth = toml.getDouble("simulation.exitWidth");
            pedestrians = toml.getLong("simulation.pedestrians");
            minRadius = toml.getDouble("simulation.minRadius");
            maxRadius = toml.getDouble("simulation.maxRadius");
            vdMax = toml.getDouble("simulation.vdMax");
            beta = toml.getDouble("simulation.beta");
            dtSimulation = toml.getDouble("simulation.dtSimulation");
            outputInterval = toml.getLong("simulation.outputInterval");
            staticFile = toml.getString("files.staticFile");
            outputFile = toml.getString("files.outputFile");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static long getBoxLength() {
        return boxLength;
    }

    public static double getExitWidth() {
        return exitWidth;
    }

    public static long getPedestrians() {
        return pedestrians;
    }

    public static double getMinRadius() {
        return minRadius;
    }

    public static double getMaxRadius() {
        return maxRadius;
    }

    public static double getVdMax() {
        return vdMax;
    }

    public static double getBeta() {
        return beta;
    }

    public static double getDtSimulation() {
        return dtSimulation;
    }

    public static long getOutputInterval() {
        return outputInterval;
    }

    public static String getStaticFile() {
        return staticFile;
    }

    public static String getOutputFile() {
        return outputFile;
    }
}
