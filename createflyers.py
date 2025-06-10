from wand.image import Image as WandImage
from exif import Image as ExifImage
from borb.pdf import (
    Document,
    Page,
    SingleColumnLayout,
    PageLayout,
    Paragraph,
    PDF,
    Alignment,
    ChunkOfText,
    InlineFlow,
    Barcode,
    BarcodeType,
    UnorderedList,
    HexColor,
    Image as BorbImage,
)
from borb.pdf.canvas.layout.annotation.remote_go_to_annotation import (
    RemoteGoToAnnotation,
)
import fitz

from decimal import Decimal
from pathlib import Path
import requests
import os

from names import *


def decimal_coords(coords, ref):
    """
    Convert from DMS (degrees, minutes, and seconds) to decimal degrees.

    Parameters:
    coords (List): (degrees, minutes, seconds)
    ref (String): "N"/"S"/"E"/"W"

    Returns:
    float: decimal degrees
    """

    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def convertToJpg(HeicFolder, filename, JpgFolder):
    """
    Convert a HEIC file to JPG and copy it to a new folder.

    Parameters:
    HeicFolder (String): folder where HEIC file is
    filename (String): name of HEIC file to convert
    JpgFolder (String): folder where converted JPG file should be written

    Returns:
    String: whole path to converted JPG file
    """

    SourceFile = os.path.join(HeicFolder, filename)
    newfilename = filename.replace(".HEIC", ".jpg")
    newfilename = newfilename.replace(".heic", ".jpg")
    TargetFile = os.path.join(JpgFolder, newfilename)
    if not os.path.exists(TargetFile):
        img = WandImage(filename=SourceFile)
        img.format = "jpg"
        img.save(filename=TargetFile)
        img.close()
    return TargetFile


def getLatLong(TargetFile):
    """
    Get the Latitude and Longitude for a target JPG file from its EXIF location data.

    Parameters:
    TargetFile (String): whole path to JPG file

    Returns:
    Tuple: (lat, long), indicating location where picture was taken
    """

    with open(TargetFile, "rb") as src:
        img = ExifImage(src)
        lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
        long = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
        return (lat, long)


def makeFlyer(JpgFile, name, lat, long, OutFolder, OutFile):
    """
    Create a PDF flyer for a given photo, name, and location

    Parameters:
    JpgFile (String): path filename of the JPG file for the flyer image
    name (String): name to be given to the flexpost, from the names.py file
    lat (Double): latitude of the flexpost, from the JPG EXIF GPS data
    long (Double): longitude of the flexpost, from the JPG EXIF GPS data
    OutFolder (String): path to the folder where output files should be written
    OutFile (String): name to be used for output PDF filename

    Returns:
    None
    """

    # create Document
    doc: Document = Document()

    # create Page
    page: Page = Page()

    # add Page to Document
    doc.add_page(page)

    # set a PageLayout
    layout: PageLayout = SingleColumnLayout(page)
    flow1: InlineFlow = InlineFlow()
    flow2: InlineFlow = InlineFlow()

    # Title
    layout.add(
        Paragraph(
            f'Flexpost "{name}"',
            font_color=HexColor("#003087"),
            font_size=Decimal(38),
            horizontal_alignment=Alignment.CENTERED,
        )
    )
    # Subtitle
    layout.add(
        Paragraph(
            "Unofficial Erwin Road Adopt-a-Flexpost Program",
            font_color=HexColor("#003087"),
            font_size=Decimal(22),
            horizontal_alignment=Alignment.CENTERED,
        )
    )

    link0: LayoutElement = Paragraph(
        f"Location: {lat:.6f}, {long:.6f}",
        font_color=HexColor("#003087"),
        font_size=Decimal(18),
        horizontal_alignment=Alignment.CENTERED,
    )
    layout.add(link0)
    annot0: RemoteGoToAnnotation = RemoteGoToAnnotation(
        link0.get_previous_paint_box(), uri=f"https://www.google.com/maps/search/?api=1&query={lat:.6f},{long:.6f}"
    )
    page.add_annotation(annot0)

    with WandImage(filename=JpgFile) as img:
        width, height = img.width, img.height

    layout.add(
        BorbImage(
            Path(JpgFile),
            width=Decimal(300),
            height=Decimal(height / width * 300.0),
            horizontal_alignment=Alignment.CENTERED,
        )
    )

    layout.add(
        Paragraph(
            "Responsibilities:",
            font_size=Decimal(16),
            horizontal_alignment=Alignment.CENTERED,
        )
    )

    layout.add(
        UnorderedList()
        .add(Paragraph("Clear trash and debris quarterly"))
        .add(Paragraph("Request maintenance via Durham OneCall"))
        .add(Paragraph("Transfer duties if unable to do upkeep"))
    )

    # QR Code
    qr_code: LayoutElement = Barcode(
        data=f"https://www.google.com/maps/search/?api=1&query={lat:.6f},{long:.6f}",
        width=Decimal(64),
        height=Decimal(64),
        type=BarcodeType.QR,
    )
    flow1.add(qr_code)
    link1 = ChunkOfText(
        f"google.com/maps/search/?api=1&query={lat:.6f},{long:.6f}",
        vertical_alignment=Alignment.BOTTOM,
        font_color=HexColor("0000FF"),
    )
    flow1.add(link1)
    # add in-line text and link
    flow1.add(ChunkOfText(" --Thanks! ", vertical_alignment=Alignment.BOTTOM))
    layout.add(flow1)
    annot1: RemoteGoToAnnotation = RemoteGoToAnnotation(
        link1.get_previous_paint_box(), uri=f"https://www.google.com/maps/search/?api=1&query={lat:.6f},{long:.6f}"
    )
    page.add_annotation(annot1)

    # store as PDF
    with open(os.path.join(OutFolder, OutFile + ".pdf"), "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)


def convertToPng(OutFolder, OutFile):
    """
    Convert output PDF to PNG, and save in the same folder.

    Parameters:
    OutFolder (String): path to output file folder
    OutFile (String): filename without extension (.PDF -> .PNG)

    Returns:
    None
    """

    # convert to PNG
    with fitz.open(os.path.join(OutFolder, OutFile + ".pdf")) as pdf:
        for page in pdf:
            zoom = 2  # zoom factor
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            pix.save(os.path.join(OutFolder, OutFile + ".png"))


def main():
    """Main function which loops through the whole HEIC file folder and makes the output files."""

    HeicFolder = "HeicFolder"
    JpgFolder = "JpgFolder"
    OutFolder = "OutFolder"

    i = 0
    print(f'"JpgPath", "Latitude", "Longitude", "OutputName"')
    for filename in os.listdir(HeicFolder):
        # for each Heic file in the folder
        if filename.endswith(".heic") or filename.endswith(".HEIC"):
            TargetFile = convertToJpg(HeicFolder, filename, JpgFolder)
            (lat, long) = getLatLong(TargetFile)
            name = names[i]
            OutFile = f"{i:02}-{name}"
            print(f'"{TargetFile}", "{lat}","{long}", "{OutFile}"')
            makeFlyer(TargetFile, name, lat, long, OutFolder, OutFile)
            convertToPng(OutFolder, OutFile)
            i = i + 1


if __name__ == "__main__":
    main()
