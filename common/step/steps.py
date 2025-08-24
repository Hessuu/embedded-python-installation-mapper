
from common.util.logging import print

from ._step_1_map_yocto_packages import MapYoctoPackages
from ._step_2_add_target_yocto_packages import AddTargetYoctoPackages
from ._step_3_check_target_files import CheckTargetFiles
from ._step_4_map_target_modules import MapTargetModules
from ._step_5_map_target_dependencies import MapTargetDependencies
from ._step_6_map_unimported_target_modules import MapUnimportedTargetModules

all = {
    MapYoctoPackages.cli_name:              MapYoctoPackages,
    AddTargetYoctoPackages.cli_name:        AddTargetYoctoPackages,
    CheckTargetFiles.cli_name:              CheckTargetFiles,
    MapTargetModules.cli_name:              MapTargetModules,
    MapTargetDependencies.cli_name:         MapTargetDependencies,
    MapUnimportedTargetModules.cli_name:    MapUnimportedTargetModules,
}

def populate_step_queue_for_target_step(queue, target_step):

    current_step = target_step
    while current_step:
        queue.put(current_step)
        
        current_step = current_step.previous_step

    print(f"get_step_queue_for_target_step: {queue}")
    return queue
