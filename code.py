import itertools
import random
import matplotlib.pyplot as plt

# -----------------------------
# Step 1: Generate polygon deterministically
# -----------------------------
def generate_polygon(n, radius=5000, seed=0):
    random.seed(seed)
    return [(random.uniform(-radius, radius), random.uniform(-radius, radius)) for _ in range(n)]

# -----------------------------
# Step 2: Compute centroid of a triangle
# -----------------------------
def triangle_centroid(triangle):
    (x1, y1), (x2, y2), (x3, y3) = triangle
    return ((x1 + x2 + x3)/3, (y1 + y2 + y3)/3)

# -----------------------------
# Step 3: Generate all triangles
# -----------------------------
def generate_triangles(points):
    return list(itertools.combinations(points, 3))

# -----------------------------
# Step 4: Sample triangles for plotting
# -----------------------------
def sample_triangles(triangles, max_sample=600):
    if len(triangles) <= max_sample:
        return triangles
    return random.sample(triangles, max_sample)

# -----------------------------
# Step 5: Compute level-2 centroids
# -----------------------------
def level2_centroids(n, m):
    polygon = generate_polygon(n, seed=m)
    triangles_lvl1 = generate_triangles(polygon)
    centroids_lvl1 = [triangle_centroid(tri) for tri in triangles_lvl1]
    triangles_lvl2 = generate_triangles(centroids_lvl1)
    centroids_lvl2 = [triangle_centroid(tri) for tri in triangles_lvl2]
    return polygon, centroids_lvl2, triangles_lvl2

# -----------------------------
# Step 6: Plot polygon + centroids + triangles
# -----------------------------
def plot_structure(polygon, centroids_lvl2, triangles_lvl2_sample):
    plt.figure(figsize=(10,10))
    
    # Polygon edges
    poly_x, poly_y = zip(*polygon)
    plt.plot(list(poly_x)+[poly_x[0]], list(poly_y)+[poly_y[0]], 'b-', lw=2, label="Polygon")
    
    # Sampled level-2 triangles
    for tri in triangles_lvl2_sample:
        x, y = zip(*tri)
        plt.plot(list(x)+[x[0]], list(y)+[y[0]], 'm-', alpha=0.2)
    
    # Level-2 centroids
    cx, cy = zip(*centroids_lvl2)
    plt.scatter(cx, cy, c='orange', s=25, label="Level 2 Centroids")
    
    plt.gca().set_aspect("equal", adjustable="box")
    plt.legend()
    plt.title("Polygon + Level 2 Centroids + Sampled Level 2 Triangles")
    plt.show()

# -----------------------------
# Step 7: Get numeric password from k-th centroid
# -----------------------------
def get_numeric_password(n, m, k):
    polygon, centroids_lvl2, triangles_lvl2 = level2_centroids(n, m)
    triangles_lvl2_sample = sample_triangles(triangles_lvl2, max_sample=600)
    
    # Plot everything
    plot_structure(polygon, centroids_lvl2, triangles_lvl2_sample)
    
    if k < 1 or k > len(centroids_lvl2):
        raise ValueError(f"k must be between 1 and {len(centroids_lvl2)}")
    
    x, y = centroids_lvl2[k-1]
    total = x + y
    # Convert to integer password by removing decimal point and minus sign
    password = int(str(total).replace('.', '').replace('-', ''))
    return password

# -----------------------------
# Usage
# -----------------------------
if __name__ == "__main__":
    print("Enter the number of polygon sides (n):")
    n = int(input())
    
    print("Enter the seed value (m):")
    m = int(input())
    
    print("Enter the index of the centroid to select (k):")
    k = int(input())
    
    password = get_numeric_password(n, m, k)
    print(f"The numeric password for (n={n}, m={m}, k={k}) is: {password}")
