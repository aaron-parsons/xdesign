#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #########################################################################
# Copyright (c) 2016, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2016. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import logging
import matplotlib.pyplot as plt
from matplotlib.path import Path
from numbers import Number
import polytope as pt
from cached_property import cached_property
import copy
from math import sqrt, asin

logger = logging.getLogger(__name__)

__author__ = "Doga Gursoy"
__copyright__ = "Copyright (c) 2016, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['Entity',
           'Point',
        #    'Superellipse',
        #    'Ellipse',
           'Circle',
           'Line',
           'Polygon',
           'Triangle',
           'Rectangle',
           'Square',
           'Mesh']


class Entity(object):
    """Base class for all geometric entities. All geometric entities should
    have these methods."""

    def __init__(self):
        self._dim = 0

    def __str__(self):
        """A string representation for easier debugging."""
        raise NotImplementedError

    @property
    def dim(self):
        """The dimensionality of the entity"""
        return self._dim

    def translate(self, vector):
        """Translate entity along vector."""
        raise NotImplementedError

    def rotate(self, theta, point=None, axis=None):
        """Rotate entity around an axis which passes through a point by theta
        radians."""
        raise NotImplementedError

    def scale(self, vector):
        """Scale entity in each dimension according to vector. Scaling is
        centered on the origin."""
        raise NotImplementedError

    def contains(self, point):
        """Returns True if the point(s) is within the bounds of the entity.
        point is either a Point or an N points listed as an NxD array."""
        raise NotImplementedError

    def collision(self, other):
        """Returns True if this entity collides with another entity."""
        raise NotImplementedError

    def distance(self, other):
        """Return the closest distance between entities."""
        raise NotImplementedError

    def midpoint(self, other):
        """Return the midpoint between entities."""
        return self.distance(other) / 2.


class Point(Entity):
    """A point in ND cartesian space.

    Attributes
    ----------
    _x : 1darray
        ND coordinates of the point.
    x : scalar
        dimension 0 of the point.
    y : scalar
        dimension 1 of the point.
    z : scalar
        dimension 2 of the point.
    norm : scalar
        The L2/euclidian norm of the point.
    """
    def __init__(self, x):
        if not isinstance(x, (list, np.ndarray)):
            raise TypeError("x must be list, or array of coordinates.")

        super(Point, self).__init__()
        self._x = np.array(x, dtype=float, ndmin=1)
        self._x = np.ravel(self._x)
        self._dim = self._x.size

    def __str__(self):
        return "Point(%s" % ', '.join([str(n) for n in self._x]) + ")"

    @property
    def x(self):
        return self._x[0]

    @property
    def y(self):
        return self._x[1]

    @property
    def z(self):
        return self._x[2]

    @property
    def norm(self):
        """Reference: http://stackoverflow.com/a/23576322"""
        return sqrt(self._x.dot(self._x))

    @property
    def dim(self):
        return self._dim

    def translate(self, vector):
        """Translate point along vector."""
        if not isinstance(vector, (list, np.ndarray)):
            raise TypeError("vector must be arraylike.")

        self._x += vector

    def rotate(self, theta, point=None, axis=None):
        """Rotate entity around an axis by theta radians."""
        if not isinstance(theta, Number):
            raise TypeError("theta must be scalar.")
        if point is None:
            center = np.zeros(self.dim)
        elif isinstance(point, Point):
            center = point._x
        else:
            raise TypeError("center of rotation must be Point.")
        if axis is not None:
            raise NotImplementedError

        # shift rotation center to origin
        self._x -= center
        # do rotation
        R = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta),  np.cos(theta)]])
        self._x = np.dot(R, self._x)
        # shift rotation center back
        self._x += center

    def scale(self, vector):
        """Scale entity in each dimension according to vector. Scaling is
        centered on the origin."""
        if not isinstance(vector, (List, np.ndarray)):
            raise TypeError("vector must be arraylike.")

        self._x *= vector

    def contains(self, other):
        """Returns True if the other is within the bounds of the entity."""
        if isinstance(other, Point):
            return self == point
        if isinstance(other, np.ndarray):
            return np.all(self._x == other[:], axis=1)
        else:  # points can only contain points
            return False

    def collision(self, other):
        """Returns True if this entity collides with another entity."""
        if isinstance(other, Point):
            return self == point
        else:
            raise NotImplementedError

    def distance(self, other):
        """Return the closest distance between entities."""
        if not isinstance(other, Point):
            raise NotImplementedError("Point to point distance only.")
        d = self._x - other._x
        return sqrt(d.dot(d))

    # OVERLOADS
    def __eq__(self, point):
        if not isinstance(point, Point):
            raise TypeError("Points can only equal to other points.")
        return np.array_equal(self._x, point._x)

    def __add__(self, point):
        """Addition."""
        if not isinstance(point, Point):
            raise TypeError("Points can only add to other points.")
        return Point(self._x + point._x)

    def __sub__(self, point):
        """Subtraction."""
        if not isinstance(point, Point):
            raise TypeError("Points can only subtract from other points.")
        return Point(self._x - point._x)

    def __mul__(self, c):
        """Scalar, vector multiplication."""
        if not isinstance(c, Number):
            raise TypeError("Points can only multiply scalars.")
        return Point(self._x * c)

    def __truediv__(self, c):
        """Scalar, vector division."""
        if not isinstance(c, Number):
            raise TypeError("Points can only divide scalars.")
        return Point(self._x / c)

    def __hash__(self):
        return hash(self._x[:])


class LinearEntity(Entity):
    """Base class for linear entities in 2-D Cartesian space.

    Attributes
    ----------
    p1 : Point
    p2 : Point
    vertical : bool
    horizontal : bool
    slope : scalar
    points : list
    normal : Point
    tangent : Point
    dim : scalar
    """
    def __init__(self, p1, p2):
        if not isinstance(p1, Point) or not isinstance(p2, Point):
            raise TypeError("p1 and p2 must be points")
        if p1 == p2:
            raise ValueError('Requires two unique points.')
        if p1.dim != p2.dim:
            raise ValueError('Two points must have same dimensionality.')
        self.p1 = p1
        self.p2 = p2
        self._dim = p1.dim

    def __str__(self):
        return "Edge(" + str(self.p1) + ", " + str(self.p2) + ")"

    @property
    def vertical(self):
        """True if line is vertical."""
        return self.p1.x == self.p2.x

    @property
    def horizontal(self):
        """True if line is horizontal."""
        return self.p1.y == self.p2.y

    @property
    def slope(self):
        """Return the slope of the line."""
        if self.vertical:
            return np.inf
        else:
            return ((self.p2.y - self.p1.y) /
                    (self.p2.x - self.p1.x))

    @property
    def points(self):
        """The two points used to define this linear entity."""
        return (self.p1, self.p2)

    # @property
    # def bounds(self):
    #     """Return a tuple (xmin, ymin, xmax, ymax) representing the
    #     bounding rectangle for the geometric figure.
    #     """
    #     xs = [p.x for p in self.points]
    #     ys = [p.y for p in self.points]
    #     return (min(xs), min(ys), max(xs), max(ys))

    @property
    def length(self):
        """Returns the length of the segment"""
        return self.p1.distance(self.p2)

    @property
    def tangent(self):
        """Return unit tangent vector."""
        dx = (self.p2._x - self.p1._x) / self.length
        return Point(dx)

    @property
    def normal(self):
        """Return unit normal vector."""
        dx = (self.p2._x - self.p1._x) / self.length
        R = np.array([[0, 1],
                      [-1,  0]])
        n = np.dot(R, dx)
        return Point(n)

    @property
    def numpy(self):
        """Return list representation."""
        return np.vstack((self.p1._x, self.p2._x))

    @property
    def list(self):
        """Return list representation."""
        return np.hstack((self.p1._x, self.p2._x))

    @property
    def dim(self):
        """The dimensionality of the entity"""
        return self._dim

    def translate(self, vector):
        """Translate entity along vector."""
        self.p1.translate(vector)
        self.p2.translate(vector)

    def rotate(self, theta, point=None, axis=None):
        """Rotate entity around an axis which passes through an point by theta
        radians."""
        self.p1.rotate(theta, point, axis)
        self.p2.rotate(theta, point, axis)


class Line(LinearEntity):
    """Line in 2-D cartesian space.

    It is defined by two distinct points.

    Attributes
    ----------
    p1 : Point
    p2 : Point
    """

    def __init__(self, p1, p2):
        super(Line, self).__init__(p1, p2)

    def __str__(self):
        """Return line equation."""
        if self.vertical:
            return "x = %s" % self.p1.x
        elif self.dim == 2:
            return "y = %sx + %s" % (self.slope, self.yintercept)
        else:
            A, B = self.standard
            return "%sx " % '+ '.join([str(n) for n in A]) + "= " + str(B)

    def __eq__(self, line):
        return (self.slope, self.yintercept) == (line.slope, line.yintercept)

    def intercept(self, n):
        """Calculates the intercept for the nth dimension."""
        if n > self._dim:
            return 0
        else:
            A, B = self.standard
            if A[n] == 0:
                return np.inf
            else:
                return B/A[n]

    @property
    def xintercept(self):
        """Return the x-intercept."""
        if self.horizontal:
            return np.inf
        else:
            return self.p1.x - 1 / self.slope * self.p1.y

    @property
    def yintercept(self):
        """Return the y-intercept."""
        if self.vertical:
            return np.inf
        else:
            return self.p1.y - self.slope * self.p1.x

    @property
    def standard(self):
        """Returns coeffients for the first N-1 standard equation coefficients.
        The Nth is returned separately."""
        A = np.vstack((self.p1._x, self.p2._x))
        return calc_standard(A)

    def distance(self, other):
        """Return the closest distance between entities.
        REF: http://geomalgorithms.com/a02-_lines.html"""
        if not isinstance(other, Point):
            raise NotImplementedError("Line to point distance only.")
        d = np.cross(self.tangent._x, other._x - self.p1._x)
        if self.dim > 2:
            return sqrt(d.dot(d))
        else:
            return abs(d)


# class Ray(LinearEntity):
#     """Ray in 2-D cartesian space.
#
#     It is defined by two distinct points.
#
#     Attributes
#     ----------
#     p1 : Point (source)
#     p2 : Point (point direction)
#     """
#
#     def __init__(self, p1, p2):
#         super(Ray, self).__init__(p1, p2)
#
#     @property
#     def source(self):
#         """The point from which the ray emanates."""
#         return self.p1
#
#     @property
#     def direction(self):
#         """The direction in which the ray emanates."""
#         return self.p2 - self.p1


# class Segment(LinearEntity):
#     """Segment in 2-D cartesian space.
#
#     It is defined by two distinct points.
#
#     Attributes
#     ----------
#     p1 : Point (source)
#     p2 : Point (point direction)
#     """
#
#     def __init__(self, p1, p2):
#         super(Segment, self).__init__(p1, p2)
#
#     @property
#     def midpoint(self):
#         """The midpoint of the line segment."""
#         return Point.midpoint(self.p1, self.p2)


class Curve(Entity):
    """Base class for entities whose surface can be defined by a continuous
    equation.

    Attributes
    ----------
    center : Point
    """
    def __init__(self, center):
        if not isinstance(center, Point):
            raise TypeError("center must be a Point.")
        super(Curve, self).__init__()
        self.center = center

    def translate(self, vector):
        """Translate point along vector."""
        if not isinstance(vector, (Point, list, nd.array)):
            raise TypeError("vector must be point, list, or array.")
        self.center.translate(vector)

    def rotate(self, theta, point=None, axis=None):
        """Rotate entity around an axis which passes through a point by theta
        radians."""
        self.center.rotate(theta, point, axis)


class Superellipse(Curve):
    """Superellipse in 2-D cartesian space.

    Attributes
    ----------
    center : Point
    a : scalar
    b : scalar
    n : scalar
    """

    def __init__(self, center, a, b, n):
        super(Superellipse, self).__init__(center)
        self.a = float(a)
        self.b = float(b)
        self.n = float(n)

    @property
    def list(self):
        """Return list representation."""
        return [self.center.x, self.center.y, self.a, self.b, self.n]

    def scale(self, val):
        """Scale."""
        self.a *= val
        self.b *= val


class Ellipse(Superellipse):
    """Ellipse in 2-D cartesian space.

    Attributes
    ----------
    center : Point
    a : scalar
    b : scalar
    """

    def __init__(self, center, a, b):
        super(Ellipse, self).__init__(center, a, b, 2)

    @property
    def list(self):
        """Return list representation."""
        return [self.center.x, self.center.y, self.a, self.b]

    @property
    def area(self):
        """Return area."""
        return np.pi * self.a * self.b

    def scale(self, val):
        """Scale."""
        self.a *= val
        self.b *= val


class Circle(Curve):
    """Circle in 2-D cartesian space.

    Attributes
    ----------
    center : Point
        Defines the center point of the circle.
    radius : scalar
        Radius of the circle.
    """

    def __init__(self, center, radius):
        super(Circle, self).__init__(center)
        self.radius = float(radius)

    def __str__(self):
        """Return analytical equation."""
        return "(x-%s)^2 + (y-%s)^2 = %s^2" % (self.center.x, self.center.y,
                                               self.radius)

    def __eq__(self, circle):
        return ((self.x, self.y, self.radius) ==
                (circle.x, circle.y, circle.radius))

    @property
    def list(self):
        """Return list representation for saving to files."""
        return [self.center.x, self.center.y, self.radius]

    @property
    def circumference(self):
        """Return circumference."""
        return 2 * np.pi * self.radius

    @property
    def diameter(self):
        """Return diameter."""
        return 2 * self.radius

    @property
    def area(self):
        """Return area."""
        return np.pi * self.radius**2

    @property
    def patch(self):
        return plt.Circle((self.center.x, self.center.y), self.radius)

    def scale(self, val):
        """Scale."""
        raise NotImplementedError
        # self.center.scale(val)
        # self.rad *= val

    def contains(self, points):
        if isinstance(points, Point):
            x = p._x
        elif isinstance(points, np.ndarray):
            x = points
        else:
            raise TypeError("P must be point or ndarray")

        return np.sum((x - self.center._x)**2, axis=1) <= self.radius**2


class Polygon(Entity):
    """A convex polygon in 2-D cartesian space.

    It is defined by a number of distinct points.

    Attributes
    ----------
    vertices : sequence of Points
    """

    def __init__(self, vertices):
        for v in vertices:
            if not isinstance(v, Point):
                raise TypeError("vertices must be of type Point.")
        super(Polygon, self).__init__()
        self.vertices = vertices
        self._dim = vertices[0].dim

    def __str__(self):
        return "Polygon(" + str(self.numpy) + ")"
    # return "Polygon(%s" % ', '.join([str(n) for n in self.vertices]) + ")"

    @property
    def numverts(self):
        return len(self.vertices)

    @property
    def list(self):
        """Return list representation."""
        lst = []
        for m in range(self.numverts):
            lst.append(self.vertices[m].list)
        return lst

    @property
    def numpy(self):
        """Return Numpy representation."""
        points = np.empty([self.numverts, self.dim])
        for m in range(self.numverts):
            points[m] = self.vertices[m]._x
        return points

    @property
    def area(self):
        """Return the area of the entity."""
        raise NotImplementedError

    @property
    def perimeter(self):
        """Return the perimeter of the entity."""
        perimeter = 0
        verts = self.vertices
        points = verts + [verts[0]]
        for m in range(self.numverts):
            perimeter += points[m].distance(points[m + 1])
        return perimeter

    @property
    def bounds(self):
        """Return a tuple (xmin, ymin, xmax, ymax) representing the
        bounding rectangle for the geometric figure.
        """
        xs = [p.x for p in self.vertices]
        ys = [p.y for p in self.vertices]
        return (min(xs), min(ys), max(xs), max(ys))

    @property
    def patch(self):
        return plt.Polygon(self.numpy)

    def translate(self, vector):
        """Translate polygon."""
        for v in self.vertices:
            v.translate(vector)

    def rotate(self, theta, point=None, axis=None):
        """Rotate entity around an axis which passes through a point by theta
        radians."""
        for v in self.vertices:
            v.rotate(theta, point, axis)

    def contains(self, points):
        if isinstance(points, Point):
            x = p._x
        elif isinstance(points, np.ndarray):
            x = points
        else:
            raise TypeError("P must be point or ndarray")

        border = Path(self.numpy)
        return border.contains_points(points)

    @cached_property
    def half_space(self):
        """Returns the half space polytope respresentation of the polygon."""
        assert(self.dim > 0), self.dim
        A = np.ndarray((self.numverts, self.dim))
        B = np.ndarray(self.numverts)

        for i in range(0, self.numverts):
            edge = Line(self.vertices[i], self.vertices[(i+1) % self.numverts])
            A[i, :], B[i] = edge.standard

            # test for positive or negative side of line
            if self.center._x.dot(A[i, :]) > B[i]:
                A[i, :] = -A[i, :]
                B[i] = -B[i]

        p = pt.Polytope(A, B)
        return p


class Triangle(Polygon):
    """Triangle in 2-D cartesian space.

    It is defined by three distinct points.
    """

    def __init__(self, p1, p2, p3):
        super(Triangle, self).__init__([p1, p2, p3])

    def __str__(self):
        return "Triangle(" + str(self.numpy) + ")"

    @property
    def center(self):
        center = Point([0, 0])
        for v in self.vertices:
            center += v
        return center / 3

    @property
    def area(self):
        A = self.vertices[0] - self.vertices[1]
        B = self.vertices[0] - self.vertices[2]
        return 1/2 * np.abs(np.cross([A.x, A.y], [B.x, B.y]))


class Rectangle(Polygon):
    """Rectangle in 2-D cartesian space.

    It is defined by four distinct points.
    """

    def __init__(self, p1, p2, p3, p4):
        super(Rectangle, self).__init__([p1, p2, p3, p4])

    def __str__(self):
        return "Rectangle(" + str(self.numpy) + ")"

    @property
    def center(self):
        center = Point([0, 0])
        for v in self.vertices:
            center += v
        return center / 4

    @property
    def area(self):
        return (self.vertices[0].distance(self.vertices[1]) *
                self.vertices[1].distance(self.vertices[2]))


class Square(Rectangle):
    """Square in 2-D cartesian space.

    It is defined by a center and a side length.
    """

    def __init__(self, center, side_length):
        if not isinstance(center, Point):
            raise TypeError("center must be of type Point.")
        if side_length <= 0:
            raise ValueError("side_length must be greater than zero.")

        s = side_length/2
        p1 = Point([center.x + s, center.y + s])
        p2 = Point([center.x - s, center.y + s])
        p3 = Point([center.x - s, center.y - s])
        p4 = Point([center.x + s, center.y - s])
        super(Square, self).__init__(p1, p2, p3, p4)

    def __str__(self):
        return "Square(" + str(self.numpy) + ")"


class Mesh(Entity):
    """A mesh object. It is a collection of polygons"""

    def __init__(self, obj=None):
        self.faces = []
        self.area = 0
        self.population = 0
        self.radius = 0

        if obj is not None:
            self.import_triangle(obj)

    def __str__(self):
        return "Mesh(" + str(self.center) + ")"

    def import_triangle(self, obj):
        """Loads mesh data from a Python Triangle dict.
        """
        for face in obj['triangles']:
            p0 = Point(obj['vertices'][face[0], 0],
                       obj['vertices'][face[0], 1])
            p1 = Point(obj['vertices'][face[1], 0],
                       obj['vertices'][face[1], 1])
            p2 = Point(obj['vertices'][face[2], 0],
                       obj['vertices'][face[2], 1])
            t = Triangle(p0, p1, p2)
            self.append(t)

    @property
    def center(self):
        center = Point([0, 0])
        if self.area > 0:
            for f in self.faces:
                center += f.center * f.area
            center /= self.area
        return center

    def append(self, t):
        """Add a triangle to the mesh."""
        assert(isinstance(t, Polygon))
        self.population += 1
        # self.center = ((self.center * self.area + t.center * t.area) /
        #                (self.area + t.area))
        self.area += t.area
        for v in t.vertices:
            self.radius = max(self.radius, self.center.distance(v))
        self.faces.append(t)

    def pop(self, i=-1):
        """Pop i-th triangle from the mesh."""
        self.population -= 1
        self.area -= self.faces[i].area
        try:
            del self.__dict__['center']
        except KeyError:
            pass
        return self.faces.pop(i)

    def translate(self, vector):
        """Translate entity."""
        for t in self.faces:
            t.translate(vector)

    def rotate(self, theta, point=None, axis=None):
        """Rotate entity around an axis which passes through a point by theta
        radians."""
        for t in self.faces:
            t.rotate(theta, point, axis)

    def scale(self, vector):
        """Scale entity."""
        for t in self.faces:
            t.scale(vector)

    def contains(self, points):
        if isinstance(points, Point):
            x = p._x
        elif isinstance(points, np.ndarray):
            x = points
        else:
            raise TypeError("P must be point or ndarray")

        bools = np.full(x.shape[0], False, dtype=bool)
        for f in self.faces:
            bools = np.logical_or(bools, f.contains(x))
        return bools

    @property
    def patch(self):
        patches = []
        for f in self.faces:
            patches.append(f.patch)
        return patches

    @cached_property
    def half_space(self):
        regions = []
        for face in self.faces:
            regions.append(face.half_space)
        return pt.Region(regions)


def calc_standard(A):
    """Returns the standard equation (c0*x = c1) coefficents for the hyper-plane
    defined by the row-wise ND points in A. Uses single value decomposition
    (SVD) to solve the coefficents for the homogenous equations.

    Parameters
    ----------
    points : 2Darray
        Each row is an ND point.

    Returns
    ----------
    c0 : 1Darray
        The first N coeffients for the hyper-plane
    c1 : 1Darray
        The last coefficient for the hyper-plane
    """
    if not isinstance(A, np.ndarray):
        raise TypeError("A must be np.ndarray")

    if A.ndim == 1:  # Special case for 1D
        return np.array([1]), A
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be 2D square.")

    # Add coordinate for last coefficient
    A = np.pad(A, ((0, 0), (0, 1)), 'constant', constant_values=1)

    atol = 1e-16
    rtol = 0
    u, s, vh = np.linalg.svd(A)
    tol = max(atol, rtol * s[0])
    nnz = (s >= tol).sum()
    ns = vh[nnz:].conj().T

    c = ns.squeeze()

    return c[0:-1], -c[-1]


def beamintersect(beam, geometry):
    """Intersection area of infinite beam with a geometry"""
    if isinstance(geometry, Mesh):
        return beammesh(beam, geometry)
    elif isinstance(geometry, Polygon):
        return beampoly(beam, geometry)
    elif isinstance(geometry, Circle):
        return beamcirc(beam, geometry)
    else:
        raise NotImplementedError


def beammesh(beam, mesh):
    """Intersection area of infinite beam with polygonal mesh"""
    return beam.half_space.intersect(mesh.half_space).volume


def beampoly(beam, poly):
    """Intersection area of an infinite beam with a polygon"""
    return beam.half_space.intersect(poly.half_space).volume


def beamcirc(beam, circle):
    """Intersection area of a Beam (line with finite thickness) and a circle.

    Reference
    ---------
    Glassner, A. S. (Ed.). (2013). Graphics gems. Elsevier.

    Parameters
    ----------
    beam : Beam
    circle : Circle

    Returns
    -------
    a : scalar
        Area of the intersected region.
    """
    r = circle.radius
    w = beam.size/2
    p = beam.distance(circle.center)
    assert(p >= 0)

    # print("BEAMCIRC r = %f, w = %f, p = %f" % (r, w, p), end="")

    if w == 0 or r == 0:
        return 0

    if w < r:
        if p < w:
            f = 1 - halfspacecirc(w - p, r) - halfspacecirc(w + p, r)
        elif p < r - w:  # and w <= p
            f = halfspacecirc(p - w, r) - halfspacecirc(w + p, r)
        else:  # r - w <= p
            f = halfspacecirc(p - w, r)
    else:  # w >= r
        if p < w:
            f = 1 - halfspacecirc(w - p, r)
        else:  # w <= pd
            f = halfspacecirc(p - w, r)

    a = np.pi * r**2 * f
    assert(a >= 0), a
    # print()
    return a


def halfspacecirc(d, r):
    """Area of intersection between circle and half-plane. Returns the smaller
    fraction of a circle split by a line d units away from the center of the
    circle.

    Reference
    ---------
    Glassner, A. S. (Ed.). (2013). Graphics gems. Elsevier.

    Parameters
    ----------
    d : scalar
        The distance from the line to the center of the circle
    r : scalar
        The radius of the circle

    Returns
    -------
    f : scalar
        The proportion of the circle in the smaller half-space
    """
    assert(r > 0), "The radius must positive"
    assert(d >= 0), "The distance must be positive or zero."

    if d >= r:  # The line is too far away to overlap!
        return 0

    f = 0.5 - d*sqrt(r**2 - d**2)/(np.pi*r**2) - asin(d/r)/np.pi

    # Returns the smaller fraction of the circle, so it can be at most 1/2.
    try:
        assert(0 <= f and f <= 0.5), f
    except:
        RuntimeWarning("halfspacecirc was out of bounds, %f" % f)
        f = 0
    return f
