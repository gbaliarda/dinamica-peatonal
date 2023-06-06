import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class PedestrianSystem {
    private List<Particle> particles;
    private double time;
    private final double dt;
    private int particlesOutside;
    private long amountCollisions;

    public PedestrianSystem(List<Particle> particles) {
        this.particles = particles;
        Particle sample = particles.get(0);
        this.time = 0;
        this.particlesOutside = 0;
        this.amountCollisions = 0;
        this.dt = sample.getMinRadius() / (2*sample.getVdMax()); // s
    }

    enum Walls {
        LEFT(new double[]{1, 0}),
        RIGHT(new double[]{-1, 0}),
        TOP(new double[]{0, -1}),
        BOTTOM(new double[]{0, 1});

        private final double[] direction;

        Walls(double[] direction) {
            this.direction = direction;
        }

        public double[] getDirection() {
            return this.direction;
        }
    }

    // Updates particles and returns the amount of particles that left the simulation during the current time step
    public int nextStep() {
        // Check contact between particles
        CellIndexMethod cim = new CellIndexMethod(particles, Config.getBoxLength(), false);
        Map<Particle, List<Particle>> particlesInContact = cim.computeNeighbourhoods();
        long newAmountCollisions = 0;
        for (Map.Entry<Particle, List<Particle>> entry : particlesInContact.entrySet()) {
            newAmountCollisions += entry.getValue().size();
        }
        amountCollisions += newAmountCollisions / 2;

        // Check contact between particles and walls
        Map<Particle, List<Walls>> wallsInContact = new HashMap<>();
        for (Particle p : particles) {
            List<Walls> walls = p.getWallsInContact();
            if (walls.size() > 0)
                wallsInContact.put(p, walls);
            amountCollisions += walls.size();
        }

        for (Particle p : particles) {
            boolean isParticleInContact = particlesInContact.containsKey(p) || wallsInContact.containsKey(p);

            // Update particles radius
            p.updateRadius(dt, isParticleInContact);

            // Update particles velocities
            p.updateVelocity(isParticleInContact);
        }

        // Update particles positions
        for (Particle p: particles) {
            boolean wentThroughExit = p.updatePosition(
                dt,
                particlesInContact.getOrDefault(p, Collections.emptyList()),
                wallsInContact.getOrDefault(p, Collections.emptyList())
            );
            if (wentThroughExit) particlesOutside++;
        }

        // Remove particles that exit the room
        int previousSize = particles.size();
        particles = particles.stream().filter(particle -> !particle.isOutsideSimulation()).collect(Collectors.toList());

        this.time += dt;

        // Return the amount of particles that exited the room in this time step
        return previousSize - particles.size();
    }

    public boolean hasNextStep() {
        return particles.size() > 0;
    }

    public List<Particle> getParticles() {
        return particles;
    }

    public double getTime() {
        return time;
    }

    public int getParticlesOutside() { return particlesOutside; }

    public long getAmountCollisions() { return amountCollisions; }
}
