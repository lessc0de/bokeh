import unittest
import numpy as np

from bokeh.properties import HasProps, Int, Array, String, Enum, Float, DataSpec, ColorSpec

class Basictest(unittest.TestCase):

    def test_simple_class(self):
        class Foo(HasProps):
            x = Int(12)
            y = String("hello")
            z = Array([1,2,3])
            s = String(None)

        f = Foo()
        self.assertEqual(f.x, 12)
        self.assertEqual(f.y, "hello")
        self.assert_(np.array_equal(np.array([1,2,3]), f.z))
        self.assertEqual(f.s, None)

        f.x = 18
        self.assertEqual(f.x, 18)

        f.y = "bar"
        self.assertEqual(f.y, "bar")

    def test_enum(self):
        class Foo(HasProps):
            x = Enum("blue", "red", "green")
            y = Enum("small", "medium", "large", default="tiny")

        f = Foo()
        self.assertEqual(f.x, "blue")
        self.assertEqual(f.y, "tiny")
        f.x = "red"
        with self.assertRaises(ValueError):
            f.x = "yellow"
        f.y = "small"
        with self.assertRaises(ValueError):
            # Even though this is the default, it is not a valid value
            # for the Enum.
            f.y = "tiny"

    def test_inheritance(self):
        class Base(HasProps):
            x = Int(12)
            y = String("hello")

        class Child(Base):
            z = Float(3.14)

        c = Child()
        self.assertEqual(frozenset(['x', 'y', 'z']), frozenset(c.properties()))
        self.assertEqual(c.y, "hello")

    def test_set(self):
        class Foo(HasProps):
            x = Int(12)
            y = Enum("red", "blue", "green")
            z = String("blah")

        f = Foo()
        self.assertEqual(f.x, 12)
        self.assertEqual(f.y, "red")
        self.assertEqual(f.z, "blah")
        f.set(**dict(x=20, y="green", z="hello"))
        self.assertEqual(f.x, 20)
        self.assertEqual(f.y, "green")
        self.assertEqual(f.z, "hello")
        with self.assertRaises(ValueError):
            f.set(y="orange")

    def test_no_parens(self):
        class Foo(HasProps):
            x = Int
            y = Int()
        f = Foo()
        self.assertEqual(f.x, f.y)
        f.x = 13
        self.assertEqual(f.x, 13)

    # def test_kwargs_init(self):
    #     class Foo(HasProps):
    #         x = String
    #         y = Int
    #         z = Float
    #     f = Foo(x = "hello", y = 14)
    #     self.assertEqual(f.x, "hello")
    #     self.assertEqual(f.y, 14)

    #     with self.assertRaises(TypeError):
    #         # This should raise a TypeError: object.__init__() takes no parameters
    #         g = Foo(z = 3.14, q = "blah")

class TestDataSpec(unittest.TestCase):

    def test_field(self):
        class Foo(HasProps):
            x = DataSpec("xfield")
        f = Foo()
        self.assertEqual(f.x, "xfield")
        self.assertDictEqual(Foo.__dict__["x"].to_dict(f), {"field": "xfield", "units": "data"})
        f.x = "my_x"
        self.assertEqual(f.x, "my_x")
        self.assertDictEqual(Foo.__dict__["x"].to_dict(f), {"field": "my_x", "units": "data"})

    def test_value(self):
        class Foo(HasProps):
            x = DataSpec("xfield")
        f = Foo()
        self.assertEqual(f.x, "xfield")
        f.x = 12
        self.assertEqual(f.x, 12)
        self.assertDictEqual(Foo.__dict__["x"].to_dict(f), {"value": 12, "units": "data"})
        f.x = 15
        self.assertEqual(f.x, 15)
        self.assertDictEqual(Foo.__dict__["x"].to_dict(f), {"value": 15, "units": "data"})
        f.x = dict(value=23, units="screen")
        self.assertDictEqual(Foo.__dict__["x"].to_dict(f), {"value": 23, "units": "screen"})
        # Setting defaults when there is a fixed value should do nothing, so verify this.
        # Also, setting a dict clobbers all fields that are not explicitly set, so "units"
        # gets reset back to the default value on the DataSpec, which is "data".
        f.x = dict(value=32, default=18)
        self.assertDictEqual(Foo.__dict__["x"].to_dict(f), {"value": 32, "units": "data"})

    def test_default(self):
        class Foo(HasProps):
            y = DataSpec("yfield", default=12)
        f = Foo()
        self.assertEqual(f.y, {"field": "yfield", "default": 12})
        self.assertDictEqual(Foo.__dict__["y"].to_dict(f), {"field": "yfield", "default": 12, "units": "data"})
        f.y = "y1"
        self.assertEqual(f.y, "y1")
        f.y = ("y2", 27)
        self.assertDictEqual(f.y, {"field": "y2", "default": 27, "units": "data"})
        self.assertDictEqual(Foo.__dict__["y"].to_dict(f), {"field": "y2", "default": 27, "units": "data"})
        # Once we set a concrete value, the default is ignored, because it is unused
        f.y = 32
        self.assertEqual(f.y, 32)
        self.assertDictEqual(Foo.__dict__["y"].to_dict(f), {"value": 32, "units": "data"})

    def test_multiple_instances(self):
        class Foo(HasProps):
            x = DataSpec("xfield", default=12)

        a = Foo()
        b = Foo()
        a.x = 13
        b.x = 14
        self.assertEqual(a.x, 13)
        self.assertEqual(b.x, 14)
        self.assertDictEqual(Foo.__dict__["x"].to_dict(a), {"value": 13, "units": "data"})
        self.assertDictEqual(Foo.__dict__["x"].to_dict(b), {"value": 14, "units": "data"})
        a.x = ("x2", 21)
        self.assertDictEqual(Foo.__dict__["x"].to_dict(a), {"field": "x2", "default": 21, "units": "data"})
        self.assertDictEqual(Foo.__dict__["x"].to_dict(b), {"value": 14, "units": "data"})
        b.x = {"field": "x3", "units": "screen", "default": 25}
        self.assertDictEqual(Foo.__dict__["x"].to_dict(a), {"field": "x2", "default": 21, "units": "data"})
        self.assertDictEqual(Foo.__dict__["x"].to_dict(b), {"field": "x3", "units": "screen", "default": 25})


class TestColorSpec(unittest.TestCase):

    def test_field(self):
        class Foo(HasProps):
            col = ColorSpec("colorfield")
        desc = Foo.__dict__["col"]
        f = Foo()
        self.assertEqual(f.col, "colorfield")
        self.assertDictEqual(desc.to_dict(f), {"field": "colorfield"})
        f.col = "myfield"
        self.assertEqual(f.col, "myfield")
        self.assertDictEqual(desc.to_dict(f), {"field": "myfield"})

    def test_field_default(self):
        class Foo(HasProps):
            col = ColorSpec("colorfield", default="red")
        desc = Foo.__dict__["col"]
        f = Foo()
        self.assertDictEqual(f.col, {"field": "colorfield", "default": "red"})
        self.assertDictEqual(desc.to_dict(f), {"field": "colorfield", "default": "red"})
        f.col = "myfield"
        self.assertDictEqual(f.col, {"field": "myfield", "default": "red"})
        self.assertDictEqual(desc.to_dict(f), {"field": "myfield", "default": "red"})

    def test_default_tuple(self):
        class Foo(HasProps):
            col = ColorSpec("colorfield", default=(128,255,124))
        desc = Foo.__dict__["col"]
        f = Foo()
        self.assertDictEqual(f.col, {"field": "colorfield", "default": (128, 255, 124)})
        self.assertDictEqual(desc.to_dict(f), {"field": "colorfield", "default": "rgb(128, 255, 124)"})

    def test_fixed_value(self):
        class Foo(HasProps):
            col = ColorSpec("gray")
        desc = Foo.__dict__["col"]
        f = Foo()
        self.assertEqual(f.col, "gray")
        self.assertDictEqual(desc.to_dict(f), {"value": "gray"})

    def test_named_value(self):
        class Foo(HasProps):
            col = ColorSpec("colorfield")
        desc = Foo.__dict__["col"]
        f = Foo()

        f.col = "red"
        self.assertEqual(f.col, "red")
        self.assertDictEqual(desc.to_dict(f), {"value": "red"})
        f.col = "forestgreen"
        self.assertEqual(f.col, "forestgreen")
        self.assertDictEqual(desc.to_dict(f), {"value": "forestgreen"})

    def test_named_value_set_none(self):
        class Foo(HasProps):
            col = ColorSpec("colorfield")
        desc = Foo.__dict__["col"]
        f = Foo()
        f.col = None
        self.assertDictEqual(desc.to_dict(f), {"value": None})

    def test_named_color_overriding_default(self):
        class Foo(HasProps):
            col = ColorSpec("colorfield", default="blue")
        desc = Foo.__dict__["col"]
        f = Foo()
        f.col = "forestgreen"
        self.assertEqual(f.col, "forestgreen")
        self.assertDictEqual(desc.to_dict(f), {"value": "forestgreen"})
        f.col = "myfield"
        self.assertDictEqual(f.col, {"field": "myfield", "default": "blue"})
        self.assertDictEqual(desc.to_dict(f), {"field": "myfield", "default": "blue"})

    def test_hex_value(self):
        class Foo(HasProps):
            col = ColorSpec("colorfield")
        desc = Foo.__dict__["col"]
        f = Foo()
        f.col = "#FF004A"
        self.assertEqual(f.col, "#FF004A")
        self.assertDictEqual(desc.to_dict(f), {"value": "#FF004A"})
        f.col = "myfield"
        self.assertEqual(f.col, "myfield")
        self.assertDictEqual(desc.to_dict(f), {"field": "myfield"})

    def test_tuple_value(self):
        class Foo(HasProps):
            col = ColorSpec("colorfield")
        desc = Foo.__dict__["col"]
        f = Foo()
        f.col = (128, 200, 255)
        self.assertEqual(f.col, (128, 200, 255))
        self.assertDictEqual(desc.to_dict(f), {"value": "rgb(128, 200, 255)"})
        f.col = "myfield"
        self.assertEqual(f.col, "myfield")
        self.assertDictEqual(desc.to_dict(f), {"field": "myfield"})
        f.col = (100, 150, 200, 0.5)
        self.assertEqual(f.col, (100, 150, 200, 0.5))
        self.assertDictEqual(desc.to_dict(f), {"value": "rgba(100, 150, 200, 0.5)"})

    def test_set_dict(self):
        class Foo(HasProps):
            col = ColorSpec("colorfield")
        desc = Foo.__dict__["col"]
        f = Foo()
        f.col = {"field": "myfield", "default": "#88FF00"}
        self.assertDictEqual(f.col, {"field": "myfield", "default": "#88FF00"})

        f.col = "field2"
        self.assertEqual(f.col, "field2")
        self.assertDictEqual(desc.to_dict(f), {"field": "field2"})

if __name__ == "__main__":
    unittest.main()
