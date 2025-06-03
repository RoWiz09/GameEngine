import subprocess, os
from RoDevGameEngine import zipper
from RoDevGameEngine import get_glfw_bin
from json import load

def build(project_name : str):
    os.chdir(".")
    pythonProject = None
    with open(project_name+".json") as projectJson:
        projectData = load(projectJson)
        with open(project_name+".py", "r") as pythonProject:
            pythonData = pythonProject.read()
            pythonProject.close()
        with open(project_name+".py", "w") as pythonProject:
            pythonProject.write("projectData={'startingScene':%i,'projectName':'%s','compiled':True}\n"%(projectData['startingScene'], projectData["projectName"]))
            pythonProject.close()
        with open(project_name+".py", "a") as pythonProject:
            data = pythonData.splitlines()
            for line in range(len(data)):
                if data[line].startswith("projectData"):
                    data.pop(line)
                    break

            for line in data:
                pythonProject.write(line+"\n")

    scripts = get_scripts("assets")
    hidden_import_command = ""
    for script in scripts:
        hidden_import_command+="--hidden-import=\""+script.replace("\\",".")+"\" "
        print(script)

    print(hidden_import_command)

    subprocess.run("pyinstaller --noconfirm %s --add-binary=%s:glfw %s.py" % (hidden_import_command, get_glfw_bin.get_glfw_bin()[0][0],project_name+".py"))

    zipper.zipFolder()

    with open(project_name+".py", "w") as pythonProject:
        pythonProject.write(pythonData)

def get_scripts(path : str):
    files = []
    for file in os.listdir(path):
        if file.endswith(".py"):
            files.append(path.replace("/",".")+"."+file.removesuffix(".py"))
        elif os.path.isdir(path+"/"+file):
            new_files = get_scripts(path+"/"+file)
            files.extend(new_files)

    return files

