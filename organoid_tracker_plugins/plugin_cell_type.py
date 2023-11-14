from organoid_tracker.core.marker import Marker
from organoid_tracker.core.position import Position

def get_markers():
    return [
        #position, label, name, color code
        Marker([Position], "STEM", "Stem cell", (182, 1, 1)), #red
        Marker([Position], "GOBLET", "Goblet cell", (126, 255, 64)), #green
        Marker([Position], "PANETH", "Paneth cell", (65, 67, 254)), #blue
        Marker([Position], "TUFT", "Tuft cell", (250, 69, 254)),  #pink
        Marker([Position], "ENTEROCYTE", "Enterocyte cell", (252, 251, 73)),  #yellow
        Marker([Position], "ENTEROENDOCRINE", "Enteroendocrine cells", (72, 0, 105))  #purple
    ]
