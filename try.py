import what3words
import secrets

geocoder = what3words.Geocoder(secrets.W3W_API_KEY)

res = geocoder.convert_to_3wa(what3words.Coordinates(36.005274, -78.924236))
print(res)

res = geocoder.convert_to_coordinates('prom.cape.pump')
print(res)
