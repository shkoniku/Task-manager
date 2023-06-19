import psutil
from datetime import datetime
import argparse
import os


class Process:
    name = None
    cpu_usage = None
    memory_usage = None
    amount_cores = None
    time_create = None
    pid = None
    status = None
    status_nice = None
    amount_threads = None
    username = None

    def __init__(self, cpu, memory, cores, time, pid, status, nice, threads, username, name):
        self.status = status
        self.username = username
        self.time_create = time
        self.cpu_usage = cpu
        self.pid = pid
        self.memory_usage = memory
        self.amount_cores = cores
        self.amount_threads = threads
        self.status_nice = nice
        self.name = name


def get_processes_info(target):
    if target is None:
        processes = []
        for processNow in psutil.process_iter():
            with processNow.oneshot():
                pid = processNow.ppid()
                if pid == 0:
                    continue
                name = processNow.name()
                try:
                    time = datetime.fromtimestamp(processNow.create_time()).strftime('%Y-%m-%d %H:%M:%S')
                except OSError:
                    time = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
                try:
                    cpu_usage = processNow.cpu_percent()
                except psutil.AccessDenied:
                    cpu_usage = 0
                try:
                    amount_cores = len(processNow.cpu_affinity())
                except psutil.AccessDenied:
                    amount_cores = 0
                status = processNow.status()
                try:
                    status_nice = processNow.nice()
                except psutil.AccessDenied:
                    status_nice = 0
                try:
                    memory_usage = round((processNow.memory_full_info().uss >> 20) * processNow.memory_percent(), 2)
                except psutil.AccessDenied:
                    memory_usage = 0
                amount_threads = processNow.num_threads()
                try:
                    username = processNow.username()
                except psutil.AccessDenied:
                    username = "system"
                processes.append(Process(cpu_usage, memory_usage, amount_cores, time, pid, status, status_nice,
                                         amount_threads, username, name))
    else:
        processes = []
        for process in psutil.process_iter():
            with process.oneshot():
                pid = process.ppid()
                if pid == 0:
                    continue
                name = process.name()
                try:
                    time = datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')
                except OSError:
                    time = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
                try:
                    cpu_usage = process.cpu_percent()
                except psutil.AccessDenied:
                    cpu_usage = 0
                try:
                    amount_cores = len(process.cpu_affinity())
                except psutil.AccessDenied:
                    amount_cores = 0
                status = process.status()
                try:
                    status_nice = process.nice()
                except psutil.AccessDenied:
                    status_nice = 0
                try:
                    memory_usage = round((process.memory_full_info().uss >> 20) * process.memory_percent(), 2)
                except psutil.AccessDenied:
                    memory_usage = 0
                amount_threads = process.num_threads()
                try:
                    username = process.username()
                except psutil.AccessDenied:
                    username = "system"
                if target.lower() in name.lower():
                    processes.append(Process(cpu_usage, memory_usage, amount_cores, time, pid, status, status_nice,
                                             amount_threads, username, name))
    return processes


def what_field_is(process, goal):
    if goal == "memory_usage":
        return process.memory_usage
    elif goal == "cores":
        return process.amount_cores
    elif goal == "threads":
        return process.amount_threads
    elif goal == "pid":
        return process.pid
    elif goal == 'name':
        return process.name
    elif goal == 'username':
        return process.username
    elif goal == 'cpu_usage':
        return process.cpu_usage
    elif goal == 'time_create':
        return process.time_create
    elif goal == 'nice':
        return process.status_nice
    elif goal == 'status':
        return process.status


def sort_it(name_processes, goal, order=False):
    if order:
        size = 0
        while size < len(name_processes):
            iterator = size
            while iterator > 0 and what_field_is(name_processes[iterator], goal) < \
                    what_field_is(name_processes[iterator - 1], goal):
                name_processes[iterator], name_processes[iterator - 1] = \
                    name_processes[iterator - 1], name_processes[iterator]
                iterator -= 1
            size += 1
    else:
        size = 0
        while size < len(name_processes):
            iterator = size
            while iterator > 0 and what_field_is(name_processes[iterator], goal) > \
                    what_field_is(name_processes[iterator - 1], goal):
                name_processes[iterator], name_processes[iterator - 1] = \
                    name_processes[iterator - 1], name_processes[iterator]
                iterator -= 1
            size += 1


def length(number):
    number = int(number)
    length_number = 0
    while number > 0:
        length_number += 1
        number //= 10
    return length_number


def show_processes(amount, columns):
    dict_of_matches = {
        'pid': 3,
        'name': 16,
        'username': 4,
        'cpu_usage': 6,
        'cores': 5,
        'memory_usage': 12,
        'status': 6,
        'nice': 4,
        'threads': 7,
        'time_create': 13
    }
    for process in processes:
        if len(process.time_create) > dict_of_matches['time_create']:
            dict_of_matches['time_create'] = len(process.time_create)
        if length(process.pid) > dict_of_matches['pid']:
            dict_of_matches['pid'] = length(process.pid)
        if len(process.name) > dict_of_matches['name']:
            dict_of_matches['name'] = len(process.name)
        if length(process.cpu_usage) + 1 > dict_of_matches['cpu_usage']:
            dict_of_matches['cpu_usage'] = length(process.cpu_usage) + 1
        if length(process.memory_usage) + 3 > dict_of_matches['memory_usage']:
            dict_of_matches['memory_usage'] = length(process.memory_usage) + 3
        if len(process.status) > dict_of_matches['status']:
            dict_of_matches['status'] = len(process.status)
        if length(process.status_nice) > dict_of_matches['nice']:
            dict_of_matches['nice'] = length(process.status_nice)
        if len(process.username) > dict_of_matches['username']:
            dict_of_matches['username'] = len(process.username)
    for col in columns:
        print(col.ljust(dict_of_matches[col]), end=' ')
    print()
    if amount >= 0:
        for iterator in range(amount):
            for col in columns:
                print(str(what_field_is(processes[iterator], col)).ljust(dict_of_matches[col]), end=' ')
            print()
    elif amount == -1:
        for process in processes:
            for col in columns:
                print(str(what_field_is(process, col)).ljust(dict_of_matches[col]), end=' ')
            print()
    else:
        for iterator in range(10):
            for col in columns:
                print(str(what_field_is(processes[iterator], col)).ljust(dict_of_matches[col]), end=' ')
            print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='taskmanager',
                                     description='''%(prog)s will find processes, show information, kill processes.
                                     You can only show info about processes or kill process at once.''')
    parser.add_argument('-c', '--columns', type=str, help='''Columns to show,
     available are name,time_create,cores,pid,memory_usage,username,status,nice,cpu_usage(you need to call program twice
     to see info about cpu_usage),threads.
     (default:pid,name,memory_usage,username,status)''',
                        default='pid,name,memory_usage,username,status')
    parser.add_argument('-n', '--number', type=int, help='Number of rows(processes) to show.'
                                                         ' (Print -1 to show all, default: 10)', default=10)
    parser.add_argument('-s', '-sort-by', dest='sort_by', help='Column to sort by(default: memory_usage)',
                        default='memory_usage')
    parser.add_argument('-k', '--kill', type=str, help='Kill a process with specified name(not a system process)',
                        default=None)
    parser.add_argument('-t', '--target', help='Process with given name to show info about it', type=str,
                        default=None)
    arguments = parser.parse_args()
    if arguments.kill is None:
        processes = get_processes_info(arguments.target)
        sort_it(processes, arguments.sort_by)
    if arguments.kill is not None:
        try:
            os.system(f'taskkill /f /im {arguments.kill}')
        except psutil.NoSuchProcess:
            print('No such process (psutil.NoSuchProcess was raised)')
        except PermissionError:
            print('You dont have permission to kill this process.')

    if arguments.target is not None:
        show_processes(len(processes), arguments.columns.split(','))
    elif arguments.kill is None:
        show_processes(arguments.number, arguments.columns.split(','))
