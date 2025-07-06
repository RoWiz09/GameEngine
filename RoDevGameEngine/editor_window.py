from RoDevGameEngine.gameObjects import gameObject3D
from RoDevGameEngine.transform import transform
from RoDevGameEngine.mesh import Mesh

from RoDevGameEngine.create_new_project import Project

from RoDevGameEngine.input import handle_inputs, get_key_down, keyCodes
from RoDevGameEngine.sceneManager import create_scene_manager
import glfw, OpenGL.GL as gl, glm, PIL.Image

import numpy as np
import keyboard

import imgui
from imgui.integrations.glfw import GlfwRenderer

from json import load
import os

class window:
    def __init__(self, project_name : str, starting_scene : int = 0, fullscreen = False, monitor = None, compiled = False):
        glfw.init()

        # Enable OpenGL
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_COMPAT_PROFILE)

        get_monitor = lambda monitor : glfw.get_primary_monitor() if monitor == None else monitor
        get_compiled = lambda compiled : False if compiled == None else True
        
        if fullscreen:
            self.window = glfw.create_window(*glfw.get_monitor_workarea(get_monitor(monitor))[2:4], project_name, monitor, None)
        else:
            self.window = glfw.create_window(*glfw.get_monitor_workarea(get_monitor(monitor))[2:4], project_name, None, None)
        glfw.set_window_pos(self.window, 0, 0)
        glfw.make_context_current(self.window)
        
        self.res = glfw.get_monitor_workarea(get_monitor(monitor))[2:4]

        self.sceneManager = create_scene_manager(starting_scene, self, get_compiled(compiled))
        
        imgui.create_context()
        self.imgui_renderer = GlfwRenderer(self.window)

        gl.glClearColor(0.25, 0.25, 1, 1)

        gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_DEPTH_TEST)

        gl.glPushMatrix()
        gl.glLoadIdentity()

        # Editor-specific functions
        self.render_scene_data_editor = False
        self.render_new_project_menu = False
        self.render_hierarchy_menu = False
        self.render_file_tree_menu = False
        self.render_code_editor = False
        self.render_scene_menu = False 

        self.code_editor_tabs_open = []
        self.cur_open_editor_tab = None

        self.file_tree_menu_curpath = ".\\assets"
        self.file_viewers_open = []

        self.gameobject_inspection_menus_open = {}
        self.proj_name = ""

        self.selected_list_index = 0
        self.selected_tuple_index = 0

        self.texture_sample_windows_open = []

        self.debug = 0

    def save_scene(self):
        self.sceneManager.save()

    def is_scene(self, file_path:str):
        print(self.sceneManager.scenes, file_path.removeprefix(".\\"))
        if file_path.removeprefix(".\\") in self.sceneManager.scenes:
            return True
                
        return False

    def start_update_loop(self): 
        while not glfw.window_should_close(self.window):
            # get all window events
            glfw.poll_events()

            self.imgui_renderer.process_inputs()

            imgui.new_frame()

            # The bar on the top of the screen. Dunno what to call it lol
            with imgui.begin_main_menu_bar() as main_menu_bar:
                if main_menu_bar.opened:
                    # first menu dropdown
                    with imgui.begin_menu('File', True) as file_menu:
                        if file_menu.opened:
                            if imgui.menu_item('New Project', 'Ctrl+N', False, True)[1]:
                                self.render_new_project_menu = True
                            imgui.menu_item('Open ...', 'Ctrl+O', False, True)

                            if imgui.menu_item('Save', 'Ctrl+S', False, True)[1]:
                                self.save_scene()

                            # submenu
                            with imgui.begin_menu('Open Recent', True) as open_recent_menu:
                                if open_recent_menu.opened:
                                    imgui.menu_item('doc.txt', None, False, True)

                    with imgui.begin_menu("Scene") as gameobjects_menu:
                        if gameobjects_menu.opened:
                            if imgui.menu_item("Scene Customization")[1]:
                                self.render_scene_data_editor = True

                            if imgui.menu_item("Hierarchy", 'Ctrl+H', False, True)[1]:
                                self.render_hierarchy_menu = True

                    with imgui.begin_menu("Files") as files_menu:
                        if files_menu.opened:
                            if imgui.menu_item("File Viewer", "Ctrl+F")[1]:
                                self.render_file_tree_menu = True
                    
                    with imgui.begin_menu("Freecam") as freecam_options:
                        if freecam_options.opened:
                            imgui.push_item_width(200)
                            val = imgui.slider_float("Freecam Speed", self.sceneManager.freecam_camera.speed, 0.01, 100)[1]
                            self.sceneManager.freecam_camera.speed = val

                            val = imgui.slider_float("Freecam FOV", self.sceneManager.freecam_camera.zoom, 45, 225)[1]
                            self.sceneManager.freecam_camera.zoom = val
                        

            # Project Creation Menu
            if self.render_new_project_menu:
                imgui.begin("Create New Project")
                self.proj_name = imgui.input_text("Project Name: ", self.proj_name)[1]

                if imgui.button("Create Project!"):
                    try:
                        Project(self.proj_name)
                    except:
                        imgui.text("The project either cannot be created, or it already exists!")

                imgui.end()

            # File Tree Menu
            if self.render_file_tree_menu:
                with imgui.begin("File Tree"):
                    if self.file_tree_menu_curpath != ".\\assets":
                        if imgui.button("Return to assets", 200):
                            self.file_tree_menu_curpath = ".\\assets"
                    for file in os.listdir(self.file_tree_menu_curpath):
                        if not file == "__pycache__":
                            if imgui.button(file, 200):
                                if os.path.isdir(self.file_tree_menu_curpath+"\\"+file):
                                    self.file_tree_menu_curpath+="\\"+file

                                elif file.endswith((".png",".jpg")):
                                    img_id = 0
                                    for mat in self.sceneManager.materials.keys():
                                        test_res = self.sceneManager.materials[mat].check_texture_equal(self.file_tree_menu_curpath.removeprefix(".\\")+"\\"+file)
                                        print(test_res)
                                        if test_res:
                                            img_id = test_res

                                    self.texture_sample_windows_open.append([self.file_t2ree_menu_curpath.removeprefix(".\\")+file, img_id])
                                
                                elif file.endswith(".py"):
                                    self.code_editor_tabs_open.append(self.file_tree_menu_curpath+"\\"+file)
                                
                                else:
                                    is_scene = self.is_scene(self.file_tree_menu_curpath+"\\"+file)
                                    if is_scene:
                                        self.sceneManager.swap_scene(self.file_tree_menu_curpath+"\\"+file)

            # Hierarchy Menu
            if self.render_hierarchy_menu:
                imgui.begin("Hierarchy")

                if imgui.button("Create New Gameobject", 200):
                    new_go_transform = transform(glm.vec3(self.sceneManager.freecam_camera.position.to_list()), glm.vec3(0,0,0), scale=glm.vec3(1,1,1))
                    
                    new_gameobject_num = 0
                    for gameobject in self.sceneManager.get_gameobjects():
                        if gameobject.name.startswith("new_gameobject"):
                            new_gameobject_num += 1

                    self.sceneManager.add_gameobject(gameObject3D("new_gameobject_%i"%new_gameobject_num, Mesh(Mesh.cube_verts(), self.sceneManager.materials[list(self.sceneManager.materials.keys())[0]]), new_go_transform))

                for gameobject in self.sceneManager.get_gameobjects():
                    if imgui.button(gameobject.name, 200):
                        self.gameobject_inspection_menus_open[gameobject.name] = gameobject

                imgui.end()

            # Inspection Menus
            for menu in self.gameobject_inspection_menus_open.keys():
                gameobject = self.gameobject_inspection_menus_open[menu]
                if isinstance(gameobject, gameObject3D):
                    imgui.begin(menu)

                    gameobject.name = imgui.input_text("Name:", gameobject.name)[1]
                    imgui.same_line()
                    gameobject.set_active(imgui.checkbox("Active:", gameobject.get_active())[1])

                    pos = gameobject.transform.pos
                    imgui.push_item_width(100)
                    pos.x = imgui.input_float("position x", pos.x)[1]
                    imgui.same_line()
                    pos.y = imgui.input_float("position y", pos.y)[1]
                    imgui.same_line()
                    pos.z = imgui.input_float("position z", pos.z)[1]

                    rot = gameobject.transform.rot
                    rot.x = imgui.input_float("rotation x", rot.x)[1]
                    imgui.same_line()
                    rot.y = imgui.input_float("rotation y", rot.y)[1]
                    imgui.same_line()
                    rot.z = imgui.input_float("rotation z", rot.z)[1]

                    scale = gameobject.transform.scale
                    scale.x = imgui.input_float("scale x", scale.x)[1]
                    imgui.same_line()
                    scale.y = imgui.input_float("scale y", scale.y)[1]
                    imgui.same_line()
                    scale.z = imgui.input_float("scale z", scale.z)[1]

                    for component in gameobject.components:
                        imgui.spacing()
                        imgui.spacing()
                        imgui.text(type(component).__name__)

                        imgui.same_line()
                        component.set_active(imgui.checkbox("Active:", component.get_active)[1])

                        imgui.spacing()

                        for var in dir(component):
                            if all((not var.startswith("_"), not var=="parent", not callable(getattr(component, var)))):
                                value = getattr(component, var)
                                if isinstance(value, int):
                                    setattr(component, var, imgui.input_int(var, value)[1])
                                elif isinstance(value, float):
                                    setattr(component, var, imgui.input_float(var, value)[1])
                                elif isinstance(value, bool):
                                    setattr(component, var, imgui.checkbox(var, value)[1])
                                elif isinstance(value, list):
                                    idx = 0
                                    for item in value:
                                        if isinstance(value[self.selected_list_index], (int, float)):
                                            new_val = imgui.input_float("%s, item %i"%(str(var), idx), float(item))[1]
                                            orignal_val = getattr(component, var)
                                            orignal_val[idx] = new_val
                                            idx += 1

                                elif isinstance(value, tuple):
                                    with imgui.begin_list_box(var, 200, 100) as list_box:
                                        if list_box.opened:
                                            for item in value:
                                                if imgui.selectable(str(item), self.selected_tuple_index == value.index(item))[1]:
                                                    self.selected_tuple_index = value.index(item)
                                                    print(value.index(item))

                                elif isinstance(value, glm.vec3):
                                    value.x = imgui.input_float("%s x"%var, value.x)[1]
                                    imgui.same_line()
                                    value.y = imgui.input_float("%s y"%var, value.y)[1]
                                    imgui.same_line()
                                    value.z = imgui.input_float("%s z"%var, value.z)[1]
                                    imgui.same_line()
                                    setattr(component, var, value)
                                else:
                                    imgui.text(var)

                    imgui.end()
            
            # Texture Sample Menus
            for menu in self.texture_sample_windows_open:
                with imgui.begin(menu[0]) as im_window:
                    if im_window.opened:
                        imgui.image(menu[1], 500, 500)

            # Code Editor
            if self.render_code_editor:
                with imgui.begin("Code Editor") as code_editor:
                    if code_editor.opened:
                        for button in self.code_editor_tabs_open:
                            if imgui.button(button):
                                self.cur_open_editor_tab_text = open(button, "r").read()
                                self.cur_open_editor_tab = open(button, "w")

                        if self.cur_open_editor_tab:
                            self.cur_open_editor_tab_text = imgui.input_text_multiline("", self.cur_open_editor_tab_text, width=700, height=500)[1]

                            if imgui.button("Save", 700):
                                self.cur_open_editor_tab.close()
                                with open(self.cur_open_editor_tab.name, "w") as editor_code:
                                    editor_code.write(self.cur_open_editor_tab_text)
            
            # Scene Data Editor
            if self.render_scene_data_editor:
                with imgui.begin("Scene Data") as scene_data_menu:
                    if scene_data_menu.opened:
                        self.sceneManager.scene = imgui.input_int("Scene Index", self.sceneManager.scene)[1]

            # update input handler
            handle_inputs(self.window)

            if get_key_down(keyCodes.KEY_LEFT_CONTROL) and get_key_down(keyCodes.KEY_N):
                self.render_new_project_menu = True

            if get_key_down(keyCodes.KEY_LEFT_CONTROL) and get_key_down(keyCodes.KEY_S):
                self.save_scene()

            if get_key_down(keyCodes.KEY_LEFT_CONTROL) and get_key_down(keyCodes.KEY_H):
                self.render_hierarchy_menu = True

            # resize the window viewport when window gets resized
            gl.glViewport(0, 0, *glfw.get_window_size(self.window))

            # clear all buffer data
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
            gl.glLoadIdentity()

            # update all gameobjects in the scene
            self.sceneManager.update_scene_editor(glfw.get_window_size(self.window))

            # push all changes to the window
            imgui.render()
            self.imgui_renderer.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)

class editor_camera:
    """
        A non-physical object in the game's scene. 
    """
    def __init__(self, position=glm.vec3(0.0, 0.0, 0.0), up=glm.vec3(0.0, 1.0, 0.0), yaw=-90.0, pitch=0.0):
        """
            Creates and returns a new camera instance. 
            
            args:
                position (glm.vec3): The position of the camera in world space.
                up (glm.vec3): The up vector of the camera.
                yaw (float): The yaw of the camera in degrees.
                pitch (float): The pitch of the camera in degrees.
        """
        self.position = position
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = up
        self.right = glm.vec3()
        self.world_up = up
        self.yaw = yaw
        self.pitch = pitch
        self.speed = 5 
        self.sensitivity = 0.5
        self.zoom = 45.0
        self.update_vectors()

    def update_vectors(self):
        front = glm.vec3()
        front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        front.y = np.sin(glm.radians(self.pitch))
        front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def process_keyboard(self, delta_time):
        velocity = self.speed * delta_time
        if keyboard.is_pressed("w"):
            self.position += self.front * velocity
        if keyboard.is_pressed("s"):
            self.position -= self.front * velocity
        if keyboard.is_pressed("a"):
            self.position -= self.right * velocity
        if keyboard.is_pressed("d"):
            self.position += self.right * velocity

    def process_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        x_offset *= self.sensitivity
        y_offset *= self.sensitivity

        self.yaw += x_offset
        self.pitch += y_offset

        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update_vectors()


