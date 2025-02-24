import glfw, OpenGL.GL as gl

class window:
    def __init__(self, window_name : str, monitor = None):
        glfw.init()

        # Enable OpenGL
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_COMPAT_PROFILE)

        get_monitor = lambda monitor : [glfw.get_primary_monitor() if monitor == None else monitor]

        self.window = glfw.create_window(glfw.get_monitor_workarea(get_monitor(monitor)), window_name, monitor, None)
        glfw.set_window_pos(self.window)
        glfw.make_context_current(self.window)
        
        self.res = glfw.get_monitor_workarea(get_monitor(monitor))

        gl.glClearColor(1, 0, 1, 1)

        gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_DEPTH_TEST)

        gl.glPushMatrix()
        gl.glLoadIdentity()

    def start_update_loop(self):
        while not glfw.window_should_close(self.window):
            # get all window events
            glfw.poll_events(self)

            # clear all buffer data
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)

            # push all changes to the window
            glfw.swap_buffers(self.window)
