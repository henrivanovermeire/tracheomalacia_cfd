import slicer
import vtk
import json
import numpy as np
import os


# ============================================================
# Configuration
# ============================================================

PLANE_SIZE = 50.0       # mm
PLANE_OPACITY = 0.5

PROJECT_DIR = "/home/hvoverme/tracheomalacia_cfd/segmentation"

JSON_FILE = os.path.join(
    PROJECT_DIR,
    "assets",
    "airway_cut_planes.json"
)


# ============================================================
# Print configuration
# ============================================================

print("")
print("========================================")
print("Loading bronchus cut planes")
print("========================================")
print(f"Project directory: {PROJECT_DIR}")
print(f"JSON file        : {JSON_FILE}")
print("")


# ============================================================
# Check JSON exists
# ============================================================

if not os.path.isfile(JSON_FILE):
    raise FileNotFoundError(
        f"Could not find JSON file:\n{JSON_FILE}"
    )


# ============================================================
# Load JSON
# ============================================================

with open(JSON_FILE, "r") as f:
    planes_data = json.load(f)

print(
    f"Found {len(planes_data)} plane(s):"
)

for name in planes_data:
    print(f"  - {name}")

print("")


# ============================================================
# Helper: normalize vector
# ============================================================

def normalize(vector):

    vector = np.asarray(
        vector,
        dtype=float
    )

    length = np.linalg.norm(vector)

    if length < 1e-12:
        raise ValueError(
            "Cannot normalize zero-length vector."
        )

    return vector / length


# ============================================================
# Create one interactive Markups Plane
# ============================================================

def create_markups_plane(
        name,
        origin_ras,
        normal_ras,
        size=50.0):

    print("")
    print(f"Creating plane: {name}")

    # --------------------------------------------------------
    # Convert JSON values to numpy arrays
    # --------------------------------------------------------

    origin = np.asarray(
        origin_ras,
        dtype=float
    )

    normal = normalize(
        normal_ras
    )

    print(
        f"  Origin RAS: "
        f"[{origin[0]:.6f}, "
        f"{origin[1]:.6f}, "
        f"{origin[2]:.6f}]"
    )

    print(
        f"  Normal RAS: "
        f"[{normal[0]:.6f}, "
        f"{normal[1]:.6f}, "
        f"{normal[2]:.6f}]"
    )

    # --------------------------------------------------------
    # Create Markups Plane node
    # --------------------------------------------------------

    plane = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLMarkupsPlaneNode",
        name
    )

    # --------------------------------------------------------
    # Set the plane center
    #
    # This is the origin_RAS from the JSON.
    # --------------------------------------------------------

    plane.SetCenter(
        float(origin[0]),
        float(origin[1]),
        float(origin[2])
    )

    # --------------------------------------------------------
    # Set the plane normal
    #
    # This is the normal_RAS from the JSON.
    # --------------------------------------------------------

    plane.SetNormal(
        float(normal[0]),
        float(normal[1]),
        float(normal[2])
    )

    # --------------------------------------------------------
    # Set plane size
    # --------------------------------------------------------

    plane.SetSize(
        float(size),
        float(size)
    )

    # --------------------------------------------------------
    # Display settings
    # --------------------------------------------------------

    display_node = plane.GetDisplayNode()

    if display_node:

        display_node.SetVisibility(
            True
        )

        display_node.SetOpacity(
            float(PLANE_OPACITY)
        )

        # Orange
        display_node.SetSelectedColor(
            1.0,
            0.5,
            0.0
        )

    # --------------------------------------------------------
    # Store original JSON information
    # --------------------------------------------------------

    plane.SetAttribute(
        "OriginRAS",
        ",".join(
            str(float(x))
            for x in origin
        )
    )

    plane.SetAttribute(
        "NormalRAS",
        ",".join(
            str(float(x))
            for x in normal
        )
    )

    plane.SetAttribute(
        "SourceJSON",
        JSON_FILE
    )

    # --------------------------------------------------------
    # Verify what Slicer actually stored
    # --------------------------------------------------------

    stored_center = [0.0, 0.0, 0.0]
    stored_normal = [0.0, 0.0, 0.0]

    plane.GetCenter(
        stored_center
    )

    plane.GetNormal(
        stored_normal
    )

    print(
        f"  Stored center: "
        f"[{stored_center[0]:.6f}, "
        f"{stored_center[1]:.6f}, "
        f"{stored_center[2]:.6f}]"
    )

    print(
        f"  Stored normal: "
        f"[{stored_normal[0]:.6f}, "
        f"{stored_normal[1]:.6f}, "
        f"{stored_normal[2]:.6f}]"
    )

    print(
        "  Created successfully."
    )

    return plane


# ============================================================
# Remove previously created planes
#
# This prevents duplicates when the script is run repeatedly.
# ============================================================

plane_names = set(
    planes_data.keys()
)

nodes_to_remove = []

for node in slicer.util.getNodesByClass(
        "vtkMRMLMarkupsPlaneNode"):

    if node.GetName() in plane_names:

        nodes_to_remove.append(
            node
        )


for node in nodes_to_remove:

    print(
        f"Removing existing plane: "
        f"{node.GetName()}"
    )

    slicer.mrmlScene.RemoveNode(
        node
    )


# ============================================================
# Create planes
# ============================================================

created_planes = []

for name, data in planes_data.items():

    # --------------------------------------------------------
    # Validate JSON
    # --------------------------------------------------------

    if "origin_RAS" not in data:

        print(
            f"WARNING: {name} has no "
            f"origin_RAS. Skipping."
        )

        continue

    if "normal_RAS" not in data:

        print(
            f"WARNING: {name} has no "
            f"normal_RAS. Skipping."
        )

        continue

    # --------------------------------------------------------
    # Create plane
    # --------------------------------------------------------

    try:

        plane = create_markups_plane(
            name=name,
            origin_ras=data["origin_RAS"],
            normal_ras=data["normal_RAS"],
            size=PLANE_SIZE
        )

        created_planes.append(
            plane
        )

    except Exception as e:

        print(
            f"ERROR creating {name}: {e}"
        )


# ============================================================
# Summary
# ============================================================

print("")
print("========================================")
print("Finished")
print("========================================")

print(
    f"Created {len(created_planes)} "
    f"interactive plane(s)."
)

for plane in created_planes:

    print(
        f"  - {plane.GetName()}"
    )

print("")
print(
    "The planes are "
    "vtkMRMLMarkupsPlaneNode objects."
)

print(
    "Their centers and normals are taken "
    "directly from the JSON RAS coordinates."
)

print(
    "Use the Markups interaction handles to "
    "move, rotate, and resize them."
)

print("")

