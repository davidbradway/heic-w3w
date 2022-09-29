from wand.image import Image as WandImage
from exif import Image as ExifImage
import what3words
from borb.pdf import (Document, Page, SingleColumnLayout, PageLayout,
Paragraph, PDF, Alignment, ChunkOfText, InlineFlow, Barcode,
BarcodeType, UnorderedList, HexColor, Image as BorbImage)
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
import secrets

geocoder = what3words.Geocoder(secrets.W3W_API_KEY)


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def convertToJpg(HeicFolder, filename, JpgFolder):
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
    with open(TargetFile, "rb") as src:
        img = ExifImage(src)
        lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
        lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
        res = geocoder.convert_to_3wa(what3words.Coordinates(lat, lon))
        w3w = f"{res['words']}"
    return w3w


def makeFlyer(JpgFile, name, w3w, OutFolder, OutFile):
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
    annot0: RemoteGoToAnnotation = RemoteGoToAnnotation(link0.get_previous_paint_box(), uri=f"http://w3w.co/{w3w}")
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
    link1: LayoutElement = ChunkOfText(f"w3w.co/{w3w}", vertical_alignment=Alignment.BOTTOM, font_color=HexColor("0000FF"))
    flow1.add(link1)
     # add in-line text and emoji
    flow1.add(ChunkOfText(" --Thanks! ", vertical_alignment=Alignment.BOTTOM))
    layout.add(flow1)
    annot1: RemoteGoToAnnotation = RemoteGoToAnnotation(link1.get_previous_paint_box(), uri=f"http://w3w.co/{w3w}")
    page.add_annotation(annot1)

    # store as PDF
    with open(os.path.join(OutFolder, OutFile + ".pdf"), "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)


def convertToPng(OutFolder, OutFile):
    # convert to PNG
    with fitz.open(os.path.join(OutFolder, OutFile + ".pdf")) as pdf:
        for page in pdf:
            zoom = 2  # zoom factor
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            pix.save(os.path.join(OutFolder, OutFile + ".png"))

def main():

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
