Merge "/home/hvoverme/tracheomalacia_cfd/meshes/postop/airways.stl";

angle = 40;

ClassifySurfaces{
    angle * Pi/180,
    1,
    1,
    180 * Pi/180
};

CreateGeometry;

// --------------------
// Boundary groups
// --------------------

// Cap elementary-surface IDs for this airway geometry.
inlet[]   = {25}; // tracheal inlet
outlet1[] = {23}; // right superior lobar bronchus
outlet2[] = {24}; // right inferior lobar bronchus
outlet3[] = {22}; // left main bronchus

all[] = Surface{:};

caps[] = {
    inlet[],
    outlet1[],
    outlet2[],
    outlet3[]
};

wall[] = all[];
wall[] -= {caps[]};

Physical Surface("inlet")    = {inlet[]};
Physical Surface("outlet_1") = {outlet1[]};
Physical Surface("outlet_2") = {outlet2[]};
Physical Surface("outlet_3") = {outlet3[]};
Physical Surface("wall")     = {wall[]};

// --------------------
// Fluid volume
// --------------------

Surface Loop(1) = Surface{:};
Volume(1) = {1};

Physical Volume("fluid") = {1};

// --------------------
// Mesh parameter
// --------------------

DefineConstant[
    lc = {0.5, Name "Parameters/Mesh size"}
];

Mesh.MeshSizeMin = lc;
Mesh.MeshSizeMax = lc;

Mesh.Algorithm3D = 10;
Mesh.OptimizeNetgen = 1;
Mesh.Optimize = 1;
