# This script is used to extract x,y,z positions of all cells for every time point from the manual tracking data
# Input: directory of track_xxxxx.p files
# Output: single JSON file

from manual_tracking import positions_extractor, links_extractor
from imaging import io

# PARAMETERS
_name = "multiphoton.organoids.17-07-28_weekend_H2B-mCherry.nd799xy08"
_input_dir = "../Results/" + _name + "/Manual tracks/"
_output_file_positions = "../Results/" + _name + "/Positions/Manual.json"
_output_file_tracks = "../Results/" + _name + "/Manual links.json"
_min_time_point = 0
_max_time_point = 5000  # Organoid moved position here
# END OF PARAMETERS


positions_extractor.extract_positions(_input_dir, _output_file_positions, min_time_point=_min_time_point, max_time_point=_max_time_point)
io.save_links_to_json(
    links_extractor.extract_from_tracks(_input_dir, min_time_point=_min_time_point, max_time_point=_max_time_point),
    _output_file_tracks)
