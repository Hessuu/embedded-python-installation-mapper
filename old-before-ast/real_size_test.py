
import os, math, stat

def get_block_size():
    statvfs_result = os.statvfs(".")
    return statvfs_result.f_bsize

block_size = get_block_size()

def get_path_size(path):
    stat_info = os.lstat(path)
    return stat_info.st_blocks * 512

def get_directory_size_new(path):
    total_size = 0
    seen_inodes = set()
    
    for dirpath, dirnames, filenames in os.walk(path):
        stat_info = os.lstat(dirpath)
        inode_id = (stat_info.st_dev, stat_info.st_ino)
        if inode_id not in seen_inodes:
            total_size += get_path_size(dirpath)
            seen_inodes.add(inode_id)

        for f in filenames:
            filepath = os.path.join(dirpath, f)
            try:
                stat_info = os.lstat(filepath)
            except OSError:
                continue

            if not os.path.islink(filepath) and os.path.isfile(filepath):
                inode_id = (stat_info.st_dev, stat_info.st_ino)
                if inode_id in seen_inodes:
                    continue

                total_size += get_path_size(filepath)
                seen_inodes.add(inode_id)

    return total_size


def format_size(size, unit=None):
    for unit_candidate in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == unit_candidate:
            break
        size /= 1024
    
    size = size
    return f"{size:.1f} {unit_candidate}"


def print_total_size(path):
    total_size = get_directory_size_new(path)

    print(format_size(total_size, "KB"))
    print(format_size(total_size))




print_total_size("/")

