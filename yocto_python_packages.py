import os
import settings
import glob

from yocto_package import YoctoPackage

def get_subdirs(parent_dir):
    return [f.path for f in os.scandir(parent_dir) if f.is_dir()]

def is_proper_package(path):
    if (
            not os.path.isdir(path) or
            path.endswith("-dbg") or
            path.endswith("-dev") or
            path.endswith("-doc") or
            path.endswith("-lic") or
            path.endswith("-locale") or
            path.endswith("-src") or
            path.endswith("-staticdev") or
            path.endswith("-unneeded") or
            path.endswith("-tests") or
            path.endswith("-ptest")
    ):
        return False
    else:
        return True

def get_yocto_python_packages():
    
    packages = []
    
    for recipe_dir in glob.glob(settings.WORK_ROOT + "/python*"):
        for package_dir in glob.glob(recipe_dir + "/*/packages-split/*"):
            if is_proper_package(package_dir):
                packages.append(YoctoPackage(os.path.basename(package_dir), os.path.basename(recipe_dir), package_dir))
    
    return packages
