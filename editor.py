from RoDevGameEngine import editor_window
from json import load

projectData = load(open(".\\main.json"))

game_window = editor_window.window(projectData['projectName'], starting_scene=projectData["startingScene"], compiled=projectData.get("compiled"))
game_window.start_update_loop()