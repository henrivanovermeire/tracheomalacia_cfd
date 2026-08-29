Merge "airways.stl";

angle = 40;

ClassifySurfaces{
    angle * Pi/180,
    1,
    1,
    180 * Pi/180
};

CreateGeometry;

// Force a substantially finer surface remesh
Mesh.MeshSizeMin = 0.5;
Mesh.MeshSizeMax = 0.5;

Surface Loop(1) = Surface{:};
Volume(1) = {1};

Physical Volume("fluid") = {1};

Mesh.Algorithm3D = 1;
