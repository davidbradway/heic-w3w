from wand.image import Image as WandImage
from exif import Image as ExifImage
import what3words
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
from borb.pdf.canvas.layout.emoji.emoji import Emojis
from borb.pdf.canvas.layout.annotation.remote_go_to_annotation import (
    RemoteGoToAnnotation,
)
import fitz

from decimal import Decimal
from pathlib import Path
import requests
import os

from names import *

geocoder = what3words.Geocoder(os.environ["W3W_API_KEY"])


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


def getW3w(TargetFile):
    """
    Get the What3Words location for a target JPG file from its EXIF location data.

    Parameters:
    TargetFile (String): whole path to JPG file

    Returns:
    String: three words delimited by periods, indicating location where picture was taken
    """

    with open(TargetFile, "rb") as src:
        img = ExifImage(src)
        lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
        lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
        res = geocoder.convert_to_3wa(what3words.Coordinates(lat, lon))
        w3w = f"{res['words']}"
    return w3w


def makeFlyer(JpgFile, name, w3w, OutFolder, OutFile):
    """
    Create a PDF flyer for a given photo, name, and location

    Parameters:
    JpgFile (String):
    name (String): name to be given to the flexpost, from the names.py file
    w3w (String): location of the flexpost, from the JPG EXIF GPS data
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
            f'Flexpost "Name": {name}',
            font_color=HexColor("#003087"),
            font_size=Decimal(36),
            horizontal_alignment=Alignment.CENTERED,
        )
    )
    # Subtitle
    layout.add(
        Paragraph(
            "Officially Unofficial Erwin Road Adopt-A-Flexpost Program",
            font_color=HexColor("#003087"),
            font_size=Decimal(24),
            horizontal_alignment=Alignment.CENTERED,
        )
    )

    link0: LayoutElement = Paragraph(
        f"What3Words Location: ///{w3w}",
        font_color=HexColor("#003087"),
        font_size=Decimal(20),
        horizontal_alignment=Alignment.CENTERED,
    )
    layout.add(link0)
    annot0: RemoteGoToAnnotation = RemoteGoToAnnotation(
        link0.get_previous_paint_box(), uri=f"http://w3w.co/{w3w}"
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
            "Adoptee Responsibilities:",
            font_size=Decimal(18),
            # horizontal_alignment=Alignment.CENTERED,
        )
    )

    layout.add(
        UnorderedList()
        .add(Paragraph("Clear trash and debris quarterly"))
        .add(Paragraph("Cut back weeds and bushes annually"))
        .add(Paragraph("Report maintenance needs to Durham OneCall"))
        .add(Paragraph("Transfer ownership if unable to meet obligations"))
    )

    # QR Code
    qr_code: LayoutElement = Barcode(
        data=f"http://w3w.co/{w3w}",
        width=Decimal(64),
        height=Decimal(64),
        type=BarcodeType.QR,
    )
    flow1.add(qr_code)
    link1: LayoutElement = ChunkOfText(
        f"w3w.co/{w3w}",
        vertical_alignment=Alignment.BOTTOM,
        font_color=HexColor("0000FF"),
    )
    flow1.add(link1)
    # add in-line text and emoji
    flow1.add(ChunkOfText(" --Thanks! ", vertical_alignment=Alignment.BOTTOM))
    layout.add(flow1)
    annot1: RemoteGoToAnnotation = RemoteGoToAnnotation(
        link1.get_previous_paint_box(), uri=f"http://w3w.co/{w3w}"
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
    print(f'"JpgPath", "What3Words", "OutputName"')
    for filename in os.listdir(HeicFolder):
        # for each Heic file in the folder
        if filename.endswith(".heic") or filename.endswith(".HEIC"):
            TargetFile = convertToJpg(HeicFolder, filename, JpgFolder)
            w3w = getW3w(TargetFile)
            name = names[i]
            OutFile = f"{i:02}-{name}"
            print(f'"{TargetFile}", "{w3w}", "{OutFile}"')
            makeFlyer(TargetFile, name, w3w, OutFolder, OutFile)
            convertToPng(OutFolder, OutFile)
            i = i + 1


if __name__ == "__main__":
    main()
