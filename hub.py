import glfw
from OpenGL.GL import *

import subprocess
import imgui
from imgui.integrations.glfw import GlfwRenderer
from enum import Enum

import shutil, pathlib as pl

from json import load, dump
import os, stat

# Ensure the current working directory is the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.path.isfile("account.json") or open("account.json", "w").write('{"username": "No Account", "python_loc": ""}')

# Load Account Data
with open("account.json", "r") as account_file:
    ACCOUNT_DATA = load(account_file)
    print("Account Data Loaded:", ACCOUNT_DATA)

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
    url = f"https://api.github.com/repos/RoWiz09/GameEngine/releases"
    response = requests.get(url, headers={"Accept": "application/vnd.github.v3+json"})  # Use GitHub API headers
    # Check if the request was successful
    if response.status_code == 404:
        print(f"Repository 'RoWiz09/GameEngine' not found.")
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
projects = []

home_path = pl.Path.home()

def create_proj(project_name:str, engine_version_download_url:str, engine_version:str):
    global home_path

    if not os.path.isdir(f"{home_path}\\RoDevGameEngine\\Projects\\"):
        os.mkdir(f"{home_path}\\RoDevGameEngine\\Projects\\")

    if os.path.isdir(f"{home_path}\\RoDevGameEngine\\Projects\\%s"%project_name):
        raise Exception("Project with name '%s' already exists!"%project_name)

    os.mkdir(f"{home_path}\\RoDevGameEngine\\Projects\\%s"%project_name)

    with open(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\main.py"%(project_name), "w") as project_file:
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

    projectData = load(open("./assets/main.json"))

    game_window = editor_window.window(projectData['projectName'], starting_scene=projectData["startingScene"], compiled=None)
    game_window.start_update_loop()

elif args.boot_state == BootState.BUILD.value:
    pass

elif args.boot_state == BootState.PLAY.value:
    from RoDevGameEngine import window as game_window
    from json import load

    projectData = load(open("./assets/main.json"))

    game_window = game_window.window(projectData['projectName'], starting_scene=projectData["startingScene"], compiled=False)
    game_window.start_update_loop()
""")

    os.mkdir(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\assets"%project_name)

    with open(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\assets\\main.json"%project_name, "w") as project_json:
        project_data = {
            "projectName": project_name,
            "startingScene": 0,
        }
        dump(project_data, project_json, indent=4)
        project_json.close()

    # Set up materials folder
    os.mkdir(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\assets\\materials"%project_name)
    with open(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\assets\\materials\\sample_mat.romat"%project_name, "w") as sample_mat:
        sample_mat.write("""
            {
                "color":[1, 1, 1, 1],
                "texture_path":"./RoDevGameEngine/base_texture.png",
                "shader":"['base_vert_3d','base_frag_3d']",
                "tiling_data":[1,1]
            }
        """)

        sample_mat.close()

    # Set up scenes folder
    os.mkdir(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\assets\\scenes"%project_name)
    with open(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\assets\\scenes\\sample_scene.roscene"%project_name, "w") as sample_scene:
        sample_scene.write("""
            {
                "baseCamera":{"name":"playerCam","pos":[0,0,0],"rot":[0,0,0]},
                "3d":{
                    "testCube":{"mesh_obj":"cube","components":{"RoDevGameEngine.physics.collider":[{"class_name":"OBB","vars":["normal_collider"]}]},"pos":[0,0,0],"rot":[0,0,0],"scale":[1,1,1],"material":"assets/materials/sample_mat.romat"},

                    "light0": {
                        "mesh_obj": null,
                        "components": {
                        "RoDevGameEngine.light": {
                            "class_name": "Light",
                            "vars": {
                            "color": [1.0, 0.0, 0.0],
                            "original_constant": 6,
                            "original_intensity": 12,
                            "range": 15
                            }
                        }
                        },
                        "pos": [0.0, 1.0, 0.0],
                        "rot": [0.0, 0.0, 0.0],
                        "scale": [1.0, 1.0, 1.0],
                        "material": null
                    }
                },
                "2d": {},
                "scene_index": 0
        }""")

        sample_scene.close()

    os.mkdir(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\assets\\scripts"%project_name)
    os.mkdir(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\assets\\textures"%project_name)

    # Download and extract the engine
    engine_folder = f"{home_path}\\RoDevGameEngine\\Projects\\%s\\RoDevGameEngine" % project_name
    os.mkdir(engine_folder)

    # Download the engine zip file
    zip_path = os.path.join(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\engine.zip" % project_name)
    response = requests.get(engine_version_download_url, stream=True)
    if response.status_code == 200:
        with open(zip_path, 'wb') as zip_file:
            for chunk in response.iter_content(chunk_size=1024):
                zip_file.write(chunk)
    else:
        raise Exception(f"Failed to download engine. Status code: {response.status_code}")

    # Extract the zip file directly into the project folder
    import stat

    def ensure_writable(path):
        if os.path.exists(path):
            os.chmod(path, stat.S_IWRITE)

    with zipfile.ZipFile(zip_path) as zip_File:
        for file in zip_File.namelist():
            info = zip_File.getinfo(file)

            # Skip directories
            if info.is_dir():
                continue

            # Build full target path
            file_path = os.path.join(engine_folder, os.path.relpath(file, start=zip_File.namelist()[0]))
            file_path = os.path.normpath(file_path)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Ensure the file is writable if it already exists
            ensure_writable(file_path)

            # Extract the file
            with zip_File.open(file) as source, open(file_path, "wb") as target:
                target.write(source.read())
    
    with open(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\.roproj" % project_name, "w") as roproj_file:
        roproj_file.write("""
            {
                "projectName": "%s",
                "engineVersion": "%s"
            }
        """ % (project_name, engine_version))
        roproj_file.close()

    # Remove the downloaded zip file
    os.remove(zip_path)

list_of_releases = get_all_releases()
dirpath = f"{home_path}"
os.makedirs(dirpath + "\\RoDevGameEngine\\Projects", exist_ok=True)

current_permissions = os.stat(dirpath).st_mode
os.chmod(dirpath, current_permissions | stat.S_IWUSR)

def get_github_zip_release(releases_dict):
    for release in releases_dict["assets"]:
        if release.get('name') == 'Engine.zip':
            return release
        
    return None

def get_engine_download_url(engine_version):
    global list_of_releases
    if list_of_releases is None:
        raise Exception("No releases found. Please check your internet connection or the repository URL.")
    
    for release in list_of_releases[engine_version]["assets"]:
        if release["name"] == "Engine.zip":
            return release["browser_download_url"]

print(list_of_releases[last_selected_engine_version]["assets"])

def get_projects():
    global projects, home_path

    projects.clear()

    for directory in os.listdir(f"{home_path}\\RoDevGameEngine\\Projects"):
        if os.path.isfile(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\.roproj" % directory):
            with open(f"{home_path}\\RoDevGameEngine\\Projects\\%s\\.roproj" % directory, "r") as roproj_file:
                project_data = load(roproj_file)
                projects.append({
                    "name": project_data["projectName"],
                    "engine_version": project_data["engineVersion"]
                })

def update(window):
    global cur_menu, editing_account, username_last_frame, last_project_name, list_of_releases, last_selected_engine_version, ACCOUNT_DATA, projects

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
        with imgui.begin_child("projects", *(window_width-27, window_height-50), True):
            for project in projects:
                imgui.text(project["name"])
                imgui.same_line()
                imgui.text(" - ")
                imgui.same_line()
                imgui.text("Engine Version: %s" % project["engine_version"])
                imgui.same_line()

                imgui.set_cursor_pos_x(window_width - 287)
                if imgui.button(f"Delete##Del{project['name']}", 120):
                    shutil.rmtree(f'{home_path}\\RoDevGameEngine\\Projects\\{project["name"]}')
                    get_projects()
                imgui.same_line()

                imgui.set_cursor_pos_x(window_width - 157)
                if imgui.button(f"Edit##Edit{project['name']}", 120):
                    subprocess.run(f'py "{home_path}\\RoDevGameEngine\\Projects\\{project["name"]}\\main.py" --boot-state Edit', cwd=f'{home_path}\\RoDevGameEngine\\Projects\\{project["name"]}')
                    
                imgui.separator()

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
                    create_proj(create_project_name, get_github_zip_release(list_of_releases[engine_version])['browser_download_url'], list_of_releases[engine_version]['tag_name'])
                    cur_menu = Menu.PROJECTS
                    get_projects()

                except Exception as e:
                    raise e
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

get_projects()

# Main loop
while not glfw.window_should_close(window):
    update(window)

# Terminate GLFW
glfw.terminate()