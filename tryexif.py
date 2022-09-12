from exif import Image
import secrets
import what3words
import os

geocoder = what3words.Geocoder(secrets.W3W_API_KEY)

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == 'S' or ref == 'W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees


if __name__ == '__main__':
    SourceFolder = 'JpgFolder'

    for file in os.listdir(SourceFolder):
        if file.endswith('.jpg'):
            SourceFile = os.path.join(SourceFolder, file)

            with open(SourceFile, 'rb') as src:
                img = Image(src)

            lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
            lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)

            res = geocoder.convert_to_3wa(what3words.Coordinates(lat, lon))
            print(f"{file} {lat}/{lon} - {res['words']}")

