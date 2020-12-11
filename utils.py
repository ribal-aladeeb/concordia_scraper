import os
import logging
import json
from tqdm import tqdm


CACHE_DIR = 'cache/'
INDEX_FILE = 'inverted_index.txt'


def ensure_dir_exists(dirname):
    if not os.path.isdir(dirname):
        logging.debug(f'Creating {dirname} directory')
        os.makedirs(dirname)


def save_index(index, output_file=INDEX_FILE):

    if CACHE_DIR not in output_file:
        output_file = os.path.join(CACHE_DIR, output_file)

    print(f'Saving index to {output_file}')
    term_sorted_index = sorted(index.items(), key=lambda x: x[0])
    with open(output_file, mode='w') as f:
        for term_posting_pair in tqdm(term_sorted_index):
            print(json.dumps(term_posting_pair), file=f)
    return True


def load_index(input_file=INDEX_FILE):

    if CACHE_DIR not in input_file:
        input_file = os.path.join(CACHE_DIR, input_file)

    print(f'Loading index from {input_file}')
    inverted_index = {}

    with open(input_file, mode='r') as f:
        for line in tqdm(f):
            buffer: list = json.loads(line)
            term = buffer[0]
            inverted_index[term] = buffer[1]

    return inverted_index


if __name__ == '__main__':
    index = load_index()
    print(index['hanna'])
    save_index(index,output_file='copycat.txt')

