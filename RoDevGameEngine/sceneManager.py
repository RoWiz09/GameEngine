import os, zipfile, mouse, time, glfw, ast, PIL.Image, glm, numpy as np, importlib

import OpenGL.GL as gl

from RoDevGameEngine.gizmos.line import LineRenderer

from RoDevGameEngine.rendering.camera import Camera

from RoDevGameEngine import gameObjects
from RoDevGameEngine import transform
from RoDevGameEngine import material
from RoDevGameEngine import shaders
from RoDevGameEngine import script
from RoDevGameEngine import input
from RoDevGameEngine import light
from RoDevGameEngine import mesh

from json import load, dump

sceneManager = None

class SceneManager:
    def __init__(self, window, starting_scene_index : int = 0, compiled : bool = True):
        self.window = window
        self.scene = starting_scene_index
        self.scene_data = {}
        self.scenes = []
        self.scene_objects : list[gameObjects.gameObject3D] = []

        self.materials : dict[str,material.Material] = {}

        self.freecam_camera = None
        self.editor_freecam_active = False

        self.active_camera : Camera = None

        if not compiled:
            materials = self.get_materials("assets")
            for mat in materials:
                with open(mat) as materialFile:
                    materialData = load(materialFile)
                    self.materials[mat] = material.Material(glm.vec4(materialData["color"]),PIL.Image.open(materialData["texture_path"]), materialData["texture_path"], materialData["tiling_data"],shaders.BaseShaderProgram())

            scenes = self.get_scenes("assets")
            self.scenes = scenes.copy()
            for scene in scenes:
                with open(scene) as sceneFile:
                    sceneData = load(sceneFile)
                    self.scenes[sceneData["scene_index"]] = scene
                    sceneFile.close()

        elif compiled:
            zipFile = zipfile.ZipFile("./assets.zip")
            textures = {}
            inflist = zipFile.infolist()

            for f in inflist:
                if f.filename.endswith((".png",".jpg")):
                    ifile = zipFile.open(f)
                    img = PIL.Image.open(ifile)
                    textures[ifile.name] = img

            materials = []
            for mat in zipFile.infolist():
                if mat.filename.endswith(".romat"):
                    materials.append(mat.filename)

            for mat in materials:
                with zipFile.open(mat) as materialFile:
                    materialData = ast.literal_eval(materialFile.read().decode())
                    self.materials["assets\\"+mat.replace("/","\\")] = material.Material(glm.vec4(materialData["color"]), textures[materialData["texture_path"].removeprefix(".\\assets\\").replace("\\","/")], materialData["tiling_data"],shaders.BaseShaderProgram())

            scenes = []
            for scene in zipFile.infolist():
                if scene.filename.endswith(".roscene"):
                    scenes.append(scene.filename)
            
            self.scenes = scenes.copy()
            for scene in scenes:
                with zipFile.open(scene) as sceneFile:
                    sceneData = ast.literal_eval(sceneFile.read().decode())
                    self.scenes[sceneData["scene_index"]] = scene
                    sceneFile.close()

        self.compiled = compiled

        self.load_scene()

        self.last_time = 0

        print(scenes)

        self.__line_renderer = LineRenderer()

    def get_components(self, gameObject, component_dict : dict[dict[str:list]]):
        components : list[script.script]= []
        print(component_dict)
        for component in component_dict.keys():
            component_code = importlib.import_module(component)

            if isinstance(component_dict[component], dict):
                components.append(getattr(component_code, component_dict[component]["class_name"])(gameObject,component))
                for var in component_dict[component].get("vars",{}).keys():
                    setattr(components[-1], var, component_dict[component].get("vars",{})[var])

                active = component_dict[component].get("active",True)
                components[-1].set_active(active)
                if self.active_camera == None and issubclass(type(components[-1]), light.Camera) and active:
                    self.active_camera = components[-1]

            else:
                for sub_component in range(len(component_dict[component])):
                    components.append(getattr(component_code, component_dict[component][sub_component]["class_name"])(gameObject,component))
                    for var in component_dict[component][sub_component].get("vars",{}).keys():
                        setattr(components[-1], var, component_dict[component].get("vars",{})[var])
                        
                    active = component_dict[component].get("active",True)
                    components[-1].set_active(active)
                    if self.active_camera == None and issubclass(type(components[-1]), Camera) and active:
                        self.active_camera = components[-1]
        
        return components
    
    def get_gameobjects(self):
        return self.scene_objects
    
    def swap_scene(self, new_scene_path:str):
        if not self.compiled:
            with open(new_scene_path) as scene:
                print("test")
                self.scene_objects = []
                self.scene_data = load(scene)
                self.scene = self.scene_data["scene_index"]

                if self.freecam_camera:
                    self.freecam_camera.position = glm.vec3(0,0,0)
                
                for object3d in self.scene_data["3d"].keys():
                    if isinstance(self.scene_data["3d"][object3d], dict):
                        if self.scene_data["3d"][object3d]["mesh_obj"] == "cube":
                            gameObject = gameObjects.gameObject3D(object3d, mesh.Mesh(
                                mesh.Mesh.cube_verts(), self.materials[self.scene_data["3d"][object3d]["material"]]) if self.scene_data["3d"][object3d]["material"] else None,
                                my_transform=transform.transform(
                                    glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                )
                            )
                            gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                            self.scene_objects.append(gameObject)

                        elif self.scene_data["3d"][object3d]["mesh_obj"] == "none":
                            gameObject = gameObjects.gameObject3D(object3d, None,
                                my_transform=transform.transform(
                                    glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                )
                            )
                            gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                            self.scene_objects.append(gameObject)

        else:
            with zipfile.ZipFile("./assets.zip") as zipFile:
                with zipFile.open(self.scenes[self.scene]) as sceneFile:
                    self.scene_data : dict = ast.literal_eval(sceneFile.read().decode().replace("\n", "").replace("\r", ""))
                    self.scene = self.scene_data["scene_index"]

                    self.active_camera = None
                
                    for object3d in self.scene_data["3d"].keys():
                        if isinstance(self.scene_data["3d"][object3d], dict):
                            if self.scene_data["3d"][object3d]["mesh_obj"] == "cube":
                                gameObject = gameObjects.gameObject3D(object3d, mesh.Mesh(
                                    mesh.Mesh.cube_verts(), self.materials[self.scene_data["3d"][object3d]["material"]]),
                                    my_transform=transform.transform(
                                        glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                    )
                                )
                                gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                                self.scene_objects.append(gameObject)

                            else:
                                gameObject = gameObjects.gameObject3D(mesh.Mesh(
                                    np.array([],dtype=np.float32), self.materials[self.scene_data["3d"][object3d]["material"]]),
                                    my_transform=transform.transform(
                                        glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                    )
                                )
                                gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                                self.scene_objects.append(gameObject)

    def swap_scene_idx(self, new_scene_index:int):
        if not self.compiled:
            with open(self.scenes[new_scene_index]) as scene:
                self.scene_objects.clear()
                self.scene_data = load(scene)
                self.scene = new_scene_index
                
                if self.freecam_camera:
                    self.freecam_camera.position = glm.vec3(0,0,0)
                
                for object3d in self.scene_data["3d"].keys():
                    if isinstance(self.scene_data["3d"][object3d], dict):
                        if self.scene_data["3d"][object3d]["mesh_obj"] == "cube":
                            gameObject = gameObjects.gameObject3D(object3d, mesh.Mesh(
                                mesh.Mesh.cube_verts(), self.materials[self.scene_data["3d"][object3d]["material"]]) if self.scene_data["3d"][object3d]["material"] else None,
                                my_transform=transform.transform(
                                    glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                )
                            )
                            gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                            self.scene_objects.append(gameObject)

                        elif self.scene_data["3d"][object3d]["mesh_obj"] == "none":
                            gameObject = gameObjects.gameObject3D(object3d, None,
                                my_transform=transform.transform(
                                    glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                )
                            )
                            gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                            self.scene_objects.append(gameObject)

        else:
            with zipfile.ZipFile("./assets.zip") as zipFile:
                with zipFile.open(self.scenes[new_scene_index]) as sceneFile:
                    self.scene_data : dict = ast.literal_eval(sceneFile.read().decode().replace("\n", "").replace("\r", ""))
                    self.scene = self.scene_data["scene_index"]

                    self.active_camera = None
                
                    for object3d in self.scene_data["3d"].keys():
                        if isinstance(self.scene_data["3d"][object3d], dict):
                            if self.scene_data["3d"][object3d]["mesh_obj"] == "cube":
                                gameObject = gameObjects.gameObject3D(object3d, mesh.Mesh(
                                    mesh.Mesh.cube_verts(), self.materials[self.scene_data["3d"][object3d]["material"]]),
                                    my_transform=transform.transform(
                                        glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                    )
                                )
                                gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                                self.scene_objects.append(gameObject)

                            else:
                                gameObject = gameObjects.gameObject3D(mesh.Mesh(
                                    np.array([],dtype=np.float32), self.materials[self.scene_data["3d"][object3d]["material"]]),
                                    my_transform=transform.transform(
                                        glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                    )
                                )
                                gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                                self.scene_objects.append(gameObject)

    def load_scene(self, camera_class = None):
        if not self.compiled:
            with open(self.scenes[self.scene]) as sceneFile:
                self.scene_objects.clear()

                self.scene_data : dict = load(sceneFile)
                self.freecam_camera = camera_class()
                
                for object3d in self.scene_data["3d"].keys():
                    if isinstance(self.scene_data["3d"][object3d], dict):
                        if self.scene_data["3d"][object3d]["mesh_obj"] == "cube":
                            gameObject = gameObjects.gameObject3D(object3d, mesh.Mesh(
                                mesh.Mesh.cube_verts(), self.materials[self.scene_data["3d"][object3d]["material"]]) if self.scene_data["3d"][object3d]["material"] else None,
                                my_transform=transform.transform(
                                    glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                )
                            )
                            gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                            self.scene_objects.append(gameObject)

                        elif self.scene_data["3d"][object3d]["mesh_obj"] == "none":
                            gameObject = gameObjects.gameObject3D(object3d, None,
                                my_transform=transform.transform(
                                    glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                    glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                )
                            )
                            gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                            self.scene_objects.append(gameObject)

        else:
            with zipfile.ZipFile("./assets.zip") as zipFile:
                with zipFile.open(self.scenes[self.scene]) as sceneFile:
                    self.scene_data : dict = ast.literal_eval(sceneFile.read().decode().strip("\n").strip("\r"))
                
                    for object3d in self.scene_data["3d"].keys():
                        if isinstance(self.scene_data["3d"][object3d], dict):
                            if self.scene_data["3d"][object3d]["mesh_obj"] == "cube":
                                gameObject = gameObjects.gameObject3D(object3d, mesh.Mesh(
                                    mesh.Mesh.cube_verts(), self.materials[self.scene_data["3d"][object3d]["material"]]),
                                    my_transform=transform.transform(
                                        glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                    )
                                )
                                gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                                self.scene_objects.append(gameObject)

                            else:
                                gameObject = gameObjects.gameObject3D(mesh.Mesh(
                                    np.array([],dtype=np.float32), self.materials[self.scene_data["3d"][object3d]["material"]]),
                                    my_transform=transform.transform(
                                        glm.vec3(*self.scene_data["3d"][object3d]["pos"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["rot"]),
                                        glm.vec3(*self.scene_data["3d"][object3d]["scale"])
                                    )
                                )
                                gameObject.set_components(self.get_components(gameObject, self.scene_data["3d"][object3d]['components']))

                                self.scene_objects.append(gameObject)

                    sceneFile.close()

    def update_scene(self, res : tuple):
        gl.glClearColor(*self.scene_data["scenedata"]["skybox_col"])

        if self.last_time == 0:
            self.last_time = time.time()

        cur_time = time.time()
        deltatime = cur_time-self.last_time
        self.last_time = cur_time

        view = glm.lookAt(self.freecam_camera.position, self.freecam_camera.position + self.freecam_camera.front, self.freecam_camera.up)
        projection = glm.perspective(glm.radians(self.freecam_camera.zoom), res[0] / res[1], 0.1, 16384.0)

        self.__line_renderer.update(projection, view)

        for mat in self.materials.values():
            mat.apply_lighting([light_ for gameobject in get_all_objects() for light_ in gameobject.get_components(light.Light)])

        for object in self.scene_objects:
            objects = self.scene_objects.copy()
            objects.remove(object)
            object.update(view, projection, deltatime, objects)

    def add_gameobject(self, new_gameobject:gameObjects.gameObject3D):
        self.scene_objects.append(new_gameobject)

    def update_scene_editor(self, res : tuple):
        gl.glClearColor(*self.scene_data["scenedata"]["skybox_col"])

        if self.last_time == 0:
            self.last_time = time.time()

        cur_time = time.time()
        deltatime = cur_time-self.last_time
        self.last_time = cur_time

        if self.editor_freecam_active:
            mx, my = glfw.get_cursor_pos(self.window.window)
            self.freecam_camera.process_keyboard(deltatime)
            window_size = glfw.get_window_size(self.window.window)
            self.freecam_camera.process_mouse_movement(mx-window_size[0]/2, -my+window_size[1]/2)
            glfw.set_cursor_pos(self.window.window, window_size[0]/2, window_size[1]/2)
        
        if input.get_key_pressed(input.keyCodes.KEY_Z):
            self.editor_freecam_active = not self.editor_freecam_active
            window_size = glfw.get_window_size(self.window.window)
            glfw.set_cursor_pos(self.window.window, window_size[0]/2, window_size[1]/2)

        view = glm.lookAt(self.freecam_camera.position, self.freecam_camera.position + self.freecam_camera.front, self.freecam_camera.up)
        projection = glm.perspective(glm.radians(self.freecam_camera.zoom), res[0] / res[1], 0.1, 16384.0)

        self.__line_renderer.update(projection, view)

        for mat in self.materials.values():
            mat.apply_lighting([light_ for gameobject in get_all_objects() for light_ in gameobject.get_components(light.Light)])

        for object in self.scene_objects:
            objects = self.scene_objects.copy()
            objects.remove(object)
            object.update_without_components(view, projection, deltatime, objects)

    @property
    def line_renderer(self):
        return self.__line_renderer

    def get_scenes(self, path):
        files = []
        for file in os.listdir(path):
            if os.path.isdir(path+"\\"+file):
                subfiles = self.get_scenes(path+"\\"+file)
                files.extend(subfiles)
            elif file.endswith('.roscene'):
                files.append(path+"\\"+file)

        return files
    
    def get_materials(self, path):
        files = []
        for file in os.listdir(path):
            if os.path.isdir(path+"\\"+file):
                subfiles = self.get_materials(path+"\\"+file)
                files.extend(subfiles)
            elif file.endswith('.romat'):
                files.append(path+"\\"+file)
        return files
    
    def save(self):
        def get_components(gameobject:gameObjects.gameObject3D):
            component_dict = {}
            for component in gameobject.components:
                if not component_dict.get(component._path):
                    vars_dict = {}
                    for var in dir(component):
                        if all((not var.startswith("_"), not var=="parent", not callable(getattr(component, var)))):
                            if isinstance(getattr(component, var), (str, list, tuple, int, float, dict, bool)):
                                vars_dict[var] = getattr(component, var)
                            else:
                                vars_dict[var] = getattr(component, var).to_list()

                    component_dict[component._path] = {"class_name":type(component).__name__, "vars":vars_dict}

            return component_dict

        with open(self.scenes[self.scene], "w") as scenefile:
            scenedata = {"scenedata":self.scene_data["scenedata"],"baseCamera":{"name":"playerCam","pos":[0,0,0],"rot":[0,0,0]},"3d":{},"2d":{},"scene_index":self.scene}
            for gameobject in sceneManager.get_gameobjects():
                scenedata["3d"][gameobject.name] = {
                    "mesh_obj":"cube",
                    "components":get_components(gameobject),
                    "pos":gameobject.transform.pos.to_list(),
                    "rot":gameobject.transform.rot.to_list(),
                    "scale":gameobject.transform.scale.to_list(),
                    "material":list(self.materials.keys())[list(self.materials.values()).index(gameobject.mesh.mat)] if gameobject.mesh else None
                }

            dump(scenedata, scenefile)                
    
def create_scene_manager(starting_scene : int, window, compiled = False):
    global sceneManager
    sceneManager = SceneManager(window, starting_scene, compiled=compiled)
    return sceneManager

def get_all_objects():
    if sceneManager:
        return sceneManager.get_gameobjects()