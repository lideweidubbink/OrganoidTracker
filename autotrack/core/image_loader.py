from typing import Tuple, Optional
from numpy import ndarray

from autotrack.core import TimePoint


class ImageResolution:
    """Represents the resolution of a 3D image."""
    pixel_size_zyx_um: Tuple[float, float, float]

    def __init__(self, pixel_size_x_um: float, pixel_size_y_um: float, pixel_size_z_um: float):
        self.pixel_size_zyx_um = (pixel_size_z_um, pixel_size_y_um, pixel_size_x_um)


class ImageLoader:
    """Responsible for loading all images in an experiment."""

    def load_3d_image(self, time_point: TimePoint) -> Optional[ndarray]:
        """Loads an image, usually from disk. Returns None if there is no image for this time point."""
        return None

    def get_resolution(self) -> ImageResolution:
        """Gets the resolution of an image, or raises ValueError if unknown."""
        raise ValueError()

    def unwrap(self) -> "ImageLoader":
        """If this loader is a wrapper around another loader, this method returns one loader below. Otherwise, it
        returns self.
        """
        return self

