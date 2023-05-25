import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class Particle {
    private double minRadius, maxRadius, radius;
    private double v, vdMax;
    private double x, y;
    private double beta;

    public Particle(double minRadius, double maxRadius, double radius, double v, double vdMax, double x, double y, double beta) {
        this.minRadius = minRadius;
        this.maxRadius = maxRadius;
        this.radius = radius;
        this.v = v;
        this.vdMax = vdMax;
        this.x = x;
        this.y = y;
        this.beta = beta;
    }

    public Particle copy() {
        return new Particle(this.minRadius, this.maxRadius, this.radius, this.v, this.vdMax, this.x, this.y, this.beta);
    }

    public List<PedestrianSystem.Walls> getWallsInContact() {
        List<PedestrianSystem.Walls> walls = new ArrayList<>();

        // Vertical walls
        if (x - radius <= 0)
            walls.add(PedestrianSystem.Walls.LEFT);
        else if (x + radius >= Config.getBoxLength())
            walls.add(PedestrianSystem.Walls.RIGHT);

        double L = Config.getExitWidth();
        double[] xExit = new double[]{Config.getBoxLength() / 2.0 - L / 2, Config.getBoxLength() / 2.0 + L / 2};

        // Horizontal walls
        if (y - radius <= 0 && (x - radius < xExit[0] || x + radius > xExit[1])) // take the exit into account
            walls.add(PedestrianSystem.Walls.BOTTOM);
        else if (y + radius >= Config.getBoxLength())
            walls.add(PedestrianSystem.Walls.TOP);

        return walls;
    }

    public void updateRadius(double dt, boolean isInContact) {
        if (isInContact)
            radius = minRadius;
        else if (radius < maxRadius) {
            // tau=0.5s => time taken for a particle to reach its maximum radius and thus its maximum velocity.
            radius += maxRadius / (0.5 / dt);

            if (radius > maxRadius) radius = maxRadius;
        }
    }

    public void updateVelocity(boolean isInContact) {
        if (isInContact)
            v = vdMax; // ve (escape velocity)
        else
            v = vdMax * Math.pow(((radius - minRadius) / (maxRadius - minRadius)), beta);
    }

    public void updatePosition(double dt, List<Particle> particlesInContact, List<PedestrianSystem.Walls> wallsInContact) {
        double[] escapeDirection = new double[]{0, 0};

        boolean isParticleInContact = particlesInContact.size() > 0 || wallsInContact.size() > 0;
        if (isParticleInContact) {
            for (Particle o : particlesInContact) {
                double[] escapeDirectionFromParticle = getEscapeDirection(o);
                escapeDirection[0] += escapeDirectionFromParticle[0];
                escapeDirection[1] += escapeDirectionFromParticle[1];
            }

            for (PedestrianSystem.Walls wall : wallsInContact) {
                double[] escapeDirectionFromWall = wall.getDirection();
                escapeDirection[0] += escapeDirectionFromWall[0];
                escapeDirection[1] += escapeDirectionFromWall[1];
            }
        } else {
            double L = Config.getExitWidth();
            // Exit is in the center of the bottom wall
            double[] xExit = new double[]{Config.getBoxLength() / 2.0 - L / 2, Config.getBoxLength() / 2.0 + L / 2};
            double xTarget;

            double[] decisionInterval = new double[]{xExit[0] + 0.2*L, xExit[0] + 0.8*L};
            if (x < decisionInterval[0] || x > decisionInterval[1]) {
                xTarget = decisionInterval[0] + Math.random() * (decisionInterval[1] - decisionInterval[0]);
            } else {
                xTarget = x;
            }

            double module = Math.sqrt(Math.pow(x - xTarget, 2) + Math.pow(y - 0, 2)); // yTarget = 0
            escapeDirection = new double[]{(xTarget - x)/module, (0 - y)/module};
        }

        double direction = Math.atan2(escapeDirection[1], escapeDirection[0]);
        double vx = v * Math.cos(direction);
        double vy = v * Math.sin(direction);

        x += vx * dt;
        y += vy * dt;
    }

    private double[] getEscapeDirection(Particle o) {
        // [x, y] - [o.x, o.y] = [x - o.x, y - o.y]
        // eij = [x - o.x, y - o.y] / sqrt((x-o.x)**2 + (y-o.y)**2)
        double module = Math.sqrt(Math.pow(x - o.x, 2) + Math.pow(y - o.y, 2));
        return new double[]{(x - o.x)/module, (y - o.y)/module}; // eij
    }

    public boolean isOutside() {
        double L = Config.getExitWidth();
        double[] xExit = new double[]{Config.getBoxLength() / 2.0 - L / 2, Config.getBoxLength() / 2.0 + L / 2};
        return (
            y - radius <= 0 &&
            x - radius >= xExit[0] &&
            x + radius <= xExit[1]
        );
    }

    public double getMinRadius() {
        return minRadius;
    }

    public double getRadius() {
        return radius;
    }

    public double getV() {
        return v;
    }

    public double getVdMax() {
        return vdMax;
    }

    public double getX() {
        return x;
    }

    public double getY() {
        return y;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Particle particle = (Particle) o;
        return Double.compare(particle.x, x) == 0 && Double.compare(particle.y, y) == 0;
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }
}
