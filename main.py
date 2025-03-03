projectData={'startingScene':0,'projectName':'TestProjectOne'}
import sys

from RoDevGameEngine import window
from json import load


game_window = window.window(projectData['projectName'])
game_window.start_update_loop()
