Merge "airways.stl";

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

// Replace these with the cap IDs you identify once
inlet[]  = {30};
outlet1[] = {27};
outlet2[] = {28};
outlet3[] = {29};

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

Mesh.Algorithm3D = 1;
Mesh.Optimize = 1;
