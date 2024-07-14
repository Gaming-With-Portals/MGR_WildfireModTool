from lib_py import MGR


class File:
    def __init__(self, name, data, container=False, parent="") -> None:
        self.f_name = name
        self.f_data = data
        self.is_container = container
        self.parent = parent
        self.contained_files = []

class ContainerFile:
    def __init__(self) -> None:
        self.f_name
        self.contained_files = []
        
    def _create_container(file_bytes):
        datreader = MGR.DatReader()
        datreader.read_file(file_bytes)