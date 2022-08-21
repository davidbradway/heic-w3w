from wand.image import Image
import os

SourceFolder = "HeicFolder"
TargetFolder = "JpgFolder"

for filename in os.listdir(SourceFolder):
    if filename.endswith(".heic") or filename.endswith(".HEIC"):
        SourceFile = os.path.join(SourceFolder, filename)
        newfilename = filename.replace(".HEIC", ".JPG")
        newfilename = newfilename.replace(".heic", ".jpg")
        TargetFile = os.path.join(TargetFolder, newfilename)
        if not os.path.exists(TargetFile):
            img = Image(filename = SourceFile)
            img.format = 'jpg'
            img.save(filename = TargetFile)
            img.close()
            print(f'converted {SourceFile} to {img.format}')
        else:
            print(f'skipped {SourceFile}, already existed')
