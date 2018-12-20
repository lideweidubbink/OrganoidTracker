from typing import Optional

from autotrack.core.links import LinkingTrack, Links
from autotrack.linking_analysis import linking_markers
from autotrack.linking_analysis.linking_markers import EndMarker


def get_division_count_in_lineage(starting_track: LinkingTrack, links: Links, last_time_point_number: int
                                  ) -> Optional[int]:
    """Gets how many divisions there are in the lineage starting at the given cell. If the cell does not divide, then
    this method will return 0. If a lineage ended before the end of the experiment and it was not because of an actual
    death, then it is assumed that the cell went out of view, and that no reliable clonal size can be calculated. In
    that case, this function returns None.

    Any divisions occuring after last_time_point_number are ignored. This is useful if you want to look at only a
    limited time point window.
    """
    division_count = 0
    for track in starting_track.find_all_descending_tracks(include_self=True):
        if track.min_time_point_number() > last_time_point_number:
            # Ignore this track, it is past the end of the time point window
            continue
        if not track.get_next_tracks() \
                and linking_markers.get_track_end_marker(links, track.find_last_position()) != EndMarker.DEAD\
                and track.max_time_point_number() < last_time_point_number:
            return None  # Don't know why this track ended, division count in lineage is uncertain
        if track.max_time_point_number() < last_time_point_number and len(track.get_next_tracks()) > 1:
            division_count += 1
    return division_count
