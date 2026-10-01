import contextlib
import io
import math
import unittest


# ---------------------------------------------------------------------------
# 1. The correct, final solution.
# ---------------------------------------------------------------------------

def classify_triangle(a, b, c):
    """Return the triangle type for sides a, b, c, or "Not a valid triangle".

    Raises TypeError if any side is not an int or float.
    """
    # --- Validate input types -------------------------------------------
    for side in (a, b, c):
        if not isinstance(side, (int, float)) or isinstance(side, bool):
            raise TypeError("All three sides must be numeric (int or float).")

    # --- Validate that sides are positive --------------------------------
    if a <= 0 or b <= 0 or c <= 0:
        return "Not a valid triangle"

    # --- Validate the triangle inequality ---------------------------------
    if (a + b <= c) or (a + c <= b) or (b + c <= a):
        return "Not a valid triangle"

    # --- Determine scalene / isosceles / equilateral -----------------------
    if a == b == c:
        shape = "Equilateral Triangle"
    elif a == b or b == c or a == c:
        shape = "Isosceles Triangle"
    else:
        shape = "Scalene Triangle"

    # --- Determine whether it is also a right triangle ----------------------
    sides = sorted([a, b, c])
    shortest, middle, longest = sides[0], sides[1], sides[2]

    # Use a small tolerance to account for floating point rounding error.
    is_right = math.isclose(
        shortest ** 2 + middle ** 2,
        longest ** 2,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )

    if is_right:
        return f"{shape}, Right Triangle"
    return f"{shape}, Not a Right Triangle"


# ---------------------------------------------------------------------------
# 2. A version of the SAME function with two intentionally injected bugs,
#    kept here so the TestTriangles suite below can demonstrate that it
#    actually catches real defects (per the assignment's suggestion to
#    include a few bugs to prove your tests are working).
# ---------------------------------------------------------------------------

def classify_triangle_buggy(a, b, c):
    """Same as classify_triangle(), but with two intentional bugs:

    BUG 1: the triangle-inequality check uses strict '<' instead of '<=',
           so a degenerate "triangle" where a + b == c (a straight line,
           not a real triangle) is incorrectly treated as valid.

    BUG 2: the right-triangle check uses exact floating point equality
           instead of a tolerance-based comparison, so a legitimate right
           triangle whose sides aren't "nice" integers (e.g. involving a
           sqrt() result) is incorrectly reported as not right.
    """

    for side in (a, b, c):
        if not isinstance(side, (int, float)) or isinstance(side, bool):
            raise TypeError("All three sides must be numeric (int or float).")

    if a <= 0 or b <= 0 or c <= 0:
        return "Not a valid triangle"

    # BUG 1 is on the next line: should be <=, not <.
    if (a + b < c) or (a + c < b) or (b + c < a):
        return "Not a valid triangle"

    if a == b == c:
        shape = "Equilateral Triangle"
    elif a == b or b == c or a == c:
        shape = "Isosceles Triangle"
    else:
        shape = "Scalene Triangle"

    sides = sorted([a, b, c])
    shortest, middle, longest = sides[0], sides[1], sides[2]

    # BUG 2 is on the next line: exact '==' instead of math.isclose().
    is_right = shortest ** 2 + middle ** 2 == longest ** 2

    if is_right:
        return f"{shape}, Right Triangle"
    return f"{shape}, Not a Right Triangle"


# ---------------------------------------------------------------------------
# 3. Print wrapper for manual demo runs, kept separate from
#    classify_triangle() itself so the function under test stays trivial
#    to call directly from a test framework.
# ---------------------------------------------------------------------------

def run_classify_triangle(a, b, c):
    """Invoke classify_triangle() with the given arguments and print the
    result."""
    print(f"classify_triangle({a}, {b}, {c}) = {classify_triangle(a, b, c)}")


# ---------------------------------------------------------------------------
# 4. Unit tests. Every test is written once and run against BOTH
#    classify_triangle() (expected: all pass) and classify_triangle_buggy()
#    (expected: 2 failures, the two bugs described above). This is done
#    with a "mixin" pattern: shared test bodies call
#    self.classify_triangle(...), and two small TestCase subclasses near
#    the bottom bind that name to each function in turn.
# ---------------------------------------------------------------------------

class ValidityTestsMixin:
    """Tests for rejecting invalid (non-)triangles."""

    def test_sum_of_two_sides_equal_third_is_invalid(self):
        """Test: sum of two sides equal third is invalid."""
        # Degenerate triangle: a straight line, not a real triangle.
        self.assertEqual(self.classify_triangle(1, 2, 3), "Not a valid triangle")

    def test_sum_of_two_sides_less_than_third_is_invalid(self):
        """Test: sum of two sides less than third is invalid."""
        self.assertEqual(self.classify_triangle(1, 2, 10), "Not a valid triangle")

    def test_negative_side_is_invalid(self):
        """Test: negative side is invalid."""
        self.assertEqual(self.classify_triangle(-3, 4, 5), "Not a valid triangle")

    def test_zero_side_is_invalid(self):
        """Test: zero side is invalid."""
        self.assertEqual(self.classify_triangle(0, 4, 5), "Not a valid triangle")

    def test_all_zero_sides_is_invalid(self):
        """Test: all zero sides is invalid."""
        self.assertEqual(self.classify_triangle(0, 0, 0), "Not a valid triangle")

    def test_non_numeric_side_raises_type_error(self):
        """Test: non numeric side raises type error."""
        with self.assertRaises(TypeError):
            self.classify_triangle("3", 4, 5)


class ShapeTestsMixin:
    """Tests for correctly identifying scalene / isosceles / equilateral."""

    def test_equilateral(self):
        """Test: equilateral."""
        result = self.classify_triangle(5, 5, 5)
        self.assertIn("Equilateral", result)

    def test_isosceles_first_pair_equal(self):
        """Test: isosceles first pair equal."""
        result = self.classify_triangle(5, 5, 8)
        self.assertIn("Isosceles", result)

    def test_isosceles_second_pair_equal(self):
        """Test: isosceles second pair equal."""
        result = self.classify_triangle(8, 5, 5)
        self.assertIn("Isosceles", result)

    def test_isosceles_outer_pair_equal(self):
        """Test: isosceles outer pair equal."""
        result = self.classify_triangle(5, 8, 5)
        self.assertIn("Isosceles", result)

    def test_scalene(self):
        """Test: scalene."""
        result = self.classify_triangle(4, 5, 6)
        self.assertIn("Scalene", result)

    def test_scalene_not_mislabeled_isosceles(self):
        """Test: scalene not mislabeled isosceles."""
        # Guards against an off-by-one style bug in the equality checks.
        result = self.classify_triangle(7, 8, 9)
        self.assertIn("Scalene", result)
        self.assertNotIn("Isosceles", result)
        self.assertNotIn("Equilateral", result)


class RightAngleTestsMixin:
    """Tests for correctly identifying right triangles."""

    def test_classic_3_4_5_is_right(self):
        """Test: classic 3-4-5 is right."""
        result = self.classify_triangle(3, 4, 5)
        self.assertIn("Right Triangle", result)
        self.assertNotIn("Not a Right", result)

    def test_5_12_13_is_right(self):
        """Test: 5-12-13 is right."""
        result = self.classify_triangle(5, 12, 13)
        self.assertIn("Right Triangle", result)
        self.assertNotIn("Not a Right", result)

    def test_order_of_sides_does_not_matter_for_right_check(self):
        """Test: order of sides does not matter for right check."""
        # Right-triangle check must work regardless of parameter order.
        result = self.classify_triangle(5, 3, 4)
        self.assertIn("Right Triangle", result)
        self.assertNotIn("Not a Right", result)

    def test_isosceles_right_triangle(self):
        """Test: isosceles right triangle."""
        # An isosceles right triangle with legs 5, 5 has hypotenuse
        # 5*sqrt(2) ~= 7.0710678118654755
        result = self.classify_triangle(5, 5, 7.0710678118654755)
        self.assertIn("Isosceles", result)
        self.assertIn("Right Triangle", result)
        self.assertNotIn("Not a Right", result)

    def test_equilateral_is_never_right(self):
        """Test: equilateral is never right."""
        result = self.classify_triangle(6, 6, 6)
        self.assertIn("Not a Right Triangle", result)

    def test_obtuse_scalene_is_not_right(self):
        """Test: obtuse scalene is not right."""
        result = self.classify_triangle(2, 3, 4)
        self.assertIn("Not a Right Triangle", result)

    def test_acute_scalene_is_not_right(self):
        """Test: acute scalene is not right."""
        result = self.classify_triangle(6, 7, 8)
        self.assertIn("Not a Right Triangle", result)


class FloatInputsTestsMixin:
    """Tests using floating point side lengths."""

    def test_float_scalene_right_triangle(self):
        """Test: float scalene right triangle."""
        result = self.classify_triangle(1.5, 2.0, 2.5)
        self.assertIn("Scalene", result)
        self.assertIn("Right Triangle", result)
        self.assertNotIn("Not a Right", result)

    def test_float_equilateral(self):
        """Test: float equilateral."""
        result = self.classify_triangle(2.5, 2.5, 2.5)
        self.assertIn("Equilateral", result)


class TestTriangles(
    ValidityTestsMixin,
    ShapeTestsMixin,
    RightAngleTestsMixin,
    FloatInputsTestsMixin,
    unittest.TestCase,
):
    """Runs the full suite against the corrected classify_triangle().
    Expected: all tests pass. This is the test class that certifies the
    submitted solution.
    """
    classify_triangle = staticmethod(classify_triangle)


class TestTrianglesBuggyVersion(
    ValidityTestsMixin,
    ShapeTestsMixin,
    RightAngleTestsMixin,
    FloatInputsTestsMixin,
    unittest.TestCase,
):
    """
    Expected: 2 failures, corresponding to the two bugs intentionally
    injected above:
      1. test_sum_of_two_sides_equal_third_is_invalid  (off-by-one in the
         triangle inequality check lets a degenerate triangle through)
      2. test_isosceles_right_triangle  (exact float equality instead of
         a tolerance-based comparison misses a legitimate right triangle)
    This class exists purely to demonstrate that the test suite is
    capable of catching real defects -- it is not itself part of the
    submitted solution.
    """
    classify_triangle = staticmethod(classify_triangle_buggy)


class TestDemoOutput(unittest.TestCase):
    """Tests for the print wrapper and the demo run."""

    def test_run_classify_triangle_prints_result(self):
        """Test: run_classify_triangle prints the call and its result."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            run_classify_triangle(3, 4, 5)
        self.assertEqual(
            buffer.getvalue().strip(),
            "classify_triangle(3, 4, 5) = Scalene Triangle, Right Triangle",
        )

    def test_demo_prints_one_line_per_sample(self):
        """Test: demo prints one result line for each sample triangle."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            demo()
        self.assertEqual(len(buffer.getvalue().strip().splitlines()), 9)


def demo():
    """Print the classification of a few sample triangles."""
    sample_triangles = [
        (3, 4, 5),        # scalene, right
        (5, 5, 5),        # equilateral
        (5, 5, 8),        # isosceles, not right
        (5, 5, 7.0710678118654755),  # isosceles, right (5-5-5*sqrt(2))
        (2, 3, 4),        # scalene, not right
        (1, 1, 2),        # degenerate -> not valid (a + b == c)
        (1, 2, 10),       # not valid, fails triangle inequality
        (-3, 4, 5),       # not valid, negative side
        (0, 4, 5),        # not valid, zero side
    ]
    for side_a, side_b, side_c in sample_triangles:
        run_classify_triangle(side_a, side_b, side_c)


if __name__ == "__main__":
    demo()
    print()
    unittest.main(verbosity=2)