import ctypes
import os
import sys

class Steam:
    def __init__(self):
        dll_path = os.path.abspath("GameData\\SteamworksWrapper.dll")
        self.__steam = ctypes.CDLL(dll_path)
        # Load the Steamworks DLL (make sure this path is correct)


        # Define the return and argument types
        self.__steam.steam_init.restype = ctypes.c_bool
        self.__steam.create_lobby.argtypes = [ctypes.c_bool, ctypes.c_int]

        # Initialize Steam
        if not self.__steam.steam_init():
            print("Steam failed to initialize.")
            sys.exit(1)

    def get_name(self):
        self.__steam.get_my_name.restype = ctypes.c_char_p
        return self.__steam.get_my_name().decode()

    def register_lobby_creation_callback(self, method):
        self.__steam.register_lobby_create_callback.argtypes = [steam.CALLBACKFUNC_VOID]
        self.__steam.register_lobby_create_callback(method)

    def register_lobby_join_callback(self, method):
        self.__steam.register_lobby_join_callback.argtypes = [steam.CALLBACKFUNC_STRING]
        self.__steam.register_lobby_join_callback(method)

    def register_lobby_list_refresh_callback(self, method):
        self.__steam.register_lobby_list_refresh_callback.argtypes = [steam.CALLBACKFUNC_UINT32]
        self.__steam.register_lobby_list_refresh_callback(method)

    def create_lobby(self, public:bool, max_players:int):
        self.__steam.create_lobby(public, max_players)

    def shutdown(self):
        self.__steam.steam_shutdown()

    def run_callbacks(self):
        self.__steam.run_callbacks()

    def get_lobby_list(self):
        print(self.__steam.get_lobby_list())

    def refresh_lobby_list(self):
        self.__steam.refresh_lobby_list()

    def get_lobby_steamid_off_index(self, idx):
        self.__steam.get_lobby_csteamid_off_index.restype = ctypes.c_uint64
        return self.__steam.get_lobby_csteamid_off_index(idx)
    
    def get_lobby_data_steamID(self, id:ctypes.c_uint64, key:str):
        self.__steam.get_browser_lobby_info.restype = ctypes.c_char_p
        self.__steam.get_browser_lobby_info.argtypes = [ctypes.c_uint64, ctypes.c_char_p]
        return self.__steam.get_browser_lobby_info(id, ctypes.c_char_p(key.encode()))
    
    def set_lobby_info(self, key:str, value:str):
        self.__steam.set_lobby_info.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.__steam.set_lobby_info(ctypes.c_char_p(key.encode()), ctypes.c_char_p(value.encode()))
   
    CALLBACKFUNC_VOID = ctypes.CFUNCTYPE(None)
    CALLBACKFUNC_UINT32 = ctypes.CFUNCTYPE(None, ctypes.c_uint32)
    CALLBACKFUNC_STRING = ctypes.CFUNCTYPE(None, ctypes.c_char_p)

steam = Steam()
try:
    # Define your Python callback
    @steam.CALLBACKFUNC_VOID
    def on_lobby_created():
        print("🎉 Lobby was successfully created! (Callback from C++)")

    @steam.CALLBACKFUNC_STRING
    def on_lobby_joined(name):
        print("%s joined the lobby!"%name)

    can_continue = False
    host = True
    @steam.CALLBACKFUNC_UINT32
    def on_lobby_list_refresh(lobbies : ctypes.c_uint32):
        for i in range(lobbies):
            steam_id = steam.get_lobby_steamid_off_index(i)
            print(steam.get_lobby_data_steamID(steam_id, "lobbyName"))

        global can_continue, host

        host = True if input("Do you want to host?")=="y" else False

        can_continue = True

    # Register the callback with the DLL
    steam.register_lobby_creation_callback(on_lobby_created)
    steam.register_lobby_join_callback(on_lobby_joined)    
    steam.register_lobby_list_refresh_callback(on_lobby_list_refresh)    

    steam.refresh_lobby_list()

    while not can_continue:
        steam.run_callbacks()

    if (host):
        steam.create_lobby(True, 4)
        steam.set_lobby_info("lobbyName", steam.get_name())

    while True:
        steam.run_callbacks()
except Exception as e:
    print(e)
    steam.shutdown()