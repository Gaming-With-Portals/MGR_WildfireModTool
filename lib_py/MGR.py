from lib_py import BinaryLib as bl
from lib_py import DatFile
import struct, os, math, zlib
from typing import List, Tuple
from dataclasses import dataclass


class DatHeader:
    def __init__(self):
        self.Magic = ""
        self.FileAmount = 0
        self.PositionsOffset = 0
        self.ExtensionsOffset = 0
        self.NamesOffset = 0
        self.HashMapOffset = 0
        self.SizesOffset = 0

class DatHashData:
    def __init__(self):
        self.PrehashShift = 0
        self.BucketOffsets = []
        self.Hashes = []
        self.Indices = []
        self.StructSize = 0


class DatReader:
    def __init__(self):
        pass
    
    def read_file(self, f_bytes, name):
        nameSize = 1
        Files = []
        
        reader = bl.BinaryFile(False)
        reader.open_file_from_bytes(f_bytes)
        header = DatHeader()
        
        header.Magic = reader.read_string(4)
        header.FileAmount = reader.read_u32()
        header.PositionsOffset = reader.read_u32()
        header.ExtensionsOffset = reader.read_u32()
        header.NamesOffset = reader.read_u32()
        header.SizesOffset = reader.read_u32()
        header.HashMapOffset = reader.read_u32()
        
        reader.seek(header.PositionsOffset)
        fileOffsets = []
        for x in range(header.FileAmount):
            fileOffsets.append(reader.read_u32())
            
        reader.seek(header.SizesOffset)
        fileSizes = []
        for x in range(header.FileAmount):
            fileSizes.append(reader.read_u32())
            
        reader.seek(header.NamesOffset)
        nameSize = reader.read_u32()
        fileNames = []
        for x in range(header.FileAmount):
            fileNames.append(reader.read_string(nameSize))
        
        for x in range(header.FileAmount):
            filePosition = fileOffsets[x]
            fileSize = fileSizes[x]
            fileName = fileNames[x]
            
            
            reader.seek(filePosition)
            tmp = DatFile.File(fileName.rstrip('\x00'), reader.read_bytes(fileSize))
                
            
            
            Files.append(tmp)
            
        return Files
            
    def save_file(self, files):
        print("Saving file...")
        reader = bl.BinaryFile()
        
        header = DatHeader()
        
        longestFileName = 0
        offsets = []
        sizes = []
        extensions = []
        names = []
        
        reader.write_file()
        
        for file in files:
            if longestFileName < len(file.f_name):
                longestFileName = len(file.f_name)
            
            sizes.append(len(file.f_data))
            extensions.append(os.path.splitext(file.f_name)[1])
            names.append(file.f_name)
            
        longestFileName+=1
        header.FileAmount = len(files)
        header.PositionsOffset = 0x20
        header.ExtensionsOffset = 0x20 + (4 * header.FileAmount)
        header.NamesOffset = header.ExtensionsOffset + (4 * header.FileAmount)
        header.SizesOffset = header.NamesOffset + (longestFileName * header.FileAmount) + 4
        header.HashMapOffset = header.SizesOffset + (4 * header.FileAmount)

        # Me when hashing :SamGrin:
        hashData = self.generate_hash_data(files)
        
        TempPos = header.HashMapOffset + hashData.StructSize + (2 * header.FileAmount)
        startpad = self.calcpadding(16, TempPos)
        
        _pointer = TempPos + startpad
        
        for file in files:
            offsets.append(_pointer)
            _pointer += len(file.f_data)
            pad = self.calcpadding(16, _pointer)
            _pointer += pad
        
        reader.write_string('DAT')
        reader.write_u8(0)
        reader.write_u32(header.FileAmount)
        reader.write_u32(header.PositionsOffset)
        reader.write_u32(header.ExtensionsOffset)
        reader.write_u32(header.NamesOffset)
        reader.write_u32(header.SizesOffset)
        reader.write_u32(header.HashMapOffset)
        reader.write_u32(0)
        
        reader.seek(header.PositionsOffset)
        for i in range(header.FileAmount):
            reader.write_u32(offsets[i])
        
        reader.seek(header.ExtensionsOffset)
        for i in range(header.FileAmount):
            reader.write_string(extensions[i])
            reader.write_u8(0)
        
        reader.seek(header.NamesOffset)
        reader.write_u32(longestFileName)
        
        for i in range(header.FileAmount):
            reader.write_string(names[i])
            for x in range((longestFileName - len(names[i]))):
                reader.write_u8(0)
                
        reader.seek(header.SizesOffset)
        for i in range(header.FileAmount):
            reader.write_u32(sizes[i])
        
        reader.seek(header.HashMapOffset)
        reader.write_u32(hashData.PrehashShift)
        reader.write_u32(16)
        reader.write_u32(16)
        reader.write_u32(16 + len(hashData.BucketOffsets) * 2)
        reader.write_u32(16 + (len(hashData.BucketOffsets) * 2) + (len(hashData.Hashes) * 4))
        
        for i in range(len(hashData.BucketOffsets)):
            reader.write_16(hashData.BucketOffsets[i])
            
        for i in range(header.FileAmount):
            reader.write_u32(hashData.Hashes[i])
        
        for i in range(header.FileAmount):
            reader.write_16(hashData.Indices[i])
        
        hashPad = self.calcpadding(16, reader.pointer)
        for i in range(hashPad):
            reader.write_u8(0)
        
        for i in range(header.FileAmount):
            if offsets[i] > len(reader.read_all()):
                extend = offsets[i] - len(reader.read_all())
                j = 0
                while j < extend:
                    j+=1
                    reader.write_u8(0)
            reader.seek(offsets[i])
            reader.write_bytes(files[i].f_data)
        reader.trim()
        
        total_bytes = reader.read_all()
        file_size_in_mb = len(total_bytes) * 1e-6
        if file_size_in_mb > 80:
            quit()
        
        return reader.read_all()    

    def calcpadding(self, BlockSize, Length):
        return BlockSize - (Length % BlockSize)

    # https://github.com/Petrarca181/MAMMT/blob/master/MAMMT/Workers/0_Dat_Repacktor.cs
    def crc32_hash_to_uint32(self, data: bytes) -> int:
        return zlib.crc32(data) & 0xFFFFFFFF

    def to_signed_short(self, n: int) -> int:
        """Convert an integer to a signed 16-bit integer."""
        return n if n < (1 << 15) else n - (1 << 16)

    def generate_hash_data(self, files: DatFile.File) -> DatHashData:
        file_amount_length = int(math.log(len(files), 2)) + 1
        prehash_shift = min(31, 32 - file_amount_length)
        bucket_size = 1 << (31 - prehash_shift)
        bucket_offsets = [-1] * bucket_size

        hash_tuple = sorted(
            ((self.crc32_hash_to_uint32(file.f_name.lower().encode('ascii')) & 0x7FFFFFFF, i) for i, file in enumerate(files)),
            key=lambda x: x[0] >> prehash_shift
        )

        for i in range(len(files)):
            bucket_index = hash_tuple[i][0] >> prehash_shift
            if bucket_offsets[bucket_index] == -1:
                bucket_offsets[bucket_index] = self.to_signed_short(i)
        tmp = DatHashData()
        tmp.PrehashShift = prehash_shift
        tmp.BucketOffsets = bucket_offsets
        tmp.Hashes = [x[0] for x in hash_tuple]
        tmp.Indices = [x[1] for x in hash_tuple]   
        tmp.StructSize = 4 + 2 * len(bucket_offsets) + 4 * len(hash_tuple) + 2 * len(hash_tuple)


        return tmp

        
        
        

            
if __name__ == "__main__":
    file = bl.BinaryFile(False)
    file.open_file_from_path("C:\\Users\\cashc\\Desktop\\Projects\\WildfireModTool\\lib\\em0310.dat")
    datreader = DatReader()
    datreader.read_file(file.file_bytes)

def get_wmb_type(bytes):
    wmb = bl.BinaryFile(False)
    wmb.open_file_from_bytes(bytes)
    if wmb.read_u32() == 876760407:
        return "WMB4 (MGR:R)"
    if wmb.read_u32() == 859983191:
        return "WMB3 (Nier)"
    
def get_scr_type(bytes):
    wmb = bl.BinaryFile(False)
    wmb.open_file_from_bytes(bytes)
    wmb.seek(0x06)
    model_count = wmb.read_u16()
    if  model_count > 0:
        wmb.seek(0x10)
        wmb.seek(wmb.read_u32())
        wmb.seek(wmb.read_u32())
        if wmb.read_u32() == 876760407:
            return "WMB4 (MGR:R)" + "\nModel Count: " + str(model_count)
        if wmb.read_u32() == 859983191:
            return "WMB3 (Nier)" + "\nModel Count: " + str(model_count)
    else:
        return "There are no models in this file"

def get_ly2_metadata(bytes):
    ly2 = bl.BinaryFile(False)
    ly2.open_file_from_bytes(bytes)
    ly2.read_u32()
    flags = ly2.read_u32()
    prop_type_count = ly2.read_u32()
    ly2.read_u32()
    ly2.read_u32()
    names = ""
    for i in range(prop_type_count):
        instanceFlags = list(struct.unpack("<II", ly2.read_bytes(8)))
        prop_category = ly2.read_bytes(2).decode("ascii")
        if prop_category not in {"ba", "bh", "bm"}:
            ly2.read_bytes(10)
            continue
        prop_id = "%04x" % struct.unpack("<H", ly2.read_bytes(2))[0]
        prop_name = prop_category + prop_id + ".dat"
        
        instancesPointer, instancesCount = struct.unpack("<II", ly2.read_bytes(8))
        names = names + prop_name + " (x" + str(instancesCount) + ")" + "\n" 
    
    return "Props:\n" + names 
    

def get_wta_metadata(bytes):
    wta = bl.BinaryFile(False)
    wta.open_file_from_bytes(bytes)
    magic = wta.read_bytes(4)
    version = wta.read_u32()
    num_files = wta.read_u32()
    
    return "WTA Version: " + str(version) + "\nWTP File Count: " + str(num_files)

def get_mot_metadata(bytes):
    mot = bl.BinaryFile(False)
    mot.open_file_from_bytes(bytes)    
    mot.read_u32()
    mot.read_u32()
    mot.read_u16()
    frameCount = mot.read_u16()
    mot.read_u32()
    mot.read_u32()
    animationName = mot.read_bytes(20).decode("utf-8", errors="replace").rstrip("\0")
    
    return "Framecount: " + str(frameCount) + "\nDuration: " + str(round((frameCount / 60) * 100) / 100) + "s"