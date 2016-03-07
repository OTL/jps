from multiprocessing import Process
import importlib

def launch_modules(module_names):
    '''launch module.main functions in another process'''
    processes = []
    for module_name in module_names:
        m = importlib.import_module(module_name)
        p1 = Process(target=m.main)
        p1.start()
        processes.append(p1)
    return processes
