import os
import math
import nltk
import indexer
import utils
from utils import CACHE_DIR, INDEX_FILE


QUERY_TYPES = ['TF-IDF', 'BM25']


def main():
    # Get index fle
    idx_desired = input('Which index file do you wish to query (press enter for default inverted_index.txt): ')

    if idx_desired == '':
        idx_desired = os.path.join(CACHE_DIR, INDEX_FILE)
    else:
        idx_desired = os.path.join(CACHE_DIR, idx_desired)

    index_filename = idx_desired.lower()

    # determine if query should be stemmed
    while True:
        should_stem = input('Is this a stemmed index? [Y]es/[N]o: ').lower()
        possible_values = ['y', 'yes', 'n', 'no']

        if should_stem in possible_values:
            break
        else:
            print('Please enter a correct response.')

    query_prompt = "Specify which type of query you are making [1] TF-IDF [2] BM25: "
    # for i, qtype in enumerate(QUERY_TYPES):
    #     query_prompt += f'[{i+1}] {qtype}\n'

    # determine how the documents should be ranked
    while True:
        try:
            desired_query_type = int(input(query_prompt)) - 1
            break
        except ValueError as e:
            print(e)
            print(f'Please enter and integer between 1-{len(QUERY_TYPES)}.')

    # format the query appropriately
    original_query = input('Please enter your query (keep in mind that casing is irrelevant): ')
    tokenizer = nltk.RegexpTokenizer(indexer.TOKENIZING_REGEX)
    query_tokens = indexer.custom_tokenizer(original_query, tokenizer, stem_doc=should_stem)
    index = utils.load_index(input_file=index_filename)
    print(f'\nYour formatted query is: {" ".join(query_tokens)}')

    # rank documents
    ranked_docs: dict = rank_documents(query_tokens, index, QUERY_TYPES[desired_query_type])

    top15 = sorted(ranked_docs.items(), reverse=True, key=lambda x: x[1])[:15]
    i = 1
    URLs = []
    print()
    for docID, rank in top15:
        print(f'{i}.\tDoc {docID}\twith rank {round(rank,3)}')
        with open(os.path.join(CACHE_DIR, 'documents', str(docID), 'url'), mode='r') as f:
            URLs.append(f.read())
        i -= -1
    print('\nView those documents in the browser by clicking on their corresponding URLs:\n')
    for i, url in enumerate(URLs):
        print(f'{i+1}.\t{url}')


def collect_all_doc_lengths() -> dict:
    '''
    Traverses the CACHE_DIR/documents/{ID}/length for all {ID} directories and
    creates a mapping of docID -> doc length. To be used for computation of
    average length, total collection size, and rankings.
    '''

    lengths = {}
    doc_dir = os.path.join(CACHE_DIR, 'documents/')
    document_paths = os.listdir(doc_dir)
    for ID_dir in document_paths:
        try:
            with open(os.path.join(doc_dir, ID_dir, 'length'), mode='r') as f:
                doc_length = int(f.read())
                lengths[int(ID_dir)] = doc_length
        except Exception as e:
            print(e)
            print(f'The problematic directory is {ID_dir}. It will be skipped.')

    return lengths


def avg_doc_length_and_collection_size(lengths: dict) -> float:
    '''
    Computes average doc length and total number of documents.
    '''

    len_list = lengths.values()
    total_lengths = sum(len_list)
    doc_count = len(len_list)
    avg = total_lengths/doc_count

    return avg, doc_count


def union_postings(terms, index):
    '''
    Returns a union of all the documents that contain at least one query term.
    '''

    accumulator = set()
    for t in terms:
        postings_list = index.get(t, [])
        if len(postings_list)==0:
            continue
        for pair in postings_list[1]:  # slice because the first element is df
            docID, _ = pair             # pair = (docID, tf)
            accumulator.add(docID)

    return accumulator


def rank_documents(query_tokens, index, rank_type) -> list:
    '''
    Rank documents and return them as a docID -> rank mapping
    '''

    eligible_docs = union_postings(query_tokens, index)
    print(f'Ranking {len(eligible_docs)} eligible documents.')
    doc_rank_map = {}
    length_mapping: dict = collect_all_doc_lengths()
    L_avg, N = avg_doc_length_and_collection_size(length_mapping)

    for docID in eligible_docs:
        L_d = length_mapping[docID]

        if rank_type == QUERY_TYPES[0]:
            doc_rank_map[docID] = TF_IDF(query_tokens, docID, N, index)

        elif rank_type == QUERY_TYPES[1]:
            doc_rank_map[docID] = BM25(query_tokens, docID, L_d, L_avg, N, index)

        else:
            print("Should never reach this")

    return doc_rank_map


def BM25(terms, docID, L_d, L_avg, N, index, k=100, b=0.9) -> float:
    '''
    Computes the BM25 ranking value of a term-document pair. To see the math and
    motivation behind it please refer to Stanford's NLP Information Retrieval
    textbook: https://nlp.stanford.edu/IR-book/pdf/11prob.pdf (go to 11.32).
    '''

    RSV = 0
    for term in terms:
        postings_list = index[term][1]
        df = index[term][0]
        tf = 0

        for pair in postings_list:
            if docID == pair[0]:
                tf = pair[1]
                break

        RSV += math.log10(N/df) * (k+1)*tf / (k*((1-b) + b*L_d/L_avg) + tf)

    return RSV


def TF_IDF(terms, docID, N, index) -> float:
    '''
    Compute the tf-idf ranking of a document and a query. Link to the
    corresponding chapter in the Stanford textbook:
    https://nlp.stanford.edu/IR-book/pdf/06vect.pdf.
    '''

    tf_idf = 0
    for term in terms:
        postings_list = index[term][1]
        df = index[term][0]
        tf = 0

        for pair in postings_list:
            if docID == pair[0]:
                tf = pair[1]
                break

        tf_idf += tf * math.log10(N/df)

    return tf_idf


if __name__ == '__main__':
    main()
