# Import the necessary PyInstaller hooks
from PyInstaller.utils.hooks import collect_dynamic_libs

# Specify the binaries in the spec file
binaries = collect_dynamic_libs('glfw')

# Print the binaries to copy
print(binaries)