import cProfile
from importlib import import_module
import os
import pstats
import sys

if __name__ == '__main__':
    script_path = os.path.abspath(sys.argv[1])
    project_path = os.path.abspath(__file__ + '/../..')

    print(f'script_path: {script_path}')
    print(f'project_path: {project_path}')

    assert script_path.startswith(project_path)
    module = '.'.join(script_path.split('.')[0][len(project_path) + 1:].split('/'))

    # print(f'package: {package}')
    print(f'module: {module}')

    sys.path.append(project_path)

    mod = import_module(module)

    profiler = cProfile.Profile()
    profiler.enable()

    mod.run()

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.dump_stats('latest.pstats')
    print('dumped')
