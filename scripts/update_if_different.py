import argparse
import sys
import shutil
import pymeshlab as ml
from change_3mf_title import change_3mf_title
import tempfile
import os
from pathlib import Path



def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Calculate Hausdorff Distance between two meshes."
    )

    # Define required positional arguments
    parser.add_argument(
        "sample_mesh", type=str, help="Path to the sample mesh file"
    )
    parser.add_argument(
        "target_mesh", type=str, help="Path to the target mesh file"
    )

    # Define optional argument for tolerance threshold
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.001,
        help="Mean distance error threshold (default: 0.001)",
    )

    # Define optional argument for title threshold
    parser.add_argument(
        "--title",
        type=str,
        default="",
        help="The title to update in the file",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Initialize MeshLab
    ms = ml.MeshSet()

    temp_mesh_path = ""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use .3mf or .4mf depending on your target format spec
        temp_mesh_path = os.path.join(tmpdir, "mesh.3mf") 
        
        # Create a symbolic link pointing to your .tmp file
        shutil.move(os.path.abspath(args.sample_mesh), temp_mesh_path)
        
        # 2. PyMeshLab can now safely parse it based on the extension
        try:
            ms.load_new_mesh(temp_mesh_path)
        except ml.PyMeshLabException as e:
            print(f"Error loading meshes: {e}", file=sys.stderr)
            sys.exit(2)
        
        skipTest = False
        try:
            ms.load_new_mesh(args.target_mesh)  # Index 0
        except ml.PyMeshLabException as e:
            skipTest = True
            print(f"Not loading {args.target_mesh}")


        # Calculate Hausdorff Distance (geometric deviation)
        res = {}
        if skipTest:
            res = {"max": 0, "mean": 10}
        else:
            res = ms.get_hausdorff_distance(sampledmesh=0, targetmesh=1)

        # Throw error if models deviate beyond the tolerance threshold
        if res["mean"] > args.tolerance:
            print(
                f"Overwrite: Mean distance {res['mean']} exceeds tolerance {args.tolerance}",
                file=sys.stderr,
            )
            # Copy the file and delete the tmp file.
            shutil.move(temp_mesh_path, args.target_mesh)

            # If the title is passed in, update the title.
            if args.title != "":
                change_3mf_title(args.target_mesh, args.title)

            sys.exit(0)
        else:
            print( f"Skip: Mean distance {res['mean']} is within tolerance {args.tolerance}")
            Path.touch(args.target_mesh)           
            sys.exit(0)


if __name__ == "__main__":
    main()