bl_info = {
    "name": "Homogeneous Sphere",
    "description": "Add a sphere with homogeneous vertices distribution, based on a UV Sphere construction",
    "author": "lemon",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "category": "Add Mesh"
    "location": "View3D > Add > Mesh",
}

import bpy
from math import pi, cos, sin

#Create a new mesh from a geometry 
def CreateMesh( scene, name, location, vertices, edges, polygons ):
    mesh = bpy.data.meshes.new( name )
    obj = bpy.data.objects.new( name, mesh )
    obj.location = location
 
    scene.objects.link( obj )
    scene.objects.active = obj
    obj.select = True
 
    mesh.from_pydata( vertices, edges, polygons )
    mesh.update()    

    return obj

#Merge new vertices (a ring) to previous one
def MergeGeometry( vertices, edges, newVertices ):
    base = len( vertices )
    vertices += newVertices
    newVerticesAmount = len( newVertices )
    if newVerticesAmount > 2:
        edges += [(base + i, base + int((i+1) % newVerticesAmount) ) for i in range( newVerticesAmount )]
    elif newVerticesAmount == 2:
        edges += [(base, base + 1)]
    return vertices, edges    

#Calculate a circle
def Circle( z, r, verticesAmount ):
    baseAngle = 2 * pi / verticesAmount
    return [(r * cos(i * baseAngle), r * sin(i * baseAngle), z) for i in range( verticesAmount )]

#Calculate the sphere
def HomogeneousSphereBySegments( segments, r ):
    vertices, edges = [], []

    if segments % 2 == 0:
        ringAmount = segments // 2
        baseAngle = pi / ringAmount
        chord = 2 * r * sin( pi / segments )
        arc = 2 * pi * r / segments
    else:
        #If odd we have to shift the angle from the 'equator'
        ringAmount = segments // 2 
        baseAngle = pi / ringAmount
        chord = 2 * r * cos( baseAngle / 2 ) * sin( pi / segments )
        arc = 2 * pi * r * cos( baseAngle / 2 ) / segments

    #First pole
    vertices += [(0,0,-r)]

    for i in range( 1, ringAmount ):
        angle = (i * baseAngle) - (pi / 2)
        z = r * sin( angle )
        localR = abs( r * cos( angle ) )
        verticesAmount = int( 2 * pi * localR / arc )
        vertices, edges = MergeGeometry( vertices, edges, Circle( z, localR, verticesAmount ) )
        print( ringAmount, baseAngle, angle, z, localR )        

    #Second pole
    vertices += [(0,0,r)]
        
    return vertices, edges

class HomogeneousSphere( bpy.types.Operator ):
    bl_idname = "object.homogeneous_sphere"
    bl_label = "Add a homogeneous sphere"
    bl_options = {'REGISTER', 'UNDO'}

    segments = bpy.props.IntProperty( name="Segments", default=32, min=3, soft_max=100,  ) 
    radius = bpy.props.FloatProperty( name="Radius", default=1, min=0, soft_min=0.001 )
    useDupli = bpy.props.BoolProperty( name="Use dupli" )
    dupli = bpy.props.StringProperty( name="Dupli" )
    
    def execute( self, context ):
        scene = context.scene
        cursor = context.scene.cursor_location

        vertices, edges = HomogeneousSphereBySegments( self.segments, self.radius )
        obj = CreateMesh( scene, 'HSphere', cursor, vertices, edges, [] )

        if self.useDupli and self.dupli in scene.objects and obj.name != self.dupli:
            scene.objects[self.dupli].parent = obj
            obj.dupli_type = 'VERTS'
            obj.use_dupli_vertices_rotation = True

        return {'FINISHED'}

    def draw( self, context ):
        layout = self.layout
        layout.row().prop( self, "segments" )
        layout.row().prop( self, "radius" )
        layout.row().prop( self, "useDupli" )
        if self.useDupli:
            layout.row().prop_search( self, "dupli", context.scene, "objects" )

def HomogeneousSphereMenu(self, context):
    self.layout.operator( HomogeneousSphere.bl_idname, text="Homogeneous Sphere", icon='MESH_UVSPHERE' )

def register():
    bpy.utils.register_class( HomogeneousSphere )
    bpy.types.INFO_MT_mesh_add.append( HomogeneousSphereMenu )

def unregister():
    bpy.types.INFO_MT_mesh_add.remove( HomogeneousSphereMenu )
    bpy.utils.unregister_class( HomogeneousSphere )

if __name__ == "__main__":
    register()