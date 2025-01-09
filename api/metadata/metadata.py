from PIL import Image
import piexif


def read_gps_coordinates(image_path):
    try:
        # Open the image
        img = Image.open(image_path)

        # Load EXIF data
        exif_dict = piexif.load(img.info.get("exif", b""))

        # Extract GPS data
        gps_data = exif_dict.get("GPS", {})
        if not gps_data:
            print("No GPS data found in the image.")
            return None

        # Decode GPS latitude and longitude
        def from_deg(value):
            degrees = value[0][0] / value[0][1]
            minutes = value[1][0] / value[1][1]
            seconds = value[2][0] / value[2][1]
            return degrees + (minutes / 60) + (seconds / 3600)

        lat = from_deg(gps_data.get(piexif.GPSIFD.GPSLatitude, [(0, 1), (0, 1), (0, 1)]))
        lon = from_deg(gps_data.get(piexif.GPSIFD.GPSLongitude, [(0, 1), (0, 1), (0, 1)]))

        # Get latitude and longitude reference (N/S, E/W)
        lat_ref = gps_data.get(piexif.GPSIFD.GPSLatitudeRef, b'N').decode()
        lon_ref = gps_data.get(piexif.GPSIFD.GPSLongitudeRef, b'E').decode()

        # Adjust for hemisphere
        if lat_ref == "S":
            lat = -lat
        if lon_ref == "W":
            lon = -lon

        print(f"Latitude: {lat}, Longitude: {lon}")
        return lat, lon
    except Exception as e:
        print(f"Error reading GPS coordinates: {e}")
        return None

def set_gps_coordinates(image_path, lat, lon):
    # Convert lat/lon to the EXIF format
    def to_deg(value, ref):
        degrees = int(value)
        minutes = int((value - degrees) * 60)
        seconds = round((value - degrees - minutes / 60) * 3600 * 10000)
        return [(degrees, 1), (minutes, 1), (seconds, 10000)], ref

    lat_ref = "N" if lat >= 0 else "S"
    lon_ref = "E" if lon >= 0 else "W"

    lat_deg, lon_deg = to_deg(abs(lat), lat_ref), to_deg(abs(lon), lon_ref)

    # Load image and its EXIF
    img = Image.open(image_path)
    try:
        exif_dict = piexif.load(img.info.get("exif", b""))
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}

    # Set GPS values
    exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = lat_deg[0]
    exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = lat_deg[1]
    exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = lon_deg[0]
    exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = lon_deg[1]

    # Save changes
    exif_bytes = piexif.dump(exif_dict)
    img.save(image_path, "jpeg", exif=exif_bytes)
    print("GPS coordinates updated successfully!")


