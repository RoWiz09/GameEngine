from PyInstaller.utils.hooks import collect_dynamic_libs

def get_glfw_bin():
    binaries = collect_dynamic_libs('glfw')

    return binaries