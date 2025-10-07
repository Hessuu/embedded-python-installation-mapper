from epim.file_object import *
from epim.util.color_string import *
from epim.util.file_object_size import *
from epim.util.logging import *

class PythonInstallationReport:
    def __init__(self):

        # All file types in the installation
        self.file_suffixes_encountered = set()

        # All files
        self.total_size = RealSize(0)

        # Directories        
        self.directories_size = RealSize(0)

        # By file type
        self.python_source_files_size = RealSize(0)
        self.python_bytecode_files_size = RealSize(0)
        self.so_files_size = RealSize(0)
        self.other_files_size = RealSize(0)
        
        # By file object status
        self.useful_size = RealSize(0)
        self.required_modules_size = RealSize(0)
        self.not_required_modules_size = RealSize(0)
        self.useless_size = RealSize(0)
        self.not_handled_size = RealSize(0)
        self.not_found_size = RealSize(0)
        self.unknown_size = RealSize(0)

    def add_file_object_data(self, file_object):
        file_object_path = file_object.path
        file_object_size = file_object.real_size
        file_object_suffix = "".join(file_object_path.suffixes) # Get the full type.
        file_object_status = file_object.get_status()
        file_object_content_type = file_object.file_object_content_type

        self.total_size += file_object_size


        if file_object.file_object_type == FileObjectType.DIRECTORY:
            # Directories should only be counted here.
            self.directories_size += file_object_size
        else:
            # Only files have a meaningful type.
            self.file_suffixes_encountered.add(file_object_suffix)

            # Add size to groups by type.
            if file_object_content_type == FileObjectContentType.PYTHON_SCRIPT:
                self.python_source_files_size += file_object_size
            elif file_object_content_type == FileObjectContentType.PYTHON_BYTECODE:
                self.python_bytecode_files_size += file_object_size
            elif ".so" in file_object_suffix:
                self.so_files_size += file_object_size
            else:
                self.other_files_size += file_object_size

        # Check for by type size errors.        
        assert(self.total_size ==
            self.directories_size +
            self.python_source_files_size +
            self.python_bytecode_files_size +
            self.so_files_size + 
            self.other_files_size
        )

        # Add size to groups by status
        if file_object_status == FileObjectStatus.USEFUL:
            self.useful_size += file_object_size
        elif file_object_status == FileObjectStatus.REQUIRED_MODULE:
            self.required_modules_size += file_object_size
        elif file_object_status == FileObjectStatus.NOT_REQUIRED_MODULE:
            self.not_required_modules_size += file_object_size
        elif file_object_status == FileObjectStatus.USELESS:
            self.useless_size += file_object_size
        elif file_object_status == FileObjectStatus.NOT_HANDLED:
            self.not_handled_size += file_object_size
        elif file_object_status == FileObjectStatus.DIRECTORY:
            # Directories already handled.
            pass
        elif file_object_status == FileObjectStatus.UNKNOWN:
            self.unknown_size += file_object_size
        else:
            assert False

        # Check for by status size errors.
        assert(self.total_size ==
            self.directories_size +
            self.useful_size +
            self.required_modules_size +
            self.not_required_modules_size +
            self.useless_size +
            self.not_handled_size +
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
        print(f"# Size by type #")
        print(f"Source files:    {self.python_source_files_size.format(align=True)} | {self.python_source_files_size.format(unit=SizeUnit.KIB)}")
        print(f"Bytecode files:  {self.python_bytecode_files_size.format(align=True)} | {self.python_bytecode_files_size.format(unit=SizeUnit.KIB)}")
        print(f".so files:       {self.so_files_size.format(align=True)} | {self.so_files_size.format(unit=SizeUnit.KIB)}")
        print(f"Directories:     {self.directories_size.format(align=True)} | {self.directories_size.format(unit=SizeUnit.KIB)}")
        print(f"Other files:     {self.other_files_size.format(align=True)} | {self.other_files_size.format(unit=SizeUnit.KIB)}")
        print()
        print()
        print(f"# Size by status #")
        print(ColorString.dark_green( f"Useful files:         {self.useful_size.format(align=True)} | {self.useful_size.format(unit=SizeUnit.KIB)}"))
        print(ColorString.green(      f"Required modules:     {self.required_modules_size.format(align=True)} | {self.required_modules_size.format(unit=SizeUnit.KIB)}"))
        print(ColorString.red(        f"Not required modules: {self.not_required_modules_size.format(align=True)} | {self.not_required_modules_size.format(unit=SizeUnit.KIB)}"))
        print(ColorString.dark_red(   f"Useless files:        {self.useless_size.format(align=True)} | {self.useless_size.format(unit=SizeUnit.KIB)}"))
        print(ColorString.white(      f"Not handled files:    {self.not_handled_size.format(align=True)} | {self.not_handled_size.format(unit=SizeUnit.KIB)}"))
        # Don't print not found file size.
        print(ColorString.purple(     f"Unknown files:        {self.unknown_size.format(align=True)} | {self.unknown_size.format(unit=SizeUnit.KIB)}"))
        print()

    
    # TODO: print sizes and file object counts here instead:
    def __print_encountered_file_types(self):
        
        _MAX_ROW_LENGTH = 100
        string = ""
        
        for i, file_type_str in enumerate(sorted(self.file_suffixes_encountered)):
            string += "'" + file_type_str + "'" + " "
            
            if len(string) > _MAX_ROW_LENGTH or i + 1 >= len(self.file_suffixes_encountered):
                print(string)
                string = ""
