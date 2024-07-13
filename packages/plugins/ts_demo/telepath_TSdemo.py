from plugins.utils.rosetta import Rosetta

class TypeScriptDemo(Rosetta):
    def __init__(self):
        super().__init__()
        super().url = "http://localhost:3000"
