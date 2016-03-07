from multiprocessing import Process


def launch_modules(module_names):
    '''launch module.main functions in another process'''
    processes = []
    for module_name in module_names:
        m = __import__(module_name)
        p1 = Process(target=m.main)
        p1.start()
        processes.append(p1)
    return processes
