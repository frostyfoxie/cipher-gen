from flask import Flask, render_template, request
import itertools
import random
import matplotlib.pyplot as plt
import os

# Tell Flask that templates are in the root folder
app = Flask(__name__, template_folder='.')

# Make folder for plots if it doesn't exist
if not os.path.exists("static/plots"):
    os.makedirs("static/plots")

# -----------------------------
# Polygon and centroid functions (same as before)
# -----------------------------
def generate_polygon(n, radius=5000, seed=0):
    random.seed(seed)
    return [(random.uniform(-radius, radius), random.uniform(-radius, radius)) for _ in range(n)]

def triangle_centroid(triangle):
    (x1, y1), (x2, y2), (x3, y3) = triangle
    return ((x1+x2+x3)/3, (y1+y2+y3)/3)

def generate_triangles(points):
    return list(itertools.combinations(points, 3))

def sample_triangles(triangles, max_sample=600):
    if len(triangles) <= max_sample:
        return triangles
    return random.sample(triangles, max_sample)

def level2_centroids(n, m):
    polygon = generate_polygon(n, seed=m)
    triangles_lvl1 = generate_triangles(polygon)
    centroids_lvl1 = [triangle_centroid(tri) for tri in triangles_lvl1]
    triangles_lvl2 = generate_triangles(centroids_lvl1)
    centroids_lvl2 = [triangle_centroid(tri) for tri in triangles_lvl2]
    return polygon, centroids_lvl2, triangles_lvl2

def get_numeric_password(n, m, k):
    polygon, centroids_lvl2, triangles_lvl2 = level2_centroids(n, m)
    triangles_lvl2_sample = sample_triangles(triangles_lvl2, max_sample=600)
    
    # Plot
    plt.figure(figsize=(8,8))
    poly_x, poly_y = zip(*polygon)
    plt.plot(list(poly_x)+[poly_x[0]], list(poly_y)+[poly_y[0]], 'b-', lw=2, label="Polygon")
    
    for tri in triangles_lvl2_sample:
        x, y = zip(*tri)
        plt.plot(list(x)+[x[0]], list(y)+[y[0]], 'm-', alpha=0.2)
    
    cx, cy = zip(*centroids_lvl2)
    plt.scatter(cx, cy, c='orange', s=25, label="Level 2 Centroids")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.legend()
    
    plot_path = f"static/plots/plot_{n}_{m}_{k}.png"
    plt.savefig(plot_path)
    plt.close()
    
    if k < 1 or k > len(centroids_lvl2):
        raise ValueError(f"k must be between 1 and {len(centroids_lvl2)}")
    
    x, y = centroids_lvl2[k-1]
    total = x + y
    password = int(str(total).replace('.', '').replace('-', ''))
    
    return password, plot_path

# -----------------------------
# Flask route
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    password = None
    plot_path = None
    if request.method == "POST":
        try:
            n = int(request.form.get("n"))
            m = int(request.form.get("m"))
            k = int(request.form.get("k"))
            password, plot_path = get_numeric_password(n, m, k)
        except Exception as e:
            password = f"Error: {e}"
    return render_template("index.html", password=password, plot_path=plot_path)

if __name__ == "__main__":
    app.run(debug=True)
def get_numeric_password(n, m, k):
    polygon, centroids_lvl2, triangles_lvl2 = level2_centroids(n, m)
    triangles_lvl2_sample = sample_triangles(triangles_lvl2, max_sample=600)
    
    # Plot
    plt.figure(figsize=(8,8))
    poly_x, poly_y = zip(*polygon)
    plt.plot(list(poly_x)+[poly_x[0]], list(poly_y)+[poly_y[0]], 'b-', lw=2, label="Polygon")
    
    for tri in triangles_lvl2_sample:
        x, y = zip(*tri)
        plt.plot(list(x)+[x[0]], list(y)+[y[0]], 'm-', alpha=0.2)
    
    cx, cy = zip(*centroids_lvl2)
    plt.scatter(cx, cy, c='orange', s=25, label="Level 2 Centroids")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.legend()
    
    plot_path = f"static/plots/plot_{n}_{m}_{k}.png"
    plt.savefig(plot_path)
    plt.close()
    
    if k < 1 or k > len(centroids_lvl2):
        raise ValueError(f"k must be between 1 and {len(centroids_lvl2)}")
    
    x, y = centroids_lvl2[k-1]
    total = x + y
    password = int(str(total).replace('.', '').replace('-', ''))
    
    return password, plot_path

# -----------------------------
# Flask routes
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    password = None
    plot_path = None
    if request.method == "POST":
        try:
            n = int(request.form.get("n"))
            m = int(request.form.get("m"))
            k = int(request.form.get("k"))
            password, plot_path = get_numeric_password(n, m, k)
        except Exception as e:
            password = f"Error: {e}"
    return render_template("index.html", password=password, plot_path=plot_path)

if __name__ == "__main__":
    app.run(debug=True)
