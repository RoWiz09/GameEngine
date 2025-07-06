import ctypes
import sys
from ctypes import *

class Steam:
    def __init__(self):
        # Load DLL (you can hardcode path if needed)
        #dll_path = "/".join(sys.executable.split("\\")[:-1]) + "/GameData/steam_api64.dll"
        dll_path = "GameData/steam_api64.dll"
        self.steam = ctypes.CDLL(dll_path)

        # Restart app if necessary
        self.steam.SteamAPI_RestartAppIfNecessary.argtypes = [c_uint32]
        self.steam.SteamAPI_RestartAppIfNecessary.restype = c_bool
        if self.steam.SteamAPI_RestartAppIfNecessary(480):  # Use your own App ID here
            raise RuntimeError("Restarted through Steam required.")

        # Init normal (non-flat) API
        self.steam.SteamAPI_Init.restype = c_bool
        if not self.steam.SteamAPI_Init():
            raise RuntimeError("SteamAPI_Init failed!")
        
        class ISteamFriends:
            def __init__(self, ptr, steamDLL):
                self.__friends_ptr = ptr

                self.__steam = steamDLL

                self.__steam.SteamAPI_ISteamFriends_GetFriendCount.argtypes = [c_void_p, c_int]
                self.__steam.SteamAPI_ISteamFriends_GetFriendCount.restype = c_int

                self.__steam.SteamAPI_ISteamFriends_GetFriendByIndex.argtypes = [c_void_p, c_int, c_int]
                self.__steam.SteamAPI_ISteamFriends_GetFriendByIndex.restype = c_uint64

                self.__steam.SteamAPI_ISteamFriends_GetFriendPersonaName.argtypes = [c_void_p, c_uint64]
                self.__steam.SteamAPI_ISteamFriends_GetFriendPersonaName.restype = c_char_p

                self.__steam.SteamAPI_ISteamFriends_GetPersonaName.argtypes = [c_void_p]
                self.__steam.SteamAPI_ISteamFriends_GetPersonaName.restype = c_char_p

                self.__steam.SteamAPI_ISteamFriends_ActivateGameOverlay.argtypes = [c_void_p, c_char_p]
                self.__steam.SteamAPI_ISteamFriends_ActivateGameOverlay.restype = None

                self.__EFriendFlagImmediate = 0x04

            def getMyName(self) -> str:
                myName:bytes = self.__steam.SteamAPI_ISteamFriends_GetPersonaName(self.__friends_ptr)

                return myName.decode()

            def getFriendByIndex(self, index) -> str:
                steam_id = self.__steam.SteamAPI_ISteamFriends_GetFriendByIndex(self.__friends_ptr, index, self.__EFriendFlagImmediate)
                name_ptr:bytes = self.__steam.SteamAPI_ISteamFriends_GetFriendPersonaName(self.__friends_ptr, steam_id)

                return name_ptr.decode()

            def getFriendCount(self) -> int:
                return self.__steam.SteamAPI_ISteamFriends_GetFriendCount(self.__friends_ptr, self.__EFriendFlagImmediate)

            def openFriendsOverlay(self):
                self.__steam.SteamAPI_ISteamFriends_ActivateGameOverlay(self.__friends_ptr, b"friends")

        # Get ISteamFriends pointer using versioned accessor
        self.steam.SteamAPI_SteamFriends_v017.restype = c_void_p
        friends_ptr = self.steam.SteamAPI_SteamFriends_v017()
        if not friends_ptr:
            raise RuntimeError("Failed to get ISteamFriends pointer")
        
        self.steamFriends = ISteamFriends(friends_ptr, self.steam)

        
        # Initalize ISteamMatchmaking
        class ISteamMatchmaking:
            def __init__(self, ptr, steam):
                self.__matchmaking_ptr = ptr
                self.__steam = steam
        
        # Get ISteamMatchmaking pointer
        self.steam.SteamAPI_SteamMatchmaking_v009.restype = c_void_p
        matchmaking_ptr = self.steam.SteamAPI_SteamMatchmaking_v009()
        if not matchmaking_ptr:
            raise RuntimeError("Failed to get ISteamMatchmaking pointer")

        self.steamMatchmaking = ISteamMatchmaking(matchmaking_ptr, self.steam)

if __name__ == "__main__":
    try:
        steam = Steam()
        print(steam.steamFriends.getFriendCount())
    except Exception as e:
        print(f"Error: {e}")
        while True:
            pass
