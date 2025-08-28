import importlib.util
import inspect
from pathlib import Path

task_dir_names=[
    "mapper",
    "printer",
]

def populate_task_queue_for_target_task(queue, target_task):

    current_task = target_task
    while current_task:
        queue.put(current_task)
        
        current_task = current_task.previous_task

    print(f"get_task_queue_for_target_task: {queue}")
    return queue


def get_all():
    found_task_classes = {}

    for task_dir_name in task_dir_names:
        #print(f"{task_dir_name}")
        task_dir_path = Path(__file__).resolve().parent / task_dir_name
        
        # Use pathlib to find all Python files in the directory
        for python_file in Path(task_dir_path).glob("*.py"):
            #print(f"  {python_file}")
            
            # Create a module name from the file path
            module_name = f"{task_dir_name}.{python_file.stem}"
            #print(f"  {module_name}")

            # Create a module spec from the file location
            spec = importlib.util.spec_from_file_location(module_name, python_file)
            if spec and spec.loader:
                
                # Create a module object from the spec
                module = importlib.util.module_from_spec(spec)
                
                # Execute the module to make its contents available
                spec.loader.exec_module(module)

                # Inspect the module for classes
                for class_name, task_class in inspect.getmembers(module, inspect.isclass):
                    #print(f"    {class_name}")
                    
                    # Only use classes defined in the module
                    if task_class.__module__ == module_name: 

                        # Use the printable_name as the key
                        task_cli_name = task_class.cli_name
                        found_task_classes[task_cli_name] = task_class
                        #print(f"Discovered '{task_cli_name}' in {task_class}")

    return found_task_classes
