#!/usr/bin/env python3

"""This script is used to detect the shapes of cells, starting from JSON position files and an image folder. It gives a
single multiveriate Gaussian as output for each image. This is more accurate than just fitting a stack of ellipses, as
is done in another script. Unfortunately, this script is also much slower.

Parameters: (all sizes are in pixels)

- threshold_block_size: length and/or height of the 2d square used for the adaptive threshold
- distance_transform_smooth_size: smoothing size (must be odd) used for the distance transform
- gaussian_fit_smooth_size: smoothing size (must be odd) used for fitting Gaussians to the image. The more the image
  already looks like Gaussians, the smaller this size can be
- min_segmentation_distance: used for recognizing cell boundaries in a watershed transform
"""
from autotrack.imaging import tifffolder, io
from autotrack.config import ConfigFile
from autotrack.particle_detection import gaussian_detector_for_experiment

# PARAMETERS
from autotrack.core.image_loader import ImageResolution
from autotrack.core.experiment import Experiment

print("Hi! Configuration file is stored at " + ConfigFile.FILE_NAME)
config = ConfigFile("detect_gaussian_shapes")
_images_folder = config.get_or_default("images_folder", "./", store_in_defaults=True)
_images_format = config.get_or_prompt("images_pattern", "What are the image file names? (Use %03d for a three digits "
                                                        "representing the time)", store_in_defaults=True)
_min_time_point = int(config.get_or_default("min_time_point", str(1), store_in_defaults=True))
_max_time_point = int(config.get_or_default("max_time_point", str(9999), store_in_defaults=True))
_pixel_size_x_um = float(config.get_or_default("pixel_size_x_um", str(0.32), store_in_defaults=True))
_pixel_size_y_um = float(config.get_or_default("pixel_size_y_um", str(0.32), store_in_defaults=True))
_pixel_size_z_um = float(config.get_or_default("pixel_size_z_um", str(2), store_in_defaults=True))
_time_point_duration_m = float(config.get_or_default("time_point_duration_m", str(12), store_in_defaults=True))
_positions_input_file = config.get_or_default("positions_input_file", "Automatic analysis/Positions/Manual.json")
_positions_output_file = config.get_or_default("positions_and_fit_output_file", "Automatic analysis/Positions/Gaussian fit.json")

_threshold_block_size = int(config.get_or_default("threshold_block_size", str(51)))
_distance_transform_smooth_size = int(config.get_or_default("distance_transform_smooth_size", str(21)))
_gaussian_fit_smooth_size = int(config.get_or_default("gaussian_fit_smooth_size", str(7)))
_min_segmentation_distance_x = int(config.get_or_default("min_segmentation_distance_x", str(11)))
_min_segmentation_distance_y = int(config.get_or_default("min_segmentation_distance_y", str(11)))
_min_segmentation_distance_z = int(config.get_or_default("min_segmentation_distance_z", str(3)))
config.save_and_exit_if_changed()
# END OF PARAMETERS

experiment = Experiment()
print("Loading cell positions...")
io.load_positions_and_shapes_from_json(experiment, _positions_input_file, min_time_point=_min_time_point,
                                       max_time_point=_max_time_point)
print("Discovering images...")
resolution = ImageResolution(_pixel_size_x_um, _pixel_size_y_um, _pixel_size_z_um, _time_point_duration_m)
tifffolder.load_images_from_folder(experiment, _images_folder, _images_format,
                                   min_time_point=_min_time_point, max_time_point=_max_time_point)
experiment.image_resolution(resolution)
print("Running detection...")
_min_segmentation_distance = (_min_segmentation_distance_x, _min_segmentation_distance_y, _min_segmentation_distance_z)
gaussian_detector_for_experiment.perform_for_experiment(experiment, threshold_block_size=_threshold_block_size,
                                                        distance_transform_smooth_size=_distance_transform_smooth_size,
                                                        minimal_distance=_min_segmentation_distance,
                                                        gaussian_fit_smooth_size=_gaussian_fit_smooth_size)
io.save_positions_and_shapes_to_json(experiment, _positions_output_file)


