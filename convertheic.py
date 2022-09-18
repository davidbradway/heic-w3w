from wand.image import Image
import os

SourceFolder = "HeicFolder"
TargetFolder = "JpgFolder"

for filename in os.listdir(SourceFolder):
    if filename.endswith(".heic") or filename.endswith(".HEIC"):
        SourceFile = os.path.join(SourceFolder, filename)
        newfilename = filename.replace(".HEIC", ".jpg")
        newfilename = newfilename.replace(".heic", ".jpg")
        TargetFile = os.path.join(TargetFolder, newfilename)
        if not os.path.exists(TargetFile):
            img = Image(filename=SourceFile)
            img.format = "jpg"
            img.save(filename=TargetFile)
            img.close()
            print(f"converted {SourceFile} to {img.format}")
        else:
            print(f"skipped {SourceFile}, already existed")

        exif = {}
        with Image(filename=SourceFile) as image:
            exif.update(
                (k[5:], v) for k, v in image.metadata.items() if k.startswith("exif:")
            )
        print(exif)
