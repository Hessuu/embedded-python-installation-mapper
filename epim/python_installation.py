from epim.package_collection import *
from epim.python_module_collection import *
from epim.util.decorators import *

class PythonInstallation(object):
    
    def __init__(self):
        # Python packages present on target.
        self.python_packages = PackageCollection()
        # Python file objects present on target.
        self.file_objects = {}
        
        # Python modules discovered from target.
        self.python_modules = PythonModuleCollection()


    @host_only
    def populate(self, all_python_packages):
        
        for package_path, package in all_python_packages.items():
            
            # Check which packages are present on target.
            if not package.found_on_target:
                print(f"❌ Not found on target | {package.name} ({package.recipe_name})")
            else:
                print(f"✅ Found on target     | {package.name} ({package.recipe_name})")
                
                # Update the list of file objects with packages on target.
                for file_object_path, file_object in package.file_objects.items():
                    
                    # For each file object, check first if it is already in our file objects.
                    if file_object_path in self.file_objects:
                        # If it is, update the package to use our file object instance.
                        # This happens often with directories, which can be in multiple packages.
                        package.file_objects[file_object_path] = self.file_objects[file_object_path]
                    else:
                        # If it is not, add to our file objects.
                        self.file_objects[file_object_path] = file_object
                
                
                # Finally, add found package to our packages.
                self.python_packages[package_path] = package
    
    @target_only
    def add_additional_file_objects_on_target(self, additional_directories_on_target):

        # Add file objects from target that were not already part of Yocto packages.
        for additional_directory_path in additional_directories_on_target:

            if not additional_directory_path.is_dir():
                print(f"WARNING: Additional installation directory is not a directory: {additional_directory_path}")
                continue

            for file_object_path in additional_directory_path.rglob("*"):
                if not file_object_path in self.file_objects:
                    print(f"🔎 Found additional Python file object from target: {file_object_path}")

                    file_object = FileObject(file_object_path, None)

                    self.file_objects[file_object_path] = file_object

    @target_only
    def update_file_object_data_on_target(self):
        # Update file object data for each file object on target
        for file_object in self.file_objects.values():
            file_object.update_data_on_target(self.file_objects)

    @host_only
    def link_python_modules_to_file_objects(self):
        for python_module in self.python_modules.values():

            if python_module.path in self.file_objects:
                file_object = self.file_objects[python_module.path]

                file_object.link_python_module(python_module)

            else:
                if python_module.is_built_in:
                    continue
                if python_module.is_entry_point:
                    print(f"Entry point not found from packages, ignoring: {python_module.path}")
                    continue

                raise Exception(f"Module not found from packages: {python_module}")

        # TODO: Check that all Python files in all packages have been handled in some way
