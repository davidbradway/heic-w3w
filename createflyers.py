from wand.image import Image as WandImage
from exif import Image as ExifImage
import what3words
from borb.pdf import Document
from borb.pdf import Page
from borb.pdf import SingleColumnLayout
from borb.pdf import PageLayout
from borb.pdf import Paragraph
from borb.pdf import PDF
from borb.pdf import Alignment
from borb.pdf import Image as BorbImage
from borb.pdf import ChunkOfText
from borb.pdf import InlineFlow
from borb.pdf import Barcode, BarcodeType
from borb.pdf import TableCell
from borb.pdf import FixedColumnWidthTable
from borb.pdf import UnorderedList
from borb.pdf import HexColor
from borb.pdf.canvas.layout.emoji.emoji import Emojis
import fitz

from decimal import Decimal
from pathlib import Path
import requests
import os

from names import *
import secrets


geocoder = what3words.Geocoder(secrets.W3W_API_KEY)


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def make_flyer(JpgFile, name, w3w, OutFolder, OutFile):
    # create Document
    doc: Document = Document()

    # create Page
    page: Page = Page()

    # add Page to Document
    doc.add_page(page)

    # set a PageLayout
    layout: PageLayout = SingleColumnLayout(page)
    flow: InlineFlow = InlineFlow()

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
            "Erwin Road Adopt-A-Flexpost Program",
            font_color=HexColor("#003087"),
            font_size=Decimal(24),
            horizontal_alignment=Alignment.CENTERED,
        )
    )

    layout.add(
        Paragraph(
            f"What3Words Location: ///{w3w}",
            font_color=HexColor("#003087"),
            font_size=Decimal(18),
            horizontal_alignment=Alignment.CENTERED,
        )
    )

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

    # add a Paragraph
    flow.add(ChunkOfText("Thanks! "))
    flow.add(Emojis.BIKE.value)
    layout.add(flow)

    # QR Code
    qr_code: LayoutElement = Barcode(
        data="https://sites.duke.edu/davidbradway/adopt-a-flexpost",
        width=Decimal(96),
        height=Decimal(96),
        type=BarcodeType.QR,
    )
    # add a QR code
    layout.add(qr_code)

    # store as PDF
    with open(os.path.join(OutFolder, filename + ".pdf"), "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)

    # convert to PNG
    with fitz.open(os.path.join(OutFolder, filename + ".pdf")) as pdf:
        for page in pdf:
            zoom = 2  # zoom factor
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            pix.save(os.path.join(OutFolder, filename + ".png"))


def main():

    HeicFolder = "HeicFolder"
    JpgFolder = "JpgFolder"
    OutFolder = "OutFolder"

    i = 0
    print(f'"JpgFileName", "OutputName", "What3Words"')
    for filename in os.listdir(HeicFolder):
        if filename.endswith(".heic") or filename.endswith(".HEIC"):
            SourceFile = os.path.join(HeicFolder, filename)
            newfilename = filename.replace(".HEIC", ".jpg")
            newfilename = newfilename.replace(".heic", ".jpg")
            TargetFile = os.path.join(JpgFolder, newfilename)
            if not os.path.exists(TargetFile):
                img = WandImage(filename=SourceFile)
                img.format = "jpg"
                img.save(filename=TargetFile)
                img.close()

            with open(TargetFile, "rb") as src:
                img = ExifImage(src)
                lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
                lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
                res = geocoder.convert_to_3wa(what3words.Coordinates(lat, lon))
                w3w = f"{res['words']}"

            name = names[i]
            OutFile = f"{i:02}-{name}"

            print(f'"{newfilename}", "{pdffilename}", "{w3w}"')
            make_flyer(TargetFile, name, w3w, OutFolder, OutFile)
            i = i + 1


if __name__ == "__main__":
    main()
