import glfw
from OpenGL.GL import *

import imgui
from imgui.integrations.glfw import GlfwRenderer
from enum import Enum

from json import load, dump
import os

# Ensure the current working directory is the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.path.isfile("account.json") or open("account.json", "w").write('{"username": "No Account"}')

# Load Account Data
with open("account.json", "r") as account_file:
    ACCOUNT_DATA = load(account_file)

# Initialize the GLFW library
if not glfw.init():
    raise Exception("GLFW initialization failed")

# Create a windowed mode window and its OpenGL context
window = glfw.create_window(800, 600, "The RoDevGameEngine Hub", None, None)
if not window:
    glfw.terminate()
    raise Exception("Failed to create GLFW window")

# Make the window's context current
glfw.make_context_current(window)

# Callback function for window resizing
def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)
    update(window)

# Set the resize callback
glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

# Initialize ImGui
imgui.create_context()
imgui_renderer = GlfwRenderer(window)

# Set the initial OpenGL viewport
glViewport(0, 0, 800, 600)

class Menu(Enum):
    PROJECTS = 1
    ACCOUNT = 2
    CREATE_PROJECT_MENU = 3

class USE_LATEST_ENGINE_VERSION(Enum):
    YES = 2
    NO = 1

import requests
import zipfile

def get_all_releases():
    url = f"https://api.github.com/repos/RoWiz09/Autoflipper/releases"
    response = requests.get(url, headers={"Accept": "application/vnd.github.v3+json"})  # Use GitHub API headers
    # Check if the request was successful
    if response.status_code == 404:
        print(f"Repository 'RoWiz09/Autoflipper' not found.")
        return None
    elif response.status_code != 200:
        print(f"Failed to fetch releases. Status code: {response.status_code}")
        return None
    else:
        return response.json()

cur_menu = Menu.PROJECTS

editing_account = False

username_last_frame = ACCOUNT_DATA["username"]
last_project_name = ""

last_selected_engine_version = 0

def create_proj(project_name:str, engine_version_download_url:str):
    if not os.path.isdir("C:\\RoDevGameEngine\\Projects\\"):
        os.mkdir("C:\\RoDevGameEngine\\Projects\\")

    if os.path.isdir("C:\\RoDevGameEngine\\Projects\\%s"%project_name):
        raise Exception("Project with name '%s' already exists!"%project_name)

    os.mkdir("C:\\RoDevGameEngine\\Projects\\%s"%project_name)

    with open("C:\\RoDevGameEngine\\Projects\\%s\\%s.py"%(project_name,project_name), "w") as project_file:
        project_file.write("""
            import argparse
            from enum import Enum

            parser = argparse.ArgumentParser()

            class BootState(Enum):
                EDIT = "Edit"
                BUILD = "Build"
                PLAY = "Play"

            parser.add_argument('--boot-state', type=str, choices=[state.value for state in BootState], default=BootState.EDIT.value, help='Boot state of the game engine', required=True)

            args = parser.parse_args()

            if args.boot_state == BootState.EDIT.value:
                from RoDevGameEngine import editor_window
                from json import load

                projectData = load(open(".assets\\main.json"))

                game_window = editor_window.window(projectData['projectName'], starting_scene=projectData["startingScene"], compiled=projectData.get("compiled"))
                game_window.start_update_loop()

            elif args.boot_state == BootState.BUILD.value:
                pass

            elif args.boot_state == BootState.PLAY.value:
                from RoDevGameEngine import window as game_window
                from json import load

                projectData = load(open(".assets\\main.json"))

                game_window = game_window.window(projectData['projectName'], starting_scene=projectData["startingScene"], compiled=projectData.get("compiled"))
                game_window.start_update_loop()

        """)

        project_file.close()

    os.mkdir("C:\\RoDevGameEngine\\Projects\\%s\\assets"%project_name)

    with open("C:\\RoDevGameEngine\\Projects\\%s\\assets\\main.json"%project_name, "w") as project_json:
        project_data = {
            "projectName": project_name,
            "startingScene": 0,
            "compiled": False
        }
        dump(project_data, project_json, indent=4)
        project_json.close()

    # Set up materials folder
    os.mkdir("C:\\RoDevGameEngine\\Projects\\%s\\assets\\materials"%project_name)
    with open("C:\\RoDevGameEngine\\Projects\\%s\\assets\\materials\\sample_mat.romat"%project_name, "w") as sample_mat:
        sample_mat.write("""
            {
                "color":[1, 1, 1, 1],
                "texture_path":".\\RoDevGameEngine\\base_texture.png",
                "shader":"['base_vert_3d','base_frag_3d']",
                "tiling_data":[1,1]
            }
        """)

        sample_mat.close()

    # Set up scenes folder
    os.mkdir("C:\\RoDevGameEngine\\Projects\\%s\\assets\\scenes"%project_name)
    with open("C:\\RoDevGameEngine\\Projects\\%s\\assets\\scenes\\sample_scene.roscene"%project_name, "w") as sample_scene:
        sample_scene.write("""
            {
                "baseCamera":{"name":"playerCam","pos":[0,0,0],"rot":[0,0,0]},
                "3d":{
                    "testCube":{"mesh_obj":"cube","components":{"RoDevGameEngine.physics.collider":[{"class_name":"OBB","vars":["normal_collider"]}]},"pos":[0,0,0],"rot":[0,0,0],"scale":[1,1,1],"material":"assets\\materials\\sample_mat.romat"},
                },
                "2d":{

                },
                "scene_index":0
            }
        """)

        sample_scene.close()

    os.mkdir("C:\\RoDevGameEngine\\Projects\\%s\\assets\\scripts"%project_name)
    os.mkdir("C:\\RoDevGameEngine\\Projects\\%s\\assets\\textures"%project_name)

    # Download and extract the engine
    engine_folder = "C:\\RoDevGameEngine\\Projects\\%s\\engine" % project_name
    os.mkdir(engine_folder)

    # Download the engine zip file
    zip_path = os.path.join("C:\\RoDevGameEngine\\Projects\\%s\\engine\\engine.zip" % project_name)
    response = requests.get(engine_version_download_url, stream=True)
    if response.status_code == 200:
        with open(zip_path, 'wb') as zip_file:
            for chunk in response.iter_content(chunk_size=1024):
                zip_file.write(chunk)
    else:
        raise Exception(f"Failed to download engine. Status code: {response.status_code}")

    # Extract the zip file directly into the project folder
    with zipfile.ZipFile(zip_path) as zipFile:
        for file in zipFile.filelist:
            if not file.is_dir():
                with zipFile.open(file) as zip_file:
                    with open("C:\\RoDevGameEngine\\Projects\\%s\\engine\\%s" % (project_name, "/".join(zip_file.name.split("/")[1:])), 'w') as extracted_file:
                        extracted_file.write(zip_file.read().decode())
                        print(zip_file.read().decode())

list_of_releases = get_all_releases()

def update(window):
    global cur_menu, editing_account, username_last_frame, last_project_name, list_of_releases, last_selected_engine_version

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Start a new ImGui frame
    imgui_renderer.process_inputs()
    imgui.new_frame()

    # Get the size of the GLFW window
    window_width, window_height = glfw.get_framebuffer_size(window)

    # Create a fullscreen ImGui window
    imgui.set_next_window_position(0, 0)
    imgui.set_next_window_size(window_width, window_height)
    imgui.begin("Fullscreen Window", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_MENU_BAR)

    with imgui.begin_menu_bar() as menu_bar:
        if menu_bar.opened:
            if imgui.button('Account', 100):
                cur_menu = Menu.ACCOUNT

            if imgui.button('Projects', 100):
                cur_menu = Menu.PROJECTS

    if cur_menu == Menu.PROJECTS:
        imgui.text("Projects Menu")
        imgui.text("List of projects will be displayed here.")
        if imgui.button("Create New Project"):
            cur_menu = Menu.CREATE_PROJECT_MENU

    elif cur_menu == Menu.CREATE_PROJECT_MENU:        
        create_project_name = imgui.input_text("Project Name", last_project_name, 256)[1]
        last_project_name = create_project_name

        imgui.text("Select Engine Version:")
        engine_version = imgui.combo("Engine Version", last_selected_engine_version, [release['tag_name'] for release in list_of_releases], 256)[1]
        last_selected_engine_version = engine_version

        if imgui.button("Create Project"):
            if create_project_name:
                try:
                    create_proj(create_project_name, list_of_releases[engine_version]['zipball_url'])
                    cur_menu = Menu.PROJECTS
                except Exception as e:
                    print("Error: %s" % str(e))
            else:
                imgui.text("Please enter a project name.")

    elif cur_menu == Menu.ACCOUNT:
        if editing_account:
            imgui.text("Editing Account")

            username = imgui.input_text("Username", username_last_frame, 256)[1]
            username_last_frame = username

            if imgui.button("Save Account"):
                editing_account = False
                with open("account.json", "w") as account_file:
                    ACCOUNT_DATA["username"] = username
                    dump(ACCOUNT_DATA, account_file, indent=4)

            if imgui.button("Cancel"):
                editing_account = False

                username_last_frame = ACCOUNT_DATA["username"]

        else:
            imgui.text("Account Data:")

            if imgui.button("Edit Account"):
                editing_account = True

            imgui.text("Username: %s" % ACCOUNT_DATA.get("username", "No Account"))

    imgui.end()

    # Render the ImGui frame
    imgui.render()
    imgui_renderer.render(imgui.get_draw_data())

    # Swap front and back buffers
    glfw.swap_buffers(window)

    # Poll for and process events
    glfw.poll_events()

# Main loop
while not glfw.window_should_close(window):
    update(window)

# Terminate GLFW
glfw.terminate()