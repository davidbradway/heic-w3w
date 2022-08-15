from exif import Image
import secrets
import what3words

geocoder = what3words.Geocoder(secrets.W3W_API_KEY)

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == 'S' or ref == 'W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees


if __name__ == "__main__":
    filename = 'JpgFolder/sample.jpg'

    with open(filename, 'rb') as src:
        img = Image(src)

    lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
    lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)

    res = geocoder.convert_to_3wa(what3words.Coordinates(lat, lon))
    print(res)

