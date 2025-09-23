from epim.file_object import *
from epim.util.file_object_size import *
from epim.util.logging import *

class PythonInstallationReport:
    def __init__(self):

        # All file types in the installation
        self.file_types_encountered = set()

        # All files
        self.total_size = RealSize(0)

        # Directories        
        self.directories_size = RealSize(0)

        # By file type
        self.py_files_size = RealSize(0)
        self.pyc_files_size = RealSize(0)
        self.so_files_size = RealSize(0)
        self.other_files_size = RealSize(0)
        
        # By file object status
        self.required_size = RealSize(0)
        self.not_required_size = RealSize(0)
        self.useless_size = RealSize(0)
        self.not_handled_size = RealSize(0)
        self.not_found_size = RealSize(0)
        self.unknown_size = RealSize(0)

    def add_file_object_data(self, file_object):
        file_object_path = file_object.path
        file_object_size = file_object.real_size
        file_object_type = file_object_path.suffix
        file_object_status = file_object.get_status()

        self.total_size += file_object_size


        if file_object.file_object_type == FileObjectType.DIRECTORY:
            # Directories should only be counted here.
            self.directories_size += file_object_size
        else:
            # Only files have a meaningful type.
            self.file_types_encountered.add(file_object_type)

            # Add size to groups by type
            match file_object_type:
                case ".py":
                    self.py_files_size += file_object_size
                case ".pyc":
                    self.pyc_files_size += file_object_size
                case ".so":
                    self.so_files_size += file_object_size
                case _:
                    self.other_files_size += file_object_size

        # Check for by type size errors.        
        assert(self.total_size ==
            self.directories_size +
            self.py_files_size +
            self.pyc_files_size +
            self.so_files_size + 
            self.other_files_size
        )

        # Add size to groups by status
        match file_object_status:
            case FileObjectStatus.REQUIRED:
                self.required_size += file_object_size
            case FileObjectStatus.NOT_REQUIRED:
                self.not_required_size += file_object_size
            case FileObjectStatus.USELESS:
                self.useless_size += file_object_size
            case FileObjectStatus.NOT_HANDLED:
                self.not_handled_size += file_object_size
            case FileObjectStatus.NOT_FOUND:
                self.not_found_size += file_object_size
            case FileObjectStatus.DIRECTORY:
                # Directories already handled.
                pass
            case FileObjectStatus.UNKNOWN:
                self.unknown_size += file_object_size
            case _:
                assert False
        
        # Check for by status size errors.
        assert(self.total_size ==
            self.directories_size +
            self.required_size +
            self.not_required_size +
            self.useless_size +
            self.not_handled_size +
            self.not_found_size +
            self.unknown_size
        )
        
        # TODO: check existence of additional installation files!
        # We should not have any not found file at this point.
        #assert self.not_found_size == RealSize(0)


    def print_report(self):

        print(f"############################")
        print(f"## FILE TYPES ENCOUNTERED ##")
        self.__print_encountered_file_types()
        print()
        print(f"## INSTALLATION SIZE ##")
        print()
        print(f"Total:       {self.total_size.format(align=True)} | {self.total_size.format(unit=SizeUnit.KIB)}")
        print()
        print(f".py files:   {self.py_files_size.format(align=True)} | {self.py_files_size.format(unit=SizeUnit.KIB)}")
        print(f".pyc files:  {self.pyc_files_size.format(align=True)} | {self.pyc_files_size.format(unit=SizeUnit.KIB)}")
        print(f".so files:   {self.so_files_size.format(align=True)} | {self.so_files_size.format(unit=SizeUnit.KIB)}")
        print(f"Directories: {self.directories_size.format(align=True)} | {self.directories_size.format(unit=SizeUnit.KIB)}")
        print(f"Other files: {self.other_files_size.format(align=True)} | {self.other_files_size.format(unit=SizeUnit.KIB)}")
        print()
        # TODO: color code these.
        print(f"Required files:     {self.required_size.format(align=True)} | {self.required_size.format(unit=SizeUnit.KIB)}")
        print(f"Not required files: {self.not_required_size.format(align=True)} | {self.not_required_size.format(unit=SizeUnit.KIB)}")
        print(f"Useless files:      {self.useless_size.format(align=True)} | {self.useless_size.format(unit=SizeUnit.KIB)}")
        print(f"Not handled files:  {self.not_handled_size.format(align=True)} | {self.not_handled_size.format(unit=SizeUnit.KIB)}")
        # Don't print not found file size.
        print(f"Unknown files:      {self.unknown_size.format(align=True)} | {self.unknown_size.format(unit=SizeUnit.KIB)}")
        print()

    
    # TODO: print sizes and file object counts here instead:
    def __print_encountered_file_types(self):
        
        _MAX_ROW_LENGTH = 100
        string = ""
        
        for i, file_type_str in enumerate(sorted(self.file_types_encountered)):
            string += "'" + file_type_str + "'" + " "
            
            if len(string) > _MAX_ROW_LENGTH or i + 1 >= len(self.file_types_encountered):
                print(string)
                string = ""
