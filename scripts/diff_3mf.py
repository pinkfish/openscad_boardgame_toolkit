import pymeshlab as ml
import sys

ms = ml.MeshSet()  # pyright: ignore[reportAttributeAccessIssue] -- present at runtime, missing from the compiled module's stubs
ms.load_new_mesh(sys.argv[1]) # Target mesh
ms.load_new_mesh(sys.argv[2]) # Sample mesh

# Calculate Hausdorff Distance (geometric deviation)
res = ms.get_hausdorff_distance(sampledmesh=1, targetmesh=0)
print(f"Max Distance: {res['max']}")
print(f"Mean Distance: {res['mean']}")

# Throw error if models deviate beyond a tolerance threshold (e.g., 0.01mm)
if res['mean'] > 0.01:
    sys.exit(1)