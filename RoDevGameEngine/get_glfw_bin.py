from PyInstaller.utils.hooks import collect_dynamic_libs

def get_glfw_bin():
    binaries = collect_dynamic_libs('glfw')

    return binaries

if __name__ == "__main__":
    glfw_binaries = get_glfw_bin()
    for binary in glfw_binaries:
        print(binary[0], binary[1])