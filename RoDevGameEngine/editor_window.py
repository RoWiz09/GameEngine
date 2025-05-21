from RoDevGameEngine.create_new_project import Project
from RoDevGameEngine.input import handle_inputs
from RoDevGameEngine.sceneManager import create_scene_manager
import glfw, OpenGL.GL as gl, glm, PIL.Image

import imgui.core as imgui
from imgui.integrations.glfw import GlfwRenderer

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
        self.render_new_project_menu = False
        self.proj_name = ""

    def start_update_loop(self): 
        while not glfw.window_should_close(self.window):
            # get all window events
            glfw.poll_events()

            self.imgui_renderer.process_inputs()

            imgui.new_frame()

            with imgui.begin_main_menu_bar() as main_menu_bar:
                if main_menu_bar.opened:
                    # first menu dropdown
                    with imgui.begin_menu('File', True) as file_menu:
                        if file_menu.opened:
                            if imgui.menu_item('New Project', 'Ctrl+N', False, True)[1]:
                                self.render_new_project_menu = True
                            imgui.menu_item('Open ...', 'Ctrl+O', False, True)

                            # submenu
                            with imgui.begin_menu('Open Recent', True) as open_recent_menu:
                                if open_recent_menu.opened:
                                    imgui.menu_item('doc.txt', None, False, True)

            if self.render_new_project_menu:
                imgui.begin("Create New Project")
                self.proj_name = imgui.input_text("Project Name: ", self.proj_name)[1]

                if imgui.button("Create Project!"):
                    try:
                        Project(self.proj_name)
                    except:
                        imgui.text("The project either cannot be created, or it already exists!")

                imgui.end()

            # update input handler
            handle_inputs(self.window)

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
