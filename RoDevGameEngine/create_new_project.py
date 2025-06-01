import os, shutil

class Project:
    def __init__(self, project_name:str):
        if not os.path.isdir("C:\\RoDevGameEngine\\"):
            os.mkdir("C:\\RoDevGameEngine\\")
            shutil.copytree("RoDevGameEngine", "C:\\RoDevGameEngine\\RoDevGameEngine")

        if not os.path.isdir("C:\\RoDevGameEngine\\Projects\\"):
            os.mkdir("C:\\RoDevGameEngine\\Projects\\")

        if os.path.isdir("C:\\RoDevGameEngine\\Projects\\%s"%project_name):
            raise Exception()

        os.mkdir("C:\\RoDevGameEngine\\Projects\\%s"%project_name)

        shutil.copytree("C:\\RoDevGameEngine\\RoDevGameEngine", "C:\\RoDevGameEngine\\Projects\\%s\\Engine"%project_name)

        with open("C:\\RoDevGameEngine\\Projects\\%s\\main.json"%project_name, "w") as project_json:
            project_json.write("""
            {
                "startingScene":0,
                "projectName":"TestProjectOne"
            }
            """)

        with open("C:\\RoDevGameEngine\\Projects\\%s\\%s.py"%(project_name,project_name), "w") as project_file:
            with open("C:\\RoDevGameEngine\\RoDevGameEngine\\main.py", "r") as sample_proj_file:
                project_file.write(sample_proj_file.read())

                sample_proj_file.close()

            project_file.close()

        os.mkdir("C:\\RoDevGameEngine\\Projects\\%s\\assets"%project_name)

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
        