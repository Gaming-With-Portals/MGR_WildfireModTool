import struct

int8 = "b"
uint8 = "B"
int16 = "h"
uint16 = "H"
int32 = "i"
uint32 = "I"
int64 = "q"
uint64 = "Q"
float16 = "e"
float = "f"



class BinaryFile:
    def __init__(self, big=False):
        self.pointer = 0
        self.endiannessheader = "<"
        if big:
            self.endiannessheader = ">"
        else:
            self.endiannessheader = "<"
        self.total_size = 0 # For trimming
        self.file_bytes = bytearray
        
        
        
    
    def open_file_from_bytes(self, file_bytes):
        self.file_bytes = file_bytes
    
    def open_file_from_path(self, path):
        self.file_bytes = open(path, "rb").read()
        
    def read_all(self):
        return self.file_bytes
    
    def read_u8(self) -> int:
        tmp = self.file_bytes[self.pointer]
        self.pointer+=1
        return struct.unpack(uint8, tmp)[0]

    def read_u16(self) -> int:
        tmp = self.file_bytes[self.pointer:self.pointer+2]
        self.pointer+=2
        return struct.unpack(self.endiannessheader + uint16, tmp)[0]

    def read_u32(self) -> int:
        tmp = self.file_bytes[self.pointer:self.pointer+4]
        self.pointer+=4
        return struct.unpack(self.endiannessheader + uint32, tmp)[0]
    
    def seek(self, location):
        self.pointer = int(location)
        
    def read_string(self, length) -> str:
        tmp = self.file_bytes[self.pointer:self.pointer+length]
        self.pointer+=length
        return tmp.decode("utf-8")
    
    def read_bytes(self, length):
        tmp = self.file_bytes[self.pointer:self.pointer+length]
        self.pointer+=length
        return tmp
    
    def write_file(self):
        self.pointer = 0
        self.file_bytes = bytearray(80000)
    
    def advance_pointer(self, amt):
        self.pointer+=amt
        self.total_size+=amt
    
    # TODO Endiness
    def write_char(self, value):
        self.file_bytes[self.pointer:self.pointer + 1] = struct.pack("<s", bytes(value, 'utf-8'))
        self.advance_pointer(1)

    def write_u8(self, value):
        self.file_bytes[self.pointer:self.pointer + 1] = struct.pack("<B", value)
        self.advance_pointer(1)
        
    def write_u16(self, value):
        self.file_bytes[self.pointer:self.pointer + 2] = struct.pack("<H", value)
        self.advance_pointer(2)
        
    def write_16(self, value):
        self.file_bytes[self.pointer:self.pointer + 2] = struct.pack("<h", value)
        self.advance_pointer(2)
        
    def write_u32(self, value):
        self.file_bytes[self.pointer:self.pointer + 4] = struct.pack("<I", value)
        self.advance_pointer(4)
        
    def write_bytes(self, value):
        self.file_bytes[self.pointer:self.pointer + len(value)] = value
        self.advance_pointer(len(value))
    
    def write_string(self, value):
        for x in value:
            self.write_char(x)
    
    def trim(self):
        self.file_bytes[:self.total_size]
        