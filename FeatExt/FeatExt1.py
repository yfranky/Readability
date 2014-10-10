"""
Extract features from corpus (set of text files) for later readability assessment
"""
__author__ = 'Yorgos'

#Import modules
import os
import codecs
import glob
import re
import nltk
#from numpy import genfromtxt

#Helper functions

def debug_print(message):
    #prints for debugging purposes only
    print("Debug:", message)


def write_log(message):
    """
    Write to log file
    Arguments:  message: log message
    Returns:    nothing
    Globals:    log_filename
    """
    with  codecs.open(log_filename, "a", "utf-8") as f:
        f.write(message + '\n')
    f.close()
    return


def write_results(filename, results, feature_list):
    """
    Write Feature data to output file
    Arguments:  filename: the name of the output file, with path
                    results:    a list of pairs:results[][0] filename
                                            results[][1] dictionary of feature values
                    feature_list: list of feature names as strings
    One row of features for each file is written to output file as tabbed text.
    """
    # Open output file for writing
    with  codecs.open(filename, "w", "utf-8") as fout:
        # Write header row to output file
        fout.write('filename')
        debug_print(['results[0][1]', results[0][1]])
        for x in sorted(results[0][1].keys()):
#        for x in feature_list:
            fout.write('\t' + x)
        fout.write('\n')
        #Write feature data, one row for each text
        for i in results:
            fout.write(i[0])
            for feature in sorted(i[1].keys()):
#            for feature in feature_list:
                fout.write('\t' + str(i[1][feature]))
            fout.write('\n')
    fout.close()




#Functions

def extract_data_from_tabbed_file(file, separator='\t'):
    """
    Extract tuples of data from file containing tabbed data
    Arguments:  file: string containing the name of the file
                separator: separates the tabbed data in the file
    Returns: A list of tuples
    """
#    data = []
    list_of_tuples = []
    with codecs.open(file, 'r', 'utf-8') as f:
        for line in f:
            tuple = line.split(separator)
            list_of_tuples.append(tuple)
    f.close()
#    data.append((os.path.basename(file), list_of_tuples))
    debug_print(['extract_data_from_tabbed_file', (os.path.basename(file), list_of_tuples)])
    return (os.path.basename(file), list_of_tuples)


def extract_data_from_many_files(files, separator='\t'):
    """
    Extract tuples of data from  many files containing tabbed data
    Arguments:  files: a list of files
                separator: separates the tabbed data in the file
    Returns: A list of tuples
    """
    data = []
    for file in files:
        data.append(extract_data_from_tabbed_file(file, separator))
    return data


def func_words_list(filename):
    """
    arguments: a text file with functional words, one per line
    returns:    a list of functional words
    """
    words = [x for line in codecs.open(filename, 'r', 'utf-8') for x in line.split()]
    debug_print(words)
    return words


def getFuncT(data_words, func_words):
    """
    Compute how many of func_words are in data_words
    arguments:  data_words, func_words : lists of words
    returns:    an integer with the number of words found
    """
    return len([x for x in func_words if x in data_words])


def freq_of_freqs(list):
    """
    Compute the frequency-of-frequencies distribution of a list (?!?)
    arguments:  list
    Returns:    a frequency-of-frequencies list
    """
    #Create a frequency distribution list
    fdist = nltk.FreqDist(list)
    debug_print('#########')
    debug_print(['fdist', fdist.most_common(100)])
    # Create a frequencies-frequency distribution list
    freqlist = [item[1] for item in fdist.items()] # Create a list of frequencies
    debug_print(['freqlist', freqlist])
    freqfreq = nltk.FreqDist(freqlist)
    debug_print(['freqfreq', freqfreq.most_common(100)])
    return freqfreq


def get_words(data):
    """
    Get words from data.
    Filter-out tokens that are not considered words (the definition of a word is important!)
    Arguments:  data
    Returns:    triplets of (word, type, pos_tag)
    """
    #Only TOK, ABBR and DIG are considered proper words!
    return [(x[2], x[3], x[4]) for x in data if x[1] in ['TOK', 'ABBR', 'DIG']]


#Functions to extract each feature

def get_N(words):
    """
    Count words
    """
    return len(words)


def get_T(words):
    """
    count types
    """
    return len(set([x[0].lower() for x in words]))


def get_Char(words):
    """
    count text characters, excluding whitespace and punctuation
    """
    return sum(len(s[0]) for s in words)


def get_awl(words):
    """
    Average word length
    Uses get_Char() and get_N()
    """
    return get_Char(words)/get_N(words)


def get_S(lem_data):
    """
    Number of Sentences
    """
    return len([x for x in lem_data if x[1]=='(SENT'])


def get_SL10():
    """
    Number of Sentences of length 10
    """
    pass


def get_SL20():
    """
    Number of Sentences of length 20
    """
    pass


def get_SL30():
    """
    Number of Sentences of length 30
    """
    pass


def get_asl(lem_data, words):
    """
    Average sentence length in words
    Uses get_N and get_S
    """
    return(get_N(words) / get_S(lem_data))


def get_LemT(words):
    """
    Number of different lemmas
    """
    return len(set([x[1] for x in words]))


def get_Noun(words):
    """
    Count Nouns
    """
    return len([x[1] for x in words if re.match('No', x[2])])


def get_Verb(words):
    """
    Count Verbs
    """
    return len([x[1] for x in words if re.match('Vb', x[2])])


def get_Adj(words):
    """
    Count Adjectivs
    """
    return len([x[1] for x in words if re.match('Aj', x[2])])


def get_Adv(words):
    """
    Count Adverbs
    """
    return len([x[1] for x in words if re.match('Ad', x[2])])


def get_Prn(words):
    """
    Count Pronouns
    """
    return len([x[1] for x in words if re.match('Pn', x[2])])


def get_PnPe(words):
    """
    Count Personal Pronouns
    """
    return len([x[1] for x in words if re.match('PnPe', x[2])])


def get_PnPe1(words):
    """
    Count Personal Pronouns in 1st person
    """
    return len([x[1] for x in words if re.match('PnPe..01', x[2])])


def get_PnPe2(words):
    """
    Count Personal Pronouns in 2st person
    """
    return len([x[1] for x in words if re.match('PnPe..02', x[2])])


def get_PnRe(words):
    """
    Count PnRe pronouns
    """
    return len([x[1] for x in words if re.match('PnRe', x[2])])


def get_Cnj(words):
    """
    Count Conjunctions
    """
    return len([x[1] for x in words if re.match('Cj', x[2])])

def get_Prep(words):
    """
    Count Prepositions
    """
    return len([x[1] for x in words if re.match('AsPp', x[2])])


def get_Pt(words):
    """
    Count Pt
    """
    return len([x[1] for x in words if re.match('Pt', x[2])])


def get_PtSj(words):
    """
    Count PtSj
    """
    return len([x[1] for x in words if re.match('PtSj', x[2])])


def get_PVerb(words):
    """
    Count PVerb
    """
    return len([x[1] for x in words if re.match('Vb(..){7}Pv', x[2])])


def get_Vb1(words):
    """
    Count Verbs in 1st person
    """
    return len([x[1] for x in words if re.match('Vb(..){3}01', x[2])])


def get_Vb2(words):
    """
    Count Verbs in 2nd person
    """
    return len([x[1] for x in words if re.match('Vb(..){3}02', x[2])])


def get_VbPr(words):
    """
    Count Verbs in Present tense
    """
    return len([x[1] for x in words if re.match('Vb(..){2}Pr', x[2])])


def get_VbPa(words):
    """
    Count Verbs in Past tense
    """
    return len([x[1] for x in words if re.match('Vb(..){2}Pa', x[2])])


def get_Pp(words):
    """
    Count participles
    """
    return len([x[1] for x in words if re.match('VbMnPp', x[2])])


def get_PpPv(words):
    """
    Count PpPv
    """
    return len([x[1] for x in words if re.match('VbMnPp(..){5}Pv', x[2])])


def get_CjCo(words):
    """
    Count CjCo
    """
    return len([x[1] for x in words if re.match('CjCo', x[2])])


def get_CjSb(words):
    """
    Count CjSb
    """
    return len([x[1] for x in words if re.match('CjSb', x[2])])


def get_NoGe(words):
    """
    Count Nouns in Genitive
    """
    return len([x[1] for x in words if re.match('No.*Ge', x[2])])


def get_TNoun(words):
    """
    Count noun types
    """
    debug_print(['TNoun', set([x[1] for x in words if re.match('No', x[2])])])
    return len(set([x[1] for x in words if re.match('No', x[2])]))


def get_TVerb(words):
    """
    Count Verb types
    """
    return len([x[1] for x in words if re.match('Vb', x[2])])


def get_TAdj(words):
    """
    Count Adjective types
    """
    return len([x[1] for x in words if re.match('Aj', x[2])])


def get_TAdv(words):
    """
    Count Adverbs
    """
    return len([x[1] for x in words if re.match('Ad', x[2])])


def getFuncT(words, func_words):
    """
    Compute how many of func_words are in data_words
    arguments:  data_words, func_words : lists of words
    returns:    an integer with the number of words found
    """
    return len([x for x in func_words if x in words])


def getFreqT(words, n=10):
    """
    Compute the frequencies of types
    """
    #Get the frequency of frequencies distribution of types
    debug_print(['list(set', list(set([x[1] for x in words]))])
    f_list = freq_of_freqs([x[1] for x in words])
    debug_print(['f_list', f_list])
    #Make dictionary from list
    d = dict(f_list)
    debug_print(['d', d])
    #Find the dictionary's biggest frequency
    max_key = sorted(d.keys(), reverse=True)[0]
    debug_print(['max_key', max_key])
    #Make dictionary of features from dictionary
    f_dict = dict()
    # for i in range (1, max_key+1):
    #     f_dict['Freq' + str(i)] = d.get(i, 0)
    for i in range (1, n+1):
        f_dict['Freq' + '{:03}'.format(i)] = d.get(i, 0)
    return f_dict


def extract_features(lem_data, feature_list):
    """
    Extract the features mentioned in a feature list from data
    Arguments:  lem_data
                feature_list
    Returns:    a dictionary of features
    """
    features = {}
    #extract word etc. from data
    words = get_words(lem_data)
    debug_print(['words', words])

    for feature in feature_list:
        if feature == 'N':
            features[feature] = get_N(words)
        if feature == 'T':
            features[feature] = get_T(words)
        if feature == 'Char':
            features[feature] = get_Char(words)
        if feature == 'awl':
            features[feature] = get_awl(words)
        if feature == 'S':
            features[feature] = get_S(lem_data)
        if feature == 'SL10':
             features[feature] = get_SL10(words)
        if feature == 'SL20':
             features[feature] = get_SL20(words)
        if feature == 'SL30':
            features[feature] = get_SL30(words)
        if feature == 'asl':
             features[feature] = get_asl(lem_data, words)
        if feature == 'LemT':
             features[feature] = get_LemT(words)
        if feature == 'Noun':
            features[feature] = get_Noun(words)
        if feature == 'Verb':
            features[feature] = get_Verb(words)
        if feature == 'Adj':
            features[feature] = get_Adj(words)
        if feature == 'Adv':
            features[feature] = get_Adv(words)
        if feature == 'Prn':
            features[feature] = get_Prn(words)
        if feature == 'PnPe':
            features[feature] = get_PnPe(words)
        if feature == 'PnPe1':
            features[feature] = get_PnPe1(words)
        if feature == 'PnPe2':
            features[feature] = get_PnPe2(words)
        if feature == 'PnRe':
            features[feature] = get_PnRe(words)
        if feature == 'Cnj':
            features[feature] = get_Cnj(words)
        if feature == 'Prep':
            features[feature] = get_Prep(words)
        if feature == 'Pt':
            features[feature] = get_Pt(words)
        if feature == 'PtSj':
            features[feature] = get_PtSj(words)
        if feature == 'PVerb':
            features[feature] = get_PVerb(words)
        if feature == 'Vb1':
            features[feature] = get_Vb1(words)
        if feature == 'Vb2':
            features[feature] = get_Vb2(words)
        if feature == 'VbPr':
            features[feature] = get_VbPr(words)
        if feature == 'VbPa':
            features[feature] = get_VbPa(words)
        if feature == 'Pp':
            features[feature] = get_Pp(words)
        if feature == 'PpPv':
            features[feature] = get_PpPv(words)
        if feature == 'CjCo':
            features[feature] = get_CjCo(words)
        if feature == 'CjSb':
            features[feature] = get_CjSb(words)
        if feature == 'NoGe':
            features[feature] = get_NoGe(words)
        if feature == 'TNoun':
            features[feature] = get_TNoun(words)
        if feature == 'TVerb':
            features[feature] = get_TVerb(words)
        if feature == 'TAdj':
            features[feature] = get_TAdj(words)
        if feature == 'TAdv':
            features[feature] = get_TAdv(words)
        if feature == 'FuncT':
            features[feature] = getFuncT(words, func_words)
        if feature == 'FreqT':
            features.update(getFreqT(words))
        """
        if feature == '':
            features[feature] = get_(words)
        """
    return features


"""
Initialize variables
"""
#Define paths for folders: Project, Data, Results
module_path = os.getcwd()
projectPath = module_path + '\\..'
dataPath = projectPath + '\\data'
resultsPath = projectPath + '\\results'
#Define input & data files
lem_datafiles = glob.glob(dataPath + '\\*.lem')
debug_print( lem_datafiles )
txt_datafiles = glob.glob(dataPath + '\\*.txt')
debug_print( txt_datafiles )
functional_words_filename = module_path + '\\' + 'functional words.txt'
#Define output files
output_filename = resultsPath + '\\' + 'featext1.txt'
log_filename = 'feature_extract.log'
feature_list = [
    'N',
    'T',
    'Char',
    'awl',
    'S',
    # 'SL10',
    # 'SL20',
    # 'SL30',
    'asl',
    'LemT',
    'Noun',
    'Verb',
    'Adj',
    'Adv',
    'Prn',
    'PnPe',
    'PnPe1',
    'PnPe2',
    'PnRe',
    'Cnj',
    'Prep',
    'Pt',
    'PtSj',
    'PVerb',
    'Vb1',
    'Vb2',
    'VbPr',
    'VbPa',
    'Pp',
    'PpPv',
    'CjCo',
    'CjSb',
    'NoGe',
    'TNoun',
    'TVerb',
    'TAdj',
    'TAdv',
    'FuncT',
    'FreqT'
]



# read a list of functional words from file
func_words = func_words_list(functional_words_filename)
# Define how many type frequencies are significant
#TODO: parameterize this
type_freqs_num = 10
#Extract features from all lem files
results = []
for file in lem_datafiles:
    file_data = extract_data_from_tabbed_file(file)
    debug_print(['file_data', file_data])
    results.append((
        file_data[0],
        extract_features(file_data[1],feature_list)))

debug_print(['results', results])
#Write to output file
write_results(output_filename, results, feature_list)


