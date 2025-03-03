import subprocess, os
from json import load

def build(project_name : str):
    os.chdir(".")
    with open(project_name+".json") as projectJson:
        projectData = load(projectJson)
        with open(project_name+".py", "r") as pythonProject:
            pythonData = pythonProject.read()
            pythonProject.close()
        with open(project_name+".py", "w") as pythonProject:
            pythonProject.write("projectData={'startingScene':%i,'projectName':'%s'}\n"%(projectData['startingScene'], projectData["projectName"]))
            pythonProject.close()
        with open(project_name+".py", "a") as pythonProject:
            data = pythonData.splitlines()
            for line in range(len(data)):
                if data[line].startswith("projectData"):
                    data.pop(line)
                    break

            for line in data:
                pythonProject.write(line+"\n")

    subprocess.run("pyinstaller %s.py" % project_name)

    with open(project_name+".py", "w") as pythonProject:
        pythonProject.write(pythonData)