def parse_image_dimensions(in_stream):
    for line in in_stream:
        if not line.isspace():
            width, height = map(lambda dimension: min(max(1, int(dimension)), 10000), line.split())
            break
    return width, height
