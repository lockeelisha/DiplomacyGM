import re
from xml.etree.ElementTree import Element
import numpy as np


class TransGL3:
    """Class to handle coordinate transformations using a 3x3 matrix.
    This parses transformation strings found in SVG elements, and turns them into a matrix."""

    def __init__(self, transform_string: str | Element | None = None):
        self.matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float)

        if transform_string is None:
            return
        if not isinstance(transform_string, str):
            transform_string = transform_string.get("transform", "")
        transform_string = transform_string.strip()

        pattern = re.compile(r"(matrix|translate|rotate|scale)\(([^)]*)\)")
        # We have to apply the transformation in right-to-left order
        for match in pattern.finditer(transform_string):
            func = match.group(1)
            args = [float(x) for x in re.split(r"[,\s]+", match.group(2).strip())]

            if func == "matrix":
                if len(args) != 6:
                    raise ValueError(
                        f"Malformed matrix transformation: {transform_string}"
                    )
                m = np.array(
                    [
                        [args[0], args[1], 0],
                        [args[2], args[3], 0],
                        [args[4], args[5], 1],
                    ]
                )
            elif func == "translate":
                args.append(0)
                m = np.array([[1, 0, 0], [0, 1, 0], [args[0], args[1], 1]])
            elif func == "rotate":
                angle = args[0] * np.pi / 180
                cos = np.cos(angle)
                sin = np.sin(angle)
                args = args + [0, 0]
                cx, cy = args[1], args[2]
                pre = np.array([[1, 0, 0], [0, 1, 0], [-cx, -cy, 1]])
                rot = np.array([[cos, sin, 0], [-sin, cos, 0], [0, 0, 1]])
                post = np.array([[1, 0, 0], [0, 1, 0], [cx, cy, 1]])
                m = pre @ rot @ post
            elif func == "scale":
                m = np.array([[args[0], 0, 0], [0, args[-1], 0], [0, 0, 1]])
            else:
                raise ValueError(f"Unknown transformation: {transform_string}")

            self.matrix = m @ self.matrix

    def init(
        self,
        x_dx: float = 1,
        y_dy: float = 1,
        x_dy: float = 0,
        y_dx: float = 0,
        x_c: float = 0,
        y_c: float = 0,
    ):
        """Creates a transformation matrix directly from the values, rather than parsing a string."""
        self.matrix = np.array([[x_dx, y_dx, 0], [x_dy, y_dy, 0], [x_c, y_c, 1]])
        return self

    def transform(self, point: complex) -> complex:
        """Applies the transformation to a point."""
        point_array = np.array([point.real, point.imag, 1])
        transformed = point_array @ self.matrix
        return complex(transformed[0], transformed[1])

    # represents a convolution
    # (t1 * t2).transform(p) == t2.transform(t1.transform(p))
    def __mul__(self, other):
        out = TransGL3()
        out.matrix = self.matrix @ other.matrix
        return out

    def __str__(self):
        return f"matrix({','.join(map(str, self.matrix[:, :2].flatten()))})"
