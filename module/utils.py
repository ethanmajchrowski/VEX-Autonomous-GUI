bg_width = 2000
WORLD_SIZE = int(1835*2)
def screen_to_world(point, zoom, offset):
    x, y = point
    offset_x, offset_y = offset
    x = ((x - offset_x) / zoom / bg_width) * WORLD_SIZE - WORLD_SIZE // 2
    y = (((y - offset_y) / zoom / bg_width) * WORLD_SIZE - WORLD_SIZE // 2)
    return x, -y

def world_to_screen(point, zoom, offset):
    """Convert world coordinates to screen coordinates with (0,0) at the center."""
    x, y = point
    y *= -1
    offset_x, offset_y = offset
    
    # Shift the world coordinates to center at (0, 0) for the map
    x += WORLD_SIZE // 2
    y += WORLD_SIZE // 2

    # Scale the world coordinates to the screen (applying zoom and panning)
    screen_x = ((x / WORLD_SIZE) * bg_width * zoom) + offset_x
    screen_y = ((y / WORLD_SIZE) * bg_width * zoom) + offset_y
    
    return int(screen_x), int(screen_y)
