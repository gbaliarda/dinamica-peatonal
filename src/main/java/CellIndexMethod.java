import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class CellIndexMethod {
    private final Map<Long, List<Particle>> map;
    private final int cellAmount;
    private final double mapLength;
    private final double interactionRadius;
    private final boolean isPeriodic;

    /*
    * L: square board size
    * isPeriodic: whether or not to use periodic boundary conditions
     */
    public CellIndexMethod(List<Particle> particles, double L, boolean isPeriodic) {
        this.map = new HashMap<>(); // cell id to list of particles on the cell index method
        this.cellAmount = (int) Math.floor(L-1); // optimal M for cell index method
        this.mapLength = L;
        this.interactionRadius = 0; // unitary radius
        this.isPeriodic = isPeriodic;
        double cellSize = (double)L/cellAmount; // cells not used in the simulation, but for the method of computing neighbours
        // assign each particle to a cell on the CIM
        particles.forEach((p) -> {
            long xCellNumber = (long)(p.getX() / cellSize) + 1; // column
            long yCellNumber = (long)(p.getY() / cellSize); // row
            long cellNumber = xCellNumber + yCellNumber * cellAmount; // cell ID
            map.putIfAbsent(cellNumber, new LinkedList<>());
            map.get(cellNumber).add(p.copy()); // create a copy of the particles
        });
    }

    public Map<Particle, List<Particle>> computeNeighbourhoods() {
        Map<Particle, List<Particle>> neighbours = new HashMap<>();
        for (int x = 1; x <= cellAmount; x++) {
            for (int y = 0 ; y < cellAmount; y++) {
                long currentCell = x + y * cellAmount;
                addNeighboursBetweenCells(neighbours, currentCell, currentCell);
                if (y > 0 || isPeriodic) {
                    long northCell = y > 0 ? x + (y - 1) * cellAmount : x + (cellAmount - 1) * cellAmount;
                    addNeighboursBetweenCells(neighbours, currentCell, northCell);
                }
                if (x < cellAmount || isPeriodic) {
                    long eastCell = ((x + 1) % cellAmount) + y * cellAmount;
                    long northEastCell = y > 0 ? ((x + 1) % cellAmount) + (y - 1) * cellAmount : ((x + 1) % cellAmount) + (cellAmount - 1) * cellAmount;
                    long southEastCell = y < cellAmount - 1 ? ((x + 1) % cellAmount) + (y + 1) * cellAmount : (x + 1) % cellAmount;
                    addNeighboursBetweenCells(neighbours, currentCell, eastCell);
                    if (y > 0 || isPeriodic)
                        addNeighboursBetweenCells(neighbours, currentCell, northEastCell);
                    if (y < cellAmount - 1 || isPeriodic)
                        addNeighboursBetweenCells(neighbours, currentCell, southEastCell);
                }
            }
        }
        return neighbours;
    }

    // Calculate euclidean distance between 2 particles
    private double calculateDistance(Particle p1, Particle p2) {
        double xDistance = Math.abs(p2.getX() - p1.getX());
        double yDistance = Math.abs(p2.getY() - p1.getY());

        if (isPeriodic) {
            if (xDistance * 2 > mapLength)
                xDistance = mapLength - xDistance;
            if (yDistance * 2 > mapLength)
                yDistance = mapLength - yDistance;
        }
        return Math.sqrt(xDistance*xDistance + yDistance*yDistance) - p1.getRadius() - p2.getRadius();
    }

    private boolean particlesAreNeighbours(Particle p1, Particle p2) {
        return !p1.equals(p2) && calculateDistance(p1, p2) <= interactionRadius;
    }

    // Given a `currentCell` and `otherCell` (could be the same), compute all neighborhoods between their particles and add them to `neighbours`
    private void addNeighboursBetweenCells(Map<Particle, List<Particle>> neighbours, long currentCell, long otherCell) {
        if (!map.containsKey(currentCell) || !map.containsKey(otherCell))
            return;
        map.get(currentCell).forEach((currentParticle) -> {
            map.get(otherCell).forEach((otherParticle) -> {
                if (particlesAreNeighbours(currentParticle, otherParticle)) {
                    neighbours.putIfAbsent(currentParticle, new LinkedList<>());
                    neighbours.get(currentParticle).add(otherParticle);
                    if (currentCell != otherCell) {
                        neighbours.putIfAbsent(otherParticle, new LinkedList<>());
                        neighbours.get(otherParticle).add(currentParticle);
                    }
                }
            });
        });
    }
}
