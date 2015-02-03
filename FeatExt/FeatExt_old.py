"""
Extract features from corpus (set of text files) for later readability assessment
"""
__author__ = 'Yorgos'

#Import modules
import os
import codecs
from datetime import datetime
import glob
import re
import configparser
try:
    import nltk
except ImportError:
    print(ImportError)
    exit('Error importing module: NLTK ')



#Helper functions


# Print for debugging purposes only
def debug_print(message):
    """Print for debugging purposes only."""
    print('Debug: {!s}'.format(message)[:240]) # truncate message because damned IDLE can't handle long output!!! (I wasted several hours to figure it out!)
    #write_log(message)


# Initialize log file.
def init_log(log_filename):
    """
    Initialize log file.

    Arguments:  none
    Returns:    nothing
    Globals:    log_filename
    """

    # Limit the size of log file.
    too_big_file = 1000000
    if os.path.isfile(log_filename):
        if os.path.getsize(log_filename) > too_big_file:
            with  codecs.open(log_filename, 'r', "utf-8") as f:
                data = f.read()
                f.close()
            with  codecs.open(log_filename, 'w', "utf-8") as f:
                f.write(data[-too_big_file:])
                f.close()
    with  codecs.open(log_filename, 'a', "utf-8") as f:
        f.write( '\n[' + str(datetime.now()) + '] ---STARTING PROGRAM---\n')
        f.close()


# Print to log file
def write_log(message):
    """
    Write to log file.

    Arguments:  message: log message
    Returns:    nothing
    Globals:    log_filename
    """
    with  codecs.open(log_filename, "a", "utf-8") as f:
        f.write( '[' + str(datetime.now()) + '] ' + str(message) + '\n')
    f.close()
    # Print to standard output too, for debugging purposes. Should be removed when coding is finished
#    debug_print(['LOG', message])
    return

# Write Feature data to output file
def write_results(filename, results, feature_list):
    """
    Write Feature data to output file.

    Arguments:  filename: the name of the output file, with path
                    results:    a list of pairs:results[][0] filename
                                            results[][1] dictionary of feature values
                    grammar_features_list: list of feature names as strings
    One row of features for each file is written to output file as tabbed text.
    """
    # Open output file for writing
    with  codecs.open(filename, "w", "utf-8") as fout:
        # Write header row to output file
        fout.write('filename')
        #debug_print(['results[0][1]', results[0][1]])
        for x in sorted(results[0][1].keys()):
#        for x in grammar_features_list:
            fout.write('\t' + x)
        fout.write('\n')
        #Write feature data, one row for each text
        for i in results:
            fout.write(i[0])
            for feature in sorted(i[1].keys()):
#            for feature in grammar_features_list:
                fout.write('\t' + str(i[1][feature]))
            fout.write('\n')
    fout.close()




#Functions


# Extract tuples of data from file containing tabbed data
def extract_data_from_tabbed_file(file, separator='\t'):
    """
    Extract tuples of data from file containing tabbed data.

    Arguments:  file: string containing the name of the file
                separator: separates the tabbed data in the file
    Returns: A list of tuples
    """

    list_of_tuples = []
    with codecs.open(file, 'rU', 'utf-8') as f:
        for line in f:
            tup = line[:-2].split(separator)
            list_of_tuples.append(tup)
    f.close()
    debug_print(['extract_data_from_tabbed_file', (os.path.basename(file), list_of_tuples)])
    return (os.path.basename(file), list_of_tuples)


# Extract tuples of data from  many files containing tabbed data
def extract_data_from_many_files(files, separator='\t'):
    """
    Extract tuples of data from  many files containing tabbed data.

    Arguments:  files: a list of files
                separator: separates the tabbed data in the file
    Returns: A list of tuples
    """

    data = []
    for file in files:
        data.append(extract_data_from_tabbed_file(file, separator))
    return data


# Get a list of -functional- words
def func_words_list(filename):
    """
    Get a list of -functional- words.

    arguments: a text file with functional words, one per line
    returns:    a list of functional words
    """

    words = [x for line in codecs.open(filename, 'r', 'utf-8') for x in line.split()]
    #debug_print(words)
    return words


# Compute how many of func_words are in data_words
def getFuncT(data_words, func_words):
    """
    Compute how many of func_words are in data_words.

    arguments:  data_words, func_words : lists of words
    returns:    an integer with the number of words found
    """

    return len([x for x in func_words if x in data_words])


# Compute the frequency-of-frequencies distribution of a list (?!?)
def freq_of_freqs(list):
    """
    Compute the frequency-of-frequencies distribution of a list.

    arguments:  list
    Returns:    a frequency-of-frequencies list
    """
    #Create a frequency distribution list
    fdist = nltk.FreqDist(list)
    #debug_print(['fdist', fdist.most_common(100)])
    # Create a frequencies-frequency distribution list
    freqlist = [item[1] for item in fdist.items()] # Create a list of frequencies
    #debug_print(['freqlist', freqlist])
    freqfreq = nltk.FreqDist(freqlist)
    #debug_print(['freqfreq', freqfreq.most_common(100)])
    return freqfreq

# Extract sentences from lem data.
def get_sentences(data):
    """
    Extract sentences from lem data.

    Filter-out tokens that are not considered words (the definition of a word is important!)
    Arguments:  data
    Returns:   a list of lists of triplets of (word, type, pos_tag)
    """
    sents = []
    for item in data:
        if item[1] == '(SENT':
            sent = []
        elif item[1] == ')SENT':
            sents.append(sent)
        elif item[1] in ['TOK', 'ABBR', 'DIG']:
           #Only TOK, ABBR and DIG are considered proper words!
           #TODO: Parameterise word definition in config file
           sent.append((item[2], item[3], item[4]))
    return sents


# # Extract words from lem data.
# def get_words(data):
#     """
#     Extract words from lem data.
#
#     Filter-out tokens that are not considered words (the definition of a word is important!)
#     Arguments:  data
#     Returns:    triplets of (word, type, pos_tag)
#     """
#     debug_print(['words', [(x[2], x[3], x[4]) for x in data if x[1] in ['TOK', 'ABBR', 'DIG']]])
#     #Only TOK, ABBR and DIG are considered proper words! This needs discussion.
#     return [(x[2], x[3], x[4]) for x in data if x[1] in ['TOK', 'ABBR', 'DIG']]



#Functions to extract each feature

def get_N(words):
    """
    Count words.
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


def get_AWL(words):
    """
    Average word length
    Uses get_Char() and get_N()
    """
    return get_Char(words)/get_N(words)


def get_S(sentences):
    """
    Number of Sentences
    """
    return len(sentences)


def get_SL10(sentences):
    """
    Number of Sentences of length greater than 10
    """
    return len([x for x in sentences if len(x) > 10])


def get_SL20(sentences):
    """
    Number of Sentences of length greater than 20
    """
    return len([x for x in sentences if len(x) > 20])


def get_SL30(sentences):
    """
    Number of Sentences of length greater than 30
    """
    return len([x for x in sentences if len(x) > 30])


def get_ASL(lem_data, words):
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


def get_FuncT(words, func_words):
    """
    Compute how many of func_words are in data_words
    arguments:  data_words, func_words : lists of words
    returns:    an integer with the number of words found
    """
    return len([x for x in func_words if x in words])


# Compute the frequencies of word Types
def getFreqT(words, n=10):
    """
    Compute the frequencies of word Types.

    """
    #Get the frequency of frequencies distribution of types
    #debug_print(['list(set', list(set([x[1] for x in words]))])
    f_list = freq_of_freqs([x[1] for x in words])
    #debug_print(['f_list', f_list])
    #Make dictionary from list
    d = dict(f_list)
    #debug_print(['d', d])
    #Find the dictionary's biggest frequency
    max_key = sorted(d.keys(), reverse=True)[0]
    #debug_print(['max_key', max_key])
    #Make dictionary of features from dictionary
    f_dict = dict()
    # for i in range (1, max_key+1):
    #     f_dict['Freq' + str(i)] = d.get(i, 0)
    for i in range (1, n+1):
        f_dict['Freq' + '{:03}'.format(i)] = d.get(i, 0)
    return f_dict


#    Extract features as mentioned in a feature list from data
def extract_features(lem_data, feature_list):
    """
    Extract features as mentioned in a feature list from data.

    Arguments:  lem_data
                grammar_features_list
    Returns:    a dictionary of features
    """

    features = {}
    #extract words, sentences etc. from data
    sentences = get_sentences(lem_data)
    debug_print(['sentences', sentences])
    words = [item for sublist in sentences for item in sublist]
    debug_print(['words', words])
    # words = get_words(lem_data)
    # debug_print(['words', words])

    for feature in feature_list:
        if feature == 'N':
            features[feature] = get_N(words)
        elif feature == 'T':
            features[feature] = get_T(words)
        elif feature == 'Char':
            features[feature] = get_Char(words)
        elif feature == 'AWL':
            features[feature] = get_AWL(words)
        elif feature == 'S':
            features[feature] = get_S(sentences)
        elif feature == 'SL10':
             features[feature] = get_SL10(sentences)
        elif feature == 'SL20':
             features[feature] = get_SL20(sentences)
        elif feature == 'SL30':
            features[feature] = get_SL30(sentences)
        elif feature == 'ASL':
             features[feature] = get_ASL(lem_data, words)
        elif feature == 'LemT':
             features[feature] = get_LemT(words)
        elif feature == 'Noun':
            features[feature] = get_Noun(words)
        elif feature == 'Verb':
            features[feature] = get_Verb(words)
        elif feature == 'Adj':
            features[feature] = get_Adj(words)
        elif feature == 'Adv':
            features[feature] = get_Adv(words)
        elif feature == 'Prn':
            features[feature] = get_Prn(words)
        elif feature == 'PnPe':
            features[feature] = get_PnPe(words)
        elif feature == 'PnPe1':
            features[feature] = get_PnPe1(words)
        elif feature == 'PnPe2':
            features[feature] = get_PnPe2(words)
        elif feature == 'PnRe':
            features[feature] = get_PnRe(words)
        elif feature == 'Cnj':
            features[feature] = get_Cnj(words)
        elif feature == 'Prep':
            features[feature] = get_Prep(words)
        elif feature == 'Pt':
            features[feature] = get_Pt(words)
        elif feature == 'PtSj':
            features[feature] = get_PtSj(words)
        elif feature == 'PVerb':
            features[feature] = get_PVerb(words)
        elif feature == 'Vb1':
            features[feature] = get_Vb1(words)
        elif feature == 'Vb2':
            features[feature] = get_Vb2(words)
        elif feature == 'VbPr':
            features[feature] = get_VbPr(words)
        elif feature == 'VbPa':
            features[feature] = get_VbPa(words)
        elif feature == 'Pp':
            features[feature] = get_Pp(words)
        elif feature == 'PpPv':
            features[feature] = get_PpPv(words)
        elif feature == 'CjCo':
            features[feature] = get_CjCo(words)
        elif feature == 'CjSb':
            features[feature] = get_CjSb(words)
        elif feature == 'NoGe':
            features[feature] = get_NoGe(words)
        elif feature == 'TNoun':
            features[feature] = get_TNoun(words)
        elif feature == 'TVerb':
            features[feature] = get_TVerb(words)
        elif feature == 'TAdj':
            features[feature] = get_TAdj(words)
        elif feature == 'TAdv':
            features[feature] = get_TAdv(words)
        elif feature == 'FuncT':
            features[feature] = get_FuncT(words, func_words)
        elif feature == 'FreqT':
            features.update(getFreqT(words))
        else:
            # Unknown feature
            write_log('Unable to extract feature: "' + feature + '". Unknown feature, skip.')
        """
        if feature == '':
            features[feature] = get_(words)
        """
    return features

###################################################################################

"""
Initialize variables
"""
# Get settings from configuration file and initialize

# Define configuration filename. NOTE: specify full path if different from cwd.
config_file = 'def_config.cfg'


def get_filestems(data_path):
    """
    Build list of file names from contents of directory, removing path and file extension

    @param data_path: the directory where data files reside
    """
    pass



try:
    # Get Settings from configuration file.

    #Define paths for folders: Project, Data, Results.
    config=configparser.ConfigParser(allow_no_value=True)
    config.read_file(codecs.open(config_file, "r", "utf-8"))
    paths = config['PATHS AND FILES']
    # Working path. Alla other paths are relative to this.
    working_path = os.path.abspath( paths.get('working dir', '..'))
    debug_print(['working path', working_path])
    data_path = working_path + '\\' +  paths.get('data dir', 'data')
    results_path = working_path + '\\' + paths.get('results dir', 'results')

    #Define output files
    output_filename = results_path + '\\' +  paths.get('output filename', 'featext.txt')
    log_filename = results_path + '\\' +  paths.get('log filename', 'feature_extract.log')
    debug_print('logfile: {}'.format(log_filename))

    #Define input files
    inputfile_names = get_filestems( data_path )
    lem_datafiles = glob.glob(data_path + '\\*.lem')
    debug_print( lem_datafiles )
    #Define data files
    functional_words_filename = data_path + '\\' +  paths.get('functional words filename', 'functional words.txt')


    # Get Features list from configuration file
    feature_list = config['FEATURES']['grammar_features_list'].split()
    debug_print(['grammar_features_list', feature_list])
    if feature_list == []: raise Exception
except :
    # If unable to read  from the configuration file, use default values.
    print('Error reading from configuration file: {0} . Will use default configuration instead.'.format(config_file))
    #Define paths for folders: Project, Data, Results
    working_path = os.path.abspath('..')
    data_path = working_path + '\\' + 'data'
    results_path = working_path + '\\' + 'results'
    #Define output files
    output_filename = results_path + '\\' + 'featext.txt'
    log_filename = results_path + '\\' + 'feature_extract.log'
    #Define input & data files
    lem_datafiles = glob.glob(data_path + '\\*.lem')
    debug_print( lem_datafiles )
    functional_words_filename = data_path + '\\' + 'functional words.txt'

    feature_list = [
        'N',
        'T',
        'Char',
        'awl',
        'S',
        'SL10',
        'SL20',
        'SL30',
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

debug_print(feature_list)
# Write initial information to the log file
init_log(log_filename)
# get the list of functional words from file
func_words = func_words_list(functional_words_filename)
# Define how many type frequencies are significant
#TODO: parameterize this
type_freqs_num = 10
#Extract features from all lem files
results = []
for file in lem_datafiles:
    write_log('Extracting features from file ' + file)
    file_data = extract_data_from_tabbed_file(file)
    debug_print(['file_data', file_data])
    debug_print(['sentences', get_sentences(file_data[1])])
    results.append((
        file_data[0], #filename
        extract_features(file_data[1],feature_list)))

debug_print(['results', results])
#Write to output file
write_log('Writing results to file ' + output_filename + '  ...')
write_results(output_filename, results, feature_list)
write_log('  ... done')
write_log('---END PROGRAM---')

