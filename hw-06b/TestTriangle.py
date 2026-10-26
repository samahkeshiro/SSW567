# -*- coding: utf-8 -*-
"""
Updated Jan 21, 2018
The primary goal of this file is to demonstrate a simple unittest implementation

@author: jrr
@author: rk
Updated Oct 2026: expanded test set (equivalence classes, boundary values,
permutations of side order, invalid inputs).
"""

import unittest

from Triangle import classifyTriangle

# This code implements the unit test functionality
# https://docs.python.org/3/library/unittest.html has a nice description of the framework

class TestTriangles(unittest.TestCase):
    # define multiple sets of tests as functions with names that begin

    # ---------- Equilateral ----------
    def testEquilateralLowerBoundary(self):  # T01
        self.assertEqual(classifyTriangle(1, 1, 1), 'Equilateral', '1,1,1 should be equilateral')

    def testEquilateralUpperBoundary(self):  # T02
        self.assertEqual(classifyTriangle(200, 200, 200), 'Equilateral', '200,200,200 should be equilateral')

    def testEquilateralNominal(self):  # T03
        self.assertEqual(classifyTriangle(7, 7, 7), 'Equilateral', '7,7,7 should be equilateral')

    # ---------- Isosceles (each pair of equal sides) ----------
    def testIsoscelesAB(self):  # T04
        self.assertEqual(classifyTriangle(5, 5, 8), 'Isoceles', '5,5,8 should be isosceles')

    def testIsoscelesBC(self):  # T05
        self.assertEqual(classifyTriangle(8, 5, 5), 'Isoceles', '8,5,5 should be isosceles')

    def testIsoscelesAC(self):  # T06
        self.assertEqual(classifyTriangle(5, 8, 5), 'Isoceles', '5,8,5 should be isosceles')

    # ---------- Scalene ----------
    def testScaleneA(self):  # T07
        self.assertEqual(classifyTriangle(4, 5, 6), 'Scalene', '4,5,6 should be scalene')

    def testScaleneB(self):  # T08
        self.assertEqual(classifyTriangle(6, 4, 5), 'Scalene', '6,4,5 should be scalene')

    def testScaleneC(self):  # T09
        self.assertEqual(classifyTriangle(5, 6, 4), 'Scalene', '5,6,4 should be scalene')

    # ---------- Right (hypotenuse in each position) ----------
    def testRightTriangleA(self):  # T10
        self.assertEqual(classifyTriangle(3, 4, 5), 'Right', '3,4,5 is a Right triangle')

    def testRightTriangleB(self):  # T11
        self.assertEqual(classifyTriangle(5, 3, 4), 'Right', '5,3,4 is a Right triangle')

    def testRightTriangleC(self):  # T12
        self.assertEqual(classifyTriangle(4, 5, 3), 'Right', '4,5,3 is a Right triangle')

    def testRightTriangleD(self):  # T13
        self.assertEqual(classifyTriangle(5, 12, 13), 'Right', '5,12,13 is a Right triangle')

    # ---------- Not a triangle: degenerate (sum equals third side) ----------
    def testDegenerateC(self):  # T14
        self.assertEqual(classifyTriangle(1, 2, 3), 'NotATriangle', '1+2 = 3 is not a triangle')

    def testDegenerateA(self):  # T15
        self.assertEqual(classifyTriangle(3, 1, 2), 'NotATriangle', '1+2 = 3 is not a triangle')

    def testDegenerateB(self):  # T16
        self.assertEqual(classifyTriangle(1, 3, 2), 'NotATriangle', '1+2 = 3 is not a triangle')

    # ---------- Not a triangle: one side too long ----------
    def testNotTriangleC(self):  # T17
        self.assertEqual(classifyTriangle(1, 2, 10), 'NotATriangle', '1+2 < 10 is not a triangle')

    def testNotTriangleA(self):  # T18
        self.assertEqual(classifyTriangle(10, 1, 2), 'NotATriangle', '1+2 < 10 is not a triangle')

    def testNotTriangleB(self):  # T19
        self.assertEqual(classifyTriangle(1, 10, 2), 'NotATriangle', '1+2 < 10 is not a triangle')

    # ---------- Invalid: below lower boundary ----------
    def testZeroA(self):  # T20
        self.assertEqual(classifyTriangle(0, 1, 1), 'InvalidInput', 'a = 0 is invalid')

    def testZeroB(self):  # T21
        self.assertEqual(classifyTriangle(1, 0, 1), 'InvalidInput', 'b = 0 is invalid')

    def testZeroC(self):  # T22
        self.assertEqual(classifyTriangle(1, 1, 0), 'InvalidInput', 'c = 0 is invalid')

    def testNegative(self):  # T23
        self.assertEqual(classifyTriangle(-3, 4, 5), 'InvalidInput', 'negative side is invalid')

    # ---------- Invalid: above upper boundary ----------
    def testTooLargeA(self):  # T24
        self.assertEqual(classifyTriangle(201, 150, 100), 'InvalidInput', 'a = 201 is invalid')

    def testTooLargeB(self):  # T25
        self.assertEqual(classifyTriangle(150, 201, 100), 'InvalidInput', 'b = 201 is invalid')

    def testTooLargeC(self):  # T26
        self.assertEqual(classifyTriangle(150, 100, 201), 'InvalidInput', 'c = 201 is invalid')

    # ---------- Invalid: non-integer types ----------
    def testFloatInput(self):  # T27
        self.assertEqual(classifyTriangle(3.0, 4, 5), 'InvalidInput', 'float input is invalid')

    def testStringInput(self):  # T28
        self.assertEqual(classifyTriangle('3', 4, 5), 'InvalidInput', 'string input is invalid')

if __name__ == '__main__':
    print('Running unit tests')
    unittest.main()
