from RoDevGameEngine.input import handle_inputs
from RoDevGameEngine.sceneManager import create_scene_manager
import glfw, OpenGL.GL as gl

window_ = None

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

        global window
        window = self.window

        glfw.set_window_pos(self.window, 0, 0)
        glfw.make_context_current(self.window)
        
        self.res = glfw.get_monitor_workarea(get_monitor(monitor))[2:4]

        self.sceneManager = create_scene_manager(starting_scene, self, get_compiled(compiled))

        gl.glClearColor(0.25, 0.25, 1, 1)

        gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_DEPTH_TEST)

        gl.glPushMatrix()
        gl.glLoadIdentity()

    def start_update_loop(self):
        while not glfw.window_should_close(self.window):
            # get all window events
            glfw.poll_events()

            # update input handler
            handle_inputs(self.window)

            # resize the window viewport when window gets resized
            gl.glViewport(0, 0, *glfw.get_window_size(self.window))

            # clear all buffer data
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
            gl.glLoadIdentity()

            # update all gameobjects in the scene
            self.sceneManager.update_scene(glfw.get_window_size(self.window))

            # push all changes to the window
            glfw.swap_buffers(self.window)
