import os
import logging
import json
from tqdm import tqdm


CACHE_DIR='cache/'


def ensure_dir_exists(dirname):
    if not os.path.isdir(dirname):
        logging.debug(f'Creating {dirname} directory')
        os.makedirs(dirname)


def save_index(index, output_file='inverted_index.txt'):

    if CACHE_DIR not in output_file:
        output_file = os.path.join(CACHE_DIR, output_file)

    print(f'Saving index to {output_file}')
    term_sorted_index = sorted(index.items(), key=lambda x: x[0])
    with open(output_file, mode='w') as f:
        for term_posting_pair in tqdm(term_sorted_index):
            print(json.dumps(term_posting_pair), file=f)
    return True
