"""Extra markers used to describe the linking data. For example, you can mark the end of a lineage as a cell death."""

from enum import Enum
from typing import Optional, Iterable

from autotrack.core.links import Links
from autotrack.core.positions import Position
from autotrack.linking_analysis.errors import Error


class EndMarker(Enum):
    DEAD = 1
    OUT_OF_VIEW = 2

    def get_display_name(self):
        """Gets a user-friendly display name."""
        return self.name.lower().replace("_", " ")


class StartMarker(Enum):
    GOES_INTO_VIEW = 1
    UNSURE = 2

    def get_display_name(self):
        """Gets a user-friendly display name."""
        return self.name.lower().replace("_", " ")


def get_track_end_marker(links: Links, position: Position) -> Optional[EndMarker]:
    """Gets a death marker, which provides a reason why the cell lineage ended."""
    ending_str = links.get_position_data(position, "ending")
    if ending_str is None:
        return None

    return EndMarker[ending_str.upper()]


def set_track_end_marker(links: Links, position: Position, end_marker: Optional[EndMarker]):
    """Sets a reason why the track ended at the given point."""
    if end_marker is None:
        links.set_position_data(position, "ending", None)
    else:
        links.set_position_data(position, "ending", end_marker.name.lower())


def find_death_positions(links: Links) -> Iterable[Position]:
    """Gets all positions that were marked as dead."""
    death_marker = EndMarker.DEAD.name.lower()
    for position, ending_marker in links.find_all_positions_with_data("ending"):
        if ending_marker == death_marker:
            yield position


def get_track_start_marker(links: Links, position: Position) -> Optional[StartMarker]:
    """Gets the appearance marker. This is used to explain why a cell appeared out of thin air."""
    starting_str = links.get_position_data(position, "starting")
    if starting_str is None:
        return None

    return StartMarker[starting_str.upper()]


def set_track_start_marker(links: Links, position: Position, start_marker: Optional[StartMarker]):
    """Sets a reason why the track ended at the given point."""
    if start_marker is None:
        links.set_position_data(position, "starting", None)
    else:
        links.set_position_data(position, "starting", start_marker.name.lower())


def find_errored_positions(links: Links) -> Iterable[Position]:
    """Gets all positions that have a (non suppressed) error."""

    with_error_marker = links.find_all_positions_with_data("error")
    for position, error_number in with_error_marker:
        if links.get_position_data(position, "suppressed_error") == error_number:
            continue # Error was suppressed

        yield position


def get_error_marker(links: Links, position: Position) -> Optional[Error]:
    """Gets the error marker for the given link, if any. Returns None if the error has been suppressed using
    suppress_error_marker."""
    error_number = links.get_position_data(position, "error")
    if error_number is None:
        return None

    if links.get_position_data(position, "suppressed_error") == error_number:
        return None  # Error was suppressed
    return Error(error_number)


def suppress_error_marker(links: Links, position: Position, error: Error):
    """Suppresses an error. Even if set_error_marker is called afterwards, the error will not show up in
    get_error_marker."""
    links.set_position_data(position, "suppressed_error", error.value)


def is_error_suppressed(links: Links, position: Position, error: Error) -> bool:
    """Returns True if the given error is suppressed. If another type of error is suppressed, this method returns
    False."""
    return links.get_position_data(position, "suppressed_error") == error.value


def set_error_marker(links: Links, position: Position, error: Optional[Error]):
    """Sets an error marker for the given position."""
    if error is None:
        links.set_position_data(position, "error", None)
    else:
        links.set_position_data(position, "error", error.value)
