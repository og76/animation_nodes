
from math import sin, cos, tan, radians, ceil, copysign
from mathutils import Vector

    ##### circle creation 
    ####################################


##### circle vecs with options
    # if fixDiv, will get a constand div of 360 circle
    #               else will divide the arc start/end
    # op: arc as pie/bow, clip delta to min/max (-)360
    
# to use start/end angles an option and this line before:
#    deltaAngle = endAngle - startAngle if not option...

def circleVectors(  center, radiusX, radiusY, startAngle, deltaAngle, 
                    divisions = 24, fixDivisions = False, 
                    clip360 = True, pie = True):

    divisions = max(divisions, 3)
    
    # options
    extra = 1
    V = [center] if pie else []
    if clip360: 
        deltaAngle = min(max(deltaAngle, -360), 360)
        if abs(deltaAngle) == 360: 
            extra = 0
            V = []

    # creation div / 360
    if fixDivisions:
        return V + circleVectors360Divided( center, radiusX, radiusY, 
                                            startAngle, deltaAngle, 
                                            divisions, extra)
    # creation div / arc
    return V + circleVectorsArcDivided( center, radiusX, radiusY, 
                                        startAngle, deltaAngle, 
                                        divisions, extra)



##### creation div / 360 (if cyclic extra = 0)
def circleVectors360Divided(center, radiusX, radiusY, startAngle, deltaAngle, 
                            divisions = 24, extra = 1):

    unit = copysign( radians(360 / divisions), deltaAngle)
    divisions = ceil(divisions * abs(deltaAngle) / 360)
    
    if extra:
        end = radians(deltaAngle + startAngle)
        last = [Vector((cos(end) * radiusX, 
                        sin(end) * radiusY, 
                        0)) + center]
    else: last = []
    
    start = radians(startAngle)
    return [Vector((cos(i * unit + start) * radiusX, 
                    sin(i * unit + start) * radiusY, 
                    0)) + center for i in range(divisions)] + last


##### creation div / arc (if cyclic extra = 0)
def circleVectorsArcDivided(center, radiusX, radiusY, startAngle, deltaAngle, 
                            divisions = 24, extra = 1):

    unit = radians(deltaAngle / divisions)
    start= radians(startAngle)
    return [Vector((cos(i * unit + start) * radiusX, 
                    sin(i * unit + start) * radiusY, 
                    0)) + center for i in range(divisions + extra)]



##### circle / cyclic / ngon indices
    # use vector list length for divisions
    
def ngonEdges(divisions = 24):
    return [(i, (i + 1) % divisions) for i in range(divisions) ]
    
def ngonPolygon(divisions = 24):
    return [tuple( range(divisions))]


    ##### end circle creation 
    ####################################



    ##### triangle grid creation 
    ####################################

# vectors
# height should be = distance * tan(angle) / 2
def triGridVertices(offset, xDiv, yDiv, base, height, shift, flip):
    vectorList = []
    
    shift = ( base + min(max(base * shift, -1), 1) ) / 2

    for y in range(yDiv):
        shiftX = y % 2 * shift
        Y = y * height
        for x in range(xDiv):
            X = x * base + shiftX

            if flip:
                vectorList.append(Vector(( Y, X, 0 )) + offset)
            else:
                vectorList.append(Vector(( X, Y, 0 )) + offset)
    
    return vectorList


# indices
def triGridEdgeIndices(xDiv, yDiv):
    edgeIndicesList = []
    for y in range(yDiv):
        for x in range(xDiv):
            i1 =       y * xDiv + x
            i2 =       y * xDiv + x + 1
            i3 = (y + 1) * xDiv + x
            i4 = (y + 1) * xDiv + x + 1
            
            if x < xDiv-1: edgeIndicesList.append((i1, i2))
            if y < yDiv-1: edgeIndicesList.append((i1, i3))
            if x < xDiv-1 and y < yDiv-1: 
                if y % 2 == 0: 
                    edgeIndicesList.append((i3, i2))
                else: 
                    edgeIndicesList.append((i1, i4))
    
    return edgeIndicesList

def triGridPolygonIndices(xDiv, yDiv):
    polygonIndicesList = []
    for y in range(yDiv-1):
        for x in range(xDiv-1):
            i1 =       y * xDiv + x
            i2 =       y * xDiv + x + 1
            i3 = (y + 1) * xDiv + x
            i4 = (y + 1) * xDiv + x + 1
            
            if y % 2 == 0:
                polygonIndicesList.append((i1, i2, i3))
                polygonIndicesList.append((i2, i4, i3))
            else:
                polygonIndicesList.append((i1, i4, i3))
                polygonIndicesList.append((i1, i2, i4))
    
    return polygonIndicesList