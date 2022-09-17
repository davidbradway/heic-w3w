from borb.pdf import Document
from borb.pdf import Page
from borb.pdf import SingleColumnLayout
from borb.pdf import PageLayout
from borb.pdf import Paragraph
from borb.pdf import PDF
from borb.pdf import Alignment
from borb.pdf import Image
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


def make_flyer(SourceFile, name, w3w, filename, OutFolder):
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
            font_size=Decimal(32),
            horizontal_alignment=Alignment.CENTERED,
        )
    )
    # Subtitle
    layout.add(
        Paragraph(
            "Erwin Road Adopt-A-Flexpost Program",
            font_color=HexColor("#003087"),
            font_size=Decimal(26),
            horizontal_alignment=Alignment.CENTERED,
        )
    )

    layout.add(
        Paragraph(
            f"What3Words Location: ///{w3w}",
            font_color=HexColor("#003087"),
            font_size=Decimal(20),
            horizontal_alignment=Alignment.CENTERED,
        )
    )

    # download image and store on disk, if needed
    if not os.path.exists(SourceFile):
        with open(SourceFile, "wb") as jpg_file_handle:
            jpg_file_handle.write(
                requests.get(
                    "https://images.unsplash.com/photo-1514606491078-3c8ff84c87e7?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=3870&q=80",
                    stream=True,
                ).content
            )

    layout.add(
        Image(
            Path(SourceFile),
            width=Decimal(200),
            height=Decimal(200),
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
            .add(Paragraph("Clear trash and debris quarterly."))
            .add(Paragraph("Cut back weeds and bushes annually."))
            .add(Paragraph("Report maintenance needs to Durham OneCall."))
            .add(Paragraph("Transfer ownership if unable to meet obligations."))
    )

    # add a Paragraph
    flow.add(ChunkOfText("Thanks! "))
    flow.add(Emojis.BIKE.value)
    layout.add(flow)

    # QR Code
    qr_code: LayoutElement = Barcode(
        data="https://www.adoptaflexpost.com",
        width=Decimal(96),
        height=Decimal(96),
        type=BarcodeType.QR,
    )
    # add a QR code
    layout.add(qr_code)

    # store as PDF
    with open(os.path.join(OutFolder, filename+".pdf"), "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)

    # convert to PNG
    doc = fitz.open(os.path.join(OutFolder, filename+".pdf"))
    for page in doc:
        zoom = 2  # zoom factor
        pix = page.get_pixmap(matrix = fitz.Matrix(zoom, zoom))
        pix.save(os.path.join(OutFolder, filename+".png"))


def main():

    SourceFolder = 'JpgFolder'
    OutFolder = 'OutFolder'

    i = 0
    for file in os.listdir(SourceFolder):
        if file.endswith('.jpg'):
            SourceFile = os.path.join(SourceFolder, file)
            name = names[i]
            w3w = "leaves.owners.solved"
            filename = f"{i:02}-{name}"
            make_flyer(SourceFile, name, w3w, filename, OutFolder)
            i = i + 1


if __name__ == "__main__":
    main()
