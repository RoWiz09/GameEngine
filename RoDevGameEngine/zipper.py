import zipfile, os

def readFolder(path : str):
    files : list[str] = []
    for file in os.listdir(path):
        if os.path.isdir(path+"\\"+file):
            subfiles = readFolder(path+"\\"+file)
            files.extend(subfiles)
        else:
            files.append(path+"\\"+file)

    return files

def zipFolder():
    files=readFolder("assets")
    
    my_zip = zipfile.ZipFile("assets.zip", 'w')
    for file in files:
        my_zip.write(file, file.removeprefix("assets\\"))
        