class Steam:
    def __init__(self):
        import ctypes

        self.steamAPI = ctypes.CDLL("GameData/steam_api64")

        print(self.steamAPI.SteamAPI_Init())

        while True:
            pass

if __name__ == "__main__":
    Steam()