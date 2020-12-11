from collections import Counter
import nltk
import os
from tqdm import tqdm
import utils
from utils import CACHE_DIR

TOKENIZING_REGEX = r"[a-zA-Z]+[-']{0,1}[a-zA-Z]*[']{0,1}"  # supports hyphenated and apostrophied words

utils.ensure_dir_exists(CACHE_DIR)


def custom_tokenizer(text: str, tokenizer, stem_doc=False) -> list:
    tokens = tokenizer.tokenize(text)
    stemmer = nltk.stem.PorterStemmer()

    cleaned_tokens = []

    for token in tokens:

        if token == "":
            continue

        while token[-1] == "-" or token[-1] == "'":
            token = token[:-1]

        if 1 < len(token): # don't bother adding single letters to the index because the smallest lastnames should be >= 2 letters
            token = token.lower()
            if stem_doc:
                token = stemmer.stem(token)
            cleaned_tokens.append(token)

    return cleaned_tokens


def load_and_tokenize_documents(documents_folder='documents/',
                                regex=TOKENIZING_REGEX,
                                stem_docs=False) -> dict:
    '''
    Traverses all directories in documents_folder, builds a mapping of docIDs ->
    document tokens. As a side effect, this function will calculate each
    document length and store in under documents/{ID}/length.
    '''

    if CACHE_DIR not in documents_folder:
        documents_folder = os.path.join(CACHE_DIR, documents_folder)

    tokenizer = nltk.RegexpTokenizer(regex)

    docs = {}
    print('Loading documents')
    for docID_dir in tqdm(os.listdir(documents_folder)):
        try:
            docID = int(docID_dir)
        except ValueError as e:
            print(e)
            print(f'{documents_folder} should only contain integer directory names.')
            print(f'Please do not manually write anything into this directory.')
            print(f'It should be entirely managed by the program.')
            continue  # skip this faulty directory name

        document_path = os.path.join(documents_folder, docID_dir)

        with open(os.path.join(document_path, 'text'), mode='r') as f:
            doc_text = f.read()

        docs[docID] = custom_tokenizer(doc_text, tokenizer, stem_doc=stem_docs)

        with open(os.path.join(document_path, 'length'), mode='w')as f:
            f.write(str(len(docs[docID])))

    return docs


def create_index(docs: dict, ) -> dict:
    '''
    Creates the inverted index in the following format:
    {term: [df, [(docID, tf), (docID, tf), ...]]}
    '''

    index = {}
    print('Building the index')

    for docID in tqdm(docs):
        tokens = docs[docID]

        term_frequencies = dict(Counter(tokens))
        for term in term_frequencies:
            postings_dict = index.get(term, {})
            postings_dict[docID] = term_frequencies[term]
            index[term] = postings_dict

    print('Sorting postings by term frequency')
    for term in tqdm(index):
        postings_dict = index[term]
        postings_list = sorted(postings_dict.items(), reverse=True, key=lambda x: x[1])
        doc_frequency = len(postings_list)
        index[term] = [doc_frequency, postings_list]

    return index


def main():

    while True:
        should_stem = input('Do you wish to stem your index? [Y]es/[N]o:').lower()
        possible_values = ['y', 'yes', 'n', 'no']

        if should_stem in possible_values:
            break
        else:
            print('Please enter a correct response.')

    should_stem = True if should_stem in ['y', 'yes'] else False
    docs = load_and_tokenize_documents(stem_docs=should_stem)
    index = create_index(docs)
    utils.save_index(index)
    print(f'Index contains {len(index)} unique terms.')


if __name__ == "__main__":
    main()
