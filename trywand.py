from wand.image import Image
import os

SourceFolder = "HeicFolder"
TargetFolder = "JpgFolder"

for file in os.listdir(SourceFolder):
    SourceFile = SourceFolder + "/" + file
    newfilename = file.replace(".HEIC", ".JPG")
    newfilename = newfilename.replace(".heic", ".jpg")
    TargetFile = TargetFolder + "/" + newfilename
                                
    img = Image(filename = SourceFile)
    img.format='jpg'
    img.save(filename = TargetFile)
    img.close()
