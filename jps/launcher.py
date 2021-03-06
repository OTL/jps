from multiprocessing import Process
import getpass
import importlib
import os
import signal
import tempfile


def get_launched_module_pid_file(module_name):
    return '{}/{}_jps_launch.pid'.format(tempfile.gettempdir(), module_name)


def kill_module(module_name):
    pid_file_path = get_launched_module_pid_file(module_name)
    if os.path.exists(pid_file_path):
        with open(pid_file_path, 'r') as f:
            old_pid = int(f.read())
            # try to kill existing process
            try:
                os.kill(old_pid, signal.SIGINT)
            except OSError:
                # do not mind if the process does not exists
                pass
        os.remove(pid_file_path)


def launch_modules(module_names, module_args={}, kill_before_launch=True):
    return launch_modules_with_names([[x, x + getpass.getuser()] for x in module_names],
                                     module_args=module_args, kill_before_launch=kill_before_launch)


def launch_modules_with_names(modules_with_names, module_args={}, kill_before_launch=True):
    '''launch module.main functions in another process'''
    processes = []
    if kill_before_launch:
        for module_name, name in modules_with_names:
            kill_module(name)
    for module_name, name in modules_with_names:
        m = importlib.import_module(module_name)
        args = {}
        if module_name in module_args:
            args = module_args[module_name]
        p1 = Process(target=m.main, args=args)
        p1.daemon = True
        p1.start()
        processes.append(p1)
        with open(get_launched_module_pid_file(name), 'w') as f:
            f.write('{}'.format(p1.pid))
    return processes
