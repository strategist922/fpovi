"""
Reproduces Table 7. Run
    bash uci-collect-results.sh ${prefix_of_your_logdir}
afterwards.
"""
from experiments.master import runner
import os
import logging
import sys

logging.basicConfig(
        stream=sys.stderr, level=logging.DEBUG,
        format='%(filename)s:%(lineno)s %(levelname)s:%(message)s')

# NOTE change the following paths
source_dir = os.path.abspath('../ffn/')
logdir_fmt = os.path.expanduser('~/exps/fpovi/regr-tbl7-{}-{}')

dat_size_dict = {
    'boston_housing': (506, 13),
    'yacht': (308, 6),
    'concrete': (1030, 8),
    'kin8mn': (8192, 8),
    'energy': (768, 8),
    'power': (9568, 4),
    'winered': (1599, 11),
    'protein_data': (45730, 9),
    'naval': (11934, 16),
}
tasks = []

import datetime
dt = datetime.datetime.now()
timestr = '{}-{}-{}-{}'.format(dt.month, dt.day, dt.hour, dt.minute)

for dat, (n_samples, sz) in dat_size_dict.items():
    root_cmd = 'python bnn_stein_f.py -dataset={} '.format(dat)
    param_specs = {
        'layers': ['10 10'],
        'seed': list(range(1334, 1344)),
        'lr': [4e-3],
        'n_particles': [20],
        ('batch_size', 'n_epoch'): [[100, 500]],
        'ptb_scale': [1],
        'test_freq': [20]
    }
    if n_samples > 1000:
        param_specs[('batch_size', 'n_epoch')] = [[1000, 3000]]

    if dat in set(['protein_data']):
        param_specs['layers'] = ['10 10']
        param_specs['seed'] = [1333, 1334, 1335, 1336, 1337]

    log_dir = logdir_fmt.format(timestr, dat)
    
    tasks += runner.list_tasks(
        root_cmd,
        param_specs,
        source_dir,
        log_dir)

print('\n'.join([t.cmd for t in tasks]))
print(len(tasks))

r = runner.Runner(n_max_gpus=4, n_multiplex=2, n_max_retry=1)
r.run_tasks(tasks)
