"""
Extract features from corpus (set of text files) for later readability assessment
"""

__author__ = 'Yorgos'

#Import modules
import os, sys

#import getopt
import argparse
import math
import numpy
import codecs
from datetime import datetime
import statistics
from math import log2
import sympy
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
    return
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
    global log_filename
    return
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
                    results:    a list of triples:
                                            results[][0] text id
                                            results[][1] filename
                                            results[][1] dictionary of feature values
                    grammar_features_list: list of feature names as strings
    One row of features for each file is written to output file as tabbed text.
    """
    # Open output file for writing
    with  codecs.open(filename, "w", "utf-8") as fout:
        # Write header row to output file
        fout.write('text_id\tfilename')
        #debug_print(['results[0][1]', results[0][1]])
        for x in sorted(results[0][2].keys()):
#        for x in grammar_features_list:
            fout.write('\t' + x)
        fout.write('\n')
        #Write feature data, one row for each text
        for i in results:
            # i[0]: text id, i[1]: filename
            fout.write( '{0}\t{1}'.format(str(i[0]), str(i[1])) )
            for feature in sorted(i[2].keys()):
#            for feature in grammar_features_list:
                fout.write('\t' + str(i[2][feature]))
            fout.write('\n')
    fout.close()


def get_basenames(path, file_extension):
    """
    Build list of file basenames (without the name extension) from contents of directory, collecting all files of a
    certain type.

    @rtype : list of file basenames
    @param data_path: the directory where files reside
    @param file_extension: type of files to collect file names
    """
    files = glob.glob(path + '\\*.' + file_extension)
    stems = [ os.path.splitext( os.path.split(file)[1] )[0] for file in files]
    debug_print('Stems: {0}'.format(str(stems)))
    return stems



#Functions


# Extract tuples of data from file containing tabbed data
def extract_data_from_tabbed_file(file, separator='\t'):
    """
    Extract lists of data from file containing tabbed data.

    Arguments:  file: string containing the name of the file
                separator: separates the tabbed data in the file
    @rtype : A list of lists of strings
    """

    list_of_lists = []
    with codecs.open(file, 'rU', 'utf-8') as f:
        for line in f:
            # Skip empty lines
            if len(line) < 3 : continue # too small line, considered empty
            #if line == '\r\n': continue #empty line contains only a CR and a LF. ATTN:this is an empirical observation!
                                         #problem: '\r\n' seems to be system or editor dependent.
            line_data = line[:-1].split(separator)
            #debug_print(line)
            #debug_print(line_data)
            list_of_lists.append(line_data)
    f.close()
    debug_print(['extract_data_from_tabbed_file', (os.path.basename(file), list_of_lists)])
    return (os.path.basename(file), list_of_lists)


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
def getFuncT(types, func_words):
    """
    Compute how many of func_words are in types.

    arguments:  data_words, func_words : lists of words
    returns:    an integer with the number of words found
    """

    return len([x for x in func_words if x in types])


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


def get_sentences(data):
    """
    Extract sentences from chunk data.

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
           # Convert to lowercase to get word type and add it as last in the tuple
           type = item[2].lower()
           sent.append((item[2], item[3], item[4], type ))
    return sents


def get_All_tokens(data):
    """
    Extract all tokens from lem data.
    Only filter-out tokens that indicate sentence start and end points.

    Arguments:  data
    Returns:    triplets of (word, type, pos_tag)
    """

    #Only TOK, ABBR and DIG are considered proper words! This needs discussion.
    tokens = [x for x in data if x[1] not in ['(SENT', ')SENT', 'SYN']]
    debug_print('All tokens: {0}'.format(tokens))
    return len(tokens)



#Functions to extract each feature

def get_N(words):
    """
    Count words.
    """
    return len(words)


def get_T(types):
    """
    count types
    """
    return len(set(types))


def get_Char(words):
    """
    count text characters, excluding whitespace and punctuation
    """
    return sum(len(s[0]) for s in words)


# def get_AWL(words):
#     """
#     Average word length
#     Uses get_Char() and get_N()
#     """
#     return get_Char(words)/get_N(words)


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


def get_m_ASL(words, sentences):
    """
    Average sentence length in words
    """
    return(get_N(words) / get_S(sentences))


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


def get_NoPr(words):
    """
    Count Proper Nouns
    """
    return len([x[1] for x in words if re.match('NoPr', x[2])])


def get_Dig(words):
    """
    Count Numbers (with digits, e.g.: 2015)
    """
    return len([x[1] for x in words if re.match('DIG', x[2])])


def get_RgFw(words):
    """
    Count Foreign language Words
    """
    return len([x[1] for x in words if re.match('RgFw', x[2])])


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

def get_PnRi(words):
    """
    Count PnRi pronouns
    """
    return len([x[1] for x in words if re.match('PnRi', x[2])])


def get_PnIr(words):
    """
    Count PnIr pronouns
    """
    return len([x[1] for x in words if re.match('PnIr', x[2])])


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
    #debug_print(['TNoun', set([x[1] for x in words if re.match('No', x[2])])])
    return len(set([x[3] for x in words if re.match('No', x[2])]))


def get_TVerb(words):
    """
    Count Verb types
    """
    return len(set([x[3] for x in words if re.match('Vb', x[2])]))


def get_TAdj(words):
    """
    Count Adjective types
    """
    return len(set([x[1] for x in words if re.match('Aj', x[2])]))


def get_TAdv(words):
    """
    Count Adverbs
    """
    return len(set([x[1] for x in words if re.match('Ad', x[2])]))


def get_FuncT(types, func_words):
    """
    Compute how many of func_words are in data_words
    arguments:  data_words, func_words : lists of words
    returns:    an integer with the number of words found
    """
    return len([x for x in func_words if x in types])


# Compute the frequencies of word Types
def getFreqT(types, n=10):
    """
    Compute the frequencies of word Types.

    """
    #Get the frequency of frequencies distribution of types
    #debug_print(['list(set', list(set([x[1] for x in words]))])
    f_list = freq_of_freqs(types)
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


def get_YuleK(types):
    """

    @param types:
    @return:
    """

    #Get the frequency of frequencies distribution of types
    f_list = freq_of_freqs(types) #[x[1] for x in words])
    # debug_print(['f_list', f_list])
    s = 0
    for item in f_list.keys():
        s += f_list[item]*item*item

    return 10000 * (s - len(types)) / float(len(types)*len(types))


def get_D(words, types):
    """
    Measure D lexical diversity
    reference: Duran, Malvern, Richards, Chipere:
            Developmental Trends in Lexical Diversity Oxford UP 2004, p224
    uses sympy

    @param words:
    @param types:
    """
    n = get_N(words)
    t = get_T(types)
    ttr = t/n
    # Solve the equation as in reference
    d = sympy.symbols('d')
    answer = sympy.solve(d/n*(sympy.sqrt(1+2*n/d)-1)-ttr, d)

    return answer[0] if answer else ''




def get_Entr(types):
    """

    @param types:
    """
    # Create a frequency distribution of types
    fdist = nltk.FreqDist(types)
    freqlist = [item[1] for item in fdist.items()] # Create a list of frequencies

    entr = 0
    for item in freqlist:
        prob = item / len(types) # calculate the probability for each type
        log_prob = log2(prob) # calculates the log-2 of probability for each type
        entr -= prob*log_prob # accumulate entropy of each type to find the entropy of the whole text

    return entr

def get_RelEntr(types):
    """

    @param types:
    @return:
    """

    max_entr = -log2(1 / len(types))

    return get_Entr(types) / max_entr


def get_grammar_features(data, feature_list):
    """
    Extract grammar features as mentioned in a feature list from data.

    Arguments:  data
                grammar_features_list
    Returns:    a dictionary of features
    """

    features = {}
    #extract words, sentences etc. from data
    sentences = get_sentences(data)
    debug_print(['sentences', sentences])
    words = [item for sublist in sentences for item in sublist]
    debug_print(['words', words])
    # build a list of types to avoid repetitive building later
    types = [x[3] for x in words]
    debug_print(['types', types])

    # get the list of functional words from file
    func_words = func_words_list(functional_words_filename)
    # Define how many type frequencies are significant
    #TODO: parameterize this
    type_freqs_num = 30

    # Compute commonly used features
    # count words
    N = float(get_N(words)) #cast to float because it will be used later in floating point calculations
    # count types
    T = float(get_T(types))
    # count sentences
    S = float(get_S(sentences))
    # count verbs
    V = float(get_Verb(words))


    # with numpy.errstate(divide='ignore'):
    for feature in feature_list:
        try:
            if feature == 'All_tokens':
                features[feature] = get_All_tokens(data)
            elif feature == 'N':
                features[feature] = N
            elif feature == 'T':
                features[feature] = T
            elif feature == 'm_TTR':
                features[feature] = T / N
            elif feature == 'FreqT':
                freqt = getFreqT(types, type_freqs_num)
                features.update(freqt)
            elif feature == 'm_FreqTpc':
                # Compute freqt only if it is not already computed, avoiding redundant computations
                try:
                    freqt
                except NameError:
                    freqt = getFreqT(types, type_freqs_num)
                # Dictionary comprehension
                freqtpc = {'m_'+key+'pc': freqt[key]/N for key in freqt.keys()}
                features.update(freqtpc)
            elif feature == 'm_DisToHapax':
                # Compute hapax and dis only if it is not already computed, avoiding redundant computations
                try:
                    freqt
                except NameError:
                    myfreqt = getFreqT(types, 2)
                else:
                    myfreqt = freqt
                features[feature] = myfreqt['Freq002'] / myfreqt['Freq001']


            elif feature == 'Char':
                features[feature] = get_Char(words)
            elif feature == 'm_AWL':
                features[feature] = get_Char(words) / N
            elif feature == 'S':
                features[feature] = S
            elif feature == 'SL10':
                 features[feature] = get_SL10(sentences)
            elif feature == 'm_SL10toS':
                 features[feature] = (features['SL10'] if 'SL10' in features else get_SL10(sentences))/ S
            elif feature == 'SL20':
                 features[feature] = get_SL20(sentences)
            elif feature == 'm_SL20toS':
                 features[feature] = (features['SL20'] if 'SL20' in features else get_SL20(sentences))/ S
            elif feature == 'SL30':
                features[feature] = get_SL30(sentences)
            elif feature == 'm_SL30toS':
                 features[feature] = (features['SL30'] if 'SL30' in features else get_SL30(sentences))/ S
            elif feature == 'm_ASL':
                 features[feature] = get_m_ASL(words, sentences)
            elif feature == 'LemT':
                 features[feature] = get_LemT(words)
            elif feature == 'm_TTRLem':
                 features[feature] = (features['LemT'] if 'LemT' in features else get_LemT(words))/ N
            elif feature == 'Noun':
                features[feature] = get_Noun(words)
            elif feature == 'm_NounToN':
                 features[feature] = (features['Noun'] if 'Noun' in features else get_Noun(words))/ N
            elif feature == 'NoPr':
                features[feature] = get_NoPr(words)
            elif feature == 'm_NoPrToN':
                 features[feature] = (features['NoPr'] if 'NoPr' in features else get_NoPr(words))/ N
            elif feature == 'Dig':
                features[feature] = get_Dig(words)
            elif feature == 'm_DigToN':
                 features[feature] = (features['Dig'] if 'Dig' in features else get_Dig(words))/ N
            elif feature == 'RgFw':
                features[feature] = get_RgFw(words)
            elif feature == 'm_RgFwToN':
                 features[feature] = (features['RgFw'] if 'RgFw' in features else get_RgFw(words))/ N
            elif feature == 'Verb':
                features[feature] = V
            elif feature == 'm_VerbToN':
                features[feature] = (features['Verb'] if 'Verb' in features else get_Verb(words))/ N
            elif feature == 'm_VerbToS':
                features[feature] = (features['Verb'] if 'Verb' in features else get_Verb(words))/ S
            elif feature == 'm_NounToVerb':
                features[feature] = (features['Noun'] if 'Noun' in features else get_Noun(words)) / \
                                    (features['Verb'] if 'Verb' in features else get_Verb(words))
            elif feature == 'Adj':
                features[feature] = get_Adj(words)
            elif feature == 'm_AdjToN':
                features[feature] = (features['Adj'] if 'Adj' in features else get_Adj(words))/ N
            elif feature == 'm_AdjToNoun':
                features[feature] = (features['Adj'] if 'Adj' in features else get_Adj(words))/ \
                                    (features['Noun'] if 'Noun' in features else get_Noun(words))
            elif feature == 'm_AdjToS':
                features[feature] = (features['Adj'] if 'Adj' in features else get_Adj(words))/ S
            elif feature == 'Adv':
                features[feature] = get_Adv(words)
            elif feature == 'm_AdvToN':
                features[feature] = (features['Adv'] if 'Adv' in features else get_Adv(words))/ N
            elif feature == 'm_AdvToVerb':
                features[feature] = (features['Adv'] if 'Adv' in features else get_Adv(words))/ \
                                    (features['Verb'] if 'Verb' in features else get_Verb(words))
            elif feature == 'm_AdvToS':
                features[feature] = (features['Adv'] if 'Adv' in features else get_Adv(words))/ S
            elif feature == 'Prn':
                features[feature] = get_Prn(words)
            elif feature == 'm_PrnToN':
                features[feature] = (features['Prn'] if 'Prn' in features else get_Prn(words))/ N
            elif feature == 'm_PrnToNoun':
                features[feature] = (features['Prn'] if 'Prn' in features else get_Prn(words))/ \
                                     (features['Noun'] if 'Noun' in features else get_Noun(words))
            elif feature == 'm_PrnToS':
                features[feature] = (features['Prn'] if 'Prn' in features else get_Prn(words))/ S
            elif feature == 'PnPe':
                features[feature] = get_PnPe(words)
            elif feature == 'm_PnPeToPrn':
                features[feature] = (features['PnPe'] if 'PnPe' in features else get_PnPe(words)) / \
                                    (features['Prn'] if 'Prn' in features else get_Prn(words))
            elif feature == 'm_PnPeToN':
                features[feature] = (features['PnPe'] if 'PnPe' in features else get_PnPe(words))/ N
            elif feature == 'PnPe1':
                features[feature] = get_PnPe1(words)
            elif feature == 'm_PnPe1ToN':
                features[feature] = (features['PnPe1'] if 'PnPe' in features else get_PnPe1(words))/ N
            elif feature == 'PnPe2':
                features[feature] = get_PnPe2(words)
            elif feature == 'm_PnPe2ToN':
                features[feature] = (features['PnPe2'] if 'PnPe2' in features else get_PnPe2(words))/ N
            elif feature == 'PnRe':
                features[feature] = get_PnRe(words)
            elif feature == 'm_PnReToPrn':
                features[feature] = (features['PnRe'] if 'PnRe' in features else get_PnRe(words)) / \
                                    (features['Prn'] if 'Prn' in features else get_Prn(words))
            elif feature == 'm_PnReToN':
                features[feature] = (features['PnRe'] if 'PnRe' in features else get_PnRe(words))/ N
            elif feature == 'PnRi':
                features[feature] = get_PnRi(words)
            elif feature == 'm_PnRiToPrn':
                features[feature] = (features['PnRi'] if 'PnRi' in features else get_PnRi(words)) / \
                                    (features['Prn'] if 'Prn' in features else get_Prn(words))
            elif feature == 'm_PnRiToN':
                features[feature] = (features['PnRi'] if 'PnRi' in features else get_PnRi(words))/ N
            elif feature == 'm_PnReRiToPrn':
                features[feature] = ((features['PnRe'] if 'PnRe' in features else get_PnRe(words)) + \
                                     (features['PnRi'] if 'PnRi' in features else get_PnRi(words))) / \
                                    (features['Prn'] if 'Prn' in features else get_Prn(words))
            elif feature == 'm_PnReRiToN':
                features[feature] = ((features['PnRe'] if 'PnRe' in features else get_PnRe(words)) + \
                                     (features['PnRi'] if 'PnRi' in features else get_PnRi(words))) / N
            elif feature == 'PnIr':
                features[feature] = get_PnIr(words)
            elif feature == 'm_PnIrToPrn':
                features[feature] = (features['PnIr'] if 'PnIr' in features else get_PnIr(words)) / \
                                    (features['Prn'] if 'Prn' in features else get_Prn(words))
            elif feature == 'm_PnIrToN':
                features[feature] = (features['PnIr'] if 'PnIr' in features else get_PnIr(words))/ N
            elif feature == 'Cnj':
                features[feature] = get_Cnj(words)
            elif feature == 'm_CnjToS':
                features[feature] = (features['Cnj'] if 'Cnj' in features else get_Cnj(words))/ S
            elif feature == 'Prep':
                features[feature] = get_Prep(words)
            elif feature == 'm_PrepToS':
                features[feature] = (features['Prep'] if 'Prep' in features else get_Prep(words))/ S
            elif feature == 'Pt':
                features[feature] = get_Pt(words)
            elif feature == 'm_PtToS':
                features[feature] = (features['Pt'] if 'Pt' in features else get_Pt(words))/ S
            elif feature == 'PtSj':
                features[feature] = get_PtSj(words)
            elif feature == 'm_PtSjToS':
                features[feature] = (features['PtSj'] if 'PtSj' in features else get_PtSj(words))/ S
            elif feature == 'm_PtSjToVerb':
                features[feature] = (features['PtSj'] if 'PtSj' in features else get_PtSj(words))/ \
                                    (features['Verb'] if 'Verb' in features else get_Verb(words))
            elif feature == 'PVerb':
                features[feature] = get_PVerb(words)
            elif feature == 'm_PVerbToVerb':
                features[feature] = (features['PVerb'] if 'PVerb' in features else get_PVerb(words))/ V
            elif feature == 'm_PVerbToS':
                features[feature] = (features['PVerb'] if 'PVerb' in features else get_PVerb(words))/ S
            elif feature == 'Vb1':
                features[feature] = get_Vb1(words)
            elif feature == 'm_Vb1ToVerb':
                features[feature] = (features['Vb1'] if 'Vb1' in features else get_Vb1(words))/ V
            elif feature == 'Vb2':
                features[feature] = get_Vb2(words)
            elif feature == 'm_Vb2ToVerb':
                features[feature] = (features['Vb2'] if 'Vb2' in features else get_Vb2(words))/ V
            elif feature == 'VbPr':
                features[feature] = get_VbPr(words)
            elif feature == 'm_VbPrToVerb':
                features[feature] = (features['VbPr'] if 'VbPr' in features else get_VbPr(words))/ V
            elif feature == 'VbPa':
                features[feature] = get_VbPa(words)
            elif feature == 'm_VbPaToVerb':
                features[feature] = (features['VbPa'] if 'VbPa' in features else get_VbPa(words))/ V
            elif feature == 'Pp':
                features[feature] = get_Pp(words)
            elif feature == 'm_PpToS':
                features[feature] = (features['Pp'] if 'Pp' in features else get_Pp(words))/ S
            elif feature == 'PpPv':
                features[feature] = get_PpPv(words)
            elif feature == 'm_PpPvToS':
                features[feature] = (features['PpPv'] if 'PpPv' in features else get_PpPv(words))/ S
            elif feature == 'm_AdjPpPvToS':
                features[feature] = ((features['Adj'] if 'Adj' in features else get_Adj(words)) + \
                                     (features['PpPv'] if 'PpPv' in features else get_PpPv(words))) / S
            elif feature == 'm_AdjPpPvToNoun':
                features[feature] = ((features['Adj'] if 'Adj' in features else get_Adj(words)) + \
                                     (features['PpPv'] if 'PpPv' in features else get_PpPv(words))) / \
                                    (features['Noun'] if 'Noun' in features else get_Noun(words))
            elif feature == 'CjCo':
                features[feature] = get_CjCo(words)
            elif feature == 'm_CjCoΤoS':
                features[feature] = (features['CjCo'] if 'CjCo' in features else get_CjCo(words))/ S
            elif feature == 'CjSb':
                features[feature] = get_CjSb(words)
            elif feature == 'm_CjSbΤoS':
                features[feature] = (features['CjSb'] if 'CjSb' in features else get_CjSb(words))/ S
            elif feature == 'm_CjSbΤoN':
                features[feature] = (features['CjSb'] if 'CjSb' in features else get_CjSb(words))/ N
            elif feature == 'm_CjCoCjSbΤoS':
                features[feature] = ((features['CjCo'] if 'CjCo' in features else get_CjCo(words)) + \
                                     (features['CjSb'] if 'CjSb' in features else get_CjSb(words))) / S
            elif feature == 'm_CjCoCjSbΤoN':
                features[feature] = ((features['CjCo'] if 'CjCo' in features else get_CjCo(words)) + \
                                     (features['CjSb'] if 'CjSb' in features else get_CjSb(words))) / N
            elif feature == 'NoGe':
                features[feature] = get_NoGe(words)
            elif feature == 'm_NoGeToNoun':
                features[feature] = ((features['NoGe'] if 'NoGe' in features else get_NoGe(words)) / \
                                     (features['Noun'] if 'Noun' in features else get_Noun(words)))
            elif feature == 'FuncT':
                features[feature] = get_FuncT(types, func_words)
            elif feature == 'TNoun':
                features[feature] = get_TNoun(words)
            elif feature == 'm_ΤΝounToN':
                features[feature] = (features['TNoun'] if 'TNoun' in features else get_TNoun(words)) / N
            elif feature == 'm_ΤΝounToNoun':
                features[feature] = (features['TNoun'] if 'TNoun' in features else get_TNoun(words)) / \
                                     (features['Noun'] if 'Noun' in features else get_Noun(words))
            elif feature == 'm_ΤΝounToNlex':
                features[feature] = (features['TNoun'] if 'TNoun' in features else get_TNoun(words)) / \
                                    (N - (features['FuncT'] if 'FuncT' in features else get_FuncT(types, func_words)))
            elif feature == 'm_SqTNoun':
                features[feature] = ((features['TNoun'] if 'TNoun' in features else get_TNoun(words))^2) / \
                                     (features['Noun'] if 'Noun' in features else get_Noun(words))
            elif feature == 'm_CorTNoun':
                features[feature] = (features['TNoun'] if 'TNoun' in features else get_TNoun(words)) / \
                                     math.sqrt( 2 * (features['Noun'] if 'Noun' in features else get_Noun(words)) )
            elif feature == 'TVerb':
                features[feature] = get_TVerb(words)
            elif feature == 'm_ΤVerbToN':
                features[feature] = (features['TVerb'] if 'TVerb' in features else get_TVerb(words)) / N
            elif feature == 'm_ΤVerbToVerb':
                features[feature] = (features['TVerb'] if 'TVerb' in features else get_TVerb(words)) / \
                                     (features['Verb'] if 'Verb' in features else get_Verb(words))
            elif feature == 'm_ΤVerbToNlex':
                features[feature] = (features['TVerb'] if 'TVerb' in features else get_TVerb(words)) / \
                                    (N - (features['FuncT'] if 'FuncT' in features else get_FuncT(types, func_words)))
            elif feature == 'm_SqTVerb':
                features[feature] = ((features['TVerb'] if 'TVerb' in features else get_TVerb(words))^2) / \
                                     (features['Verb'] if 'Verb' in features else get_Verb(words))
            elif feature == 'm_CorTVerb':
                features[feature] = (features['TVerb'] if 'TVerb' in features else get_TVerb(words)) / \
                                     math.sqrt( 2 * (features['Verb'] if 'Verb' in features else get_Verb(words)) )
            elif feature == 'TAdj':
                features[feature] = get_TAdj(words)
            elif feature == 'm_ΤAdjToN':
                features[feature] = (features['TAdj'] if 'TAdj' in features else get_TAdj(words)) / N
            elif feature == 'm_ΤAdjToAdj':
                features[feature] = (features['TAdj'] if 'TAdj' in features else get_TAdj(words)) / \
                                     (features['Adj'] if 'Adj' in features else get_Adj(words))
            elif feature == 'm_ΤAdjToNlex':
                features[feature] = (features['TAdj'] if 'TAdj' in features else get_TAdj(words)) / \
                                    (N - (features['FuncT'] if 'FuncT' in features else get_FuncT(types, func_words)))
            elif feature == 'm_SqTAdj':
                features[feature] = ((features['TAdj'] if 'TAdj' in features else get_TAdj(words))^2) / \
                                     (features['Adj'] if 'Adj' in features else get_Adj(words))
            elif feature == 'm_CorTAdj':
                features[feature] = (features['TAdj'] if 'TAdj' in features else get_TAdj(words)) / \
                                     math.sqrt( 2 * (features['Adj'] if 'Adj' in features else get_Adj(words)) )
            elif feature == 'TAdv':
                features[feature] = get_TAdv(words)
            elif feature == 'm_ΤAdvToN':
                features[feature] = (features['TAdv'] if 'TAdv' in features else get_TAdv(words)) / N
            elif feature == 'm_ΤAdvToAdv':
                features[feature] = (features['TAdv'] if 'TAdv' in features else get_TAdv(words)) / \
                                     (features['Adv'] if 'Adv' in features else get_Adv(words))
            elif feature == 'm_ΤAdvToNlex':
                features[feature] = (features['TAdv'] if 'TAdv' in features else get_TAdv(words)) / \
                                    (N - (features['FuncT'] if 'FuncT' in features else get_FuncT(types, func_words)))
            elif feature == 'm_SqTAdv':
                features[feature] = ((features['TAdv'] if 'TAdv' in features else get_TAdv(words))^2) / \
                                     (features['Adv'] if 'Adv' in features else get_Adv(words))
            elif feature == 'm_CorTAdv':
                features[feature] = (features['TAdv'] if 'TAdv' in features else get_TAdv(words)) / \
                                     math.sqrt( 2 * (features['Adv'] if 'Adv' in features else get_Adv(words)) )
            elif feature == 'm_AdVar':
                features[feature] = ((features['TAdj'] if 'TAdj' in features else get_TAdj(words)) + \
                                     (features['TAdv'] if 'TAdv' in features else get_TAdv(words))  ) / \
                                    ( N - (features['FuncT'] if 'FuncT' in features else get_FuncT(types, func_words)) )
            elif feature == 'm_Density1':
                features[feature] = (features['FuncT'] if 'FuncT' in features else get_FuncT(types, func_words)) / \
                                    ( N - (features['FuncT'] if 'FuncT' in features else get_FuncT(types, func_words)))
            elif feature == 'm_Density2':
                features[feature] = (N - (features['FuncT'] if 'FuncT' in features else get_FuncT(types, func_words))) / N
            elif feature == 'm_YuleK':
                features[feature] = get_YuleK(types)
            elif feature == 'm_D':
                features[feature] = get_D(words, types)
            elif feature == 'm_Entr':
                features[feature] = get_Entr(types)
            elif feature == 'm_RelEntr':
                features[feature] = get_RelEntr(types)
            elif feature == 'm_Uber':
                lN = math.log10(N)
                features[feature] = (lN*lN) / (lN - math.log10(T))
            elif feature == 'm_Herdan':
                features[feature] = math.log10(T) / math.log10(N)
            elif feature == 'm_Guiraud':
                features[feature] = T / math.sqrt(N)

            else:
                # Unknown feature
                write_log('Unable to extract feature: "' + feature + '". Unknown feature, skipped.')
            """ dummy elif
            if feature == '':
                features[feature] = get_()
            """
        except ZeroDivisionError:
            features[feature] = None
    return features


def conll_sentences(data):
    """
    Extract sentences from conll data.

    @rtype : list of sentences as lists.
    @param data: conll data.
    """
    sents = []
    sent  = []
    for item in data:
        if item[0] == '1': # first item of new sentence
            # Append previous sentence in sentences.
            # Note: probably, on first for-iteration an empty first sentence is appended. Will be removed after the for-loop
            sents.append(sent)
            # Start new sentence
            sent = [item]
        else: # inside sentence
           sent.append(item)

    # remove empty first sentence
    if sents[0] == []: del sents[0]

    write_log('Sentences: {0}'.format(sents))
    debug_print('Sentences: {0}'.format(sents))
    return sents


def heads_count(sentences):
    """
    Count heads for each of a list of conll sentences

    @rtype :  a list of integers, containing the count of heads for each sentence
    @param sentences: a list of sentences. Each sentence is itself a list
    """
    # global all_count
    # if all_count != None:
    #     return all_count
    # else:
    #     all_count =[]
    all_count =[]

    for sent in sentences:
        # make a list with the nodes that head other nodes in the sentence
        heads = [x[6] for x in sent]
        # count unique heads, excluding '0'
        heads_set = set( heads )
        if '0' in heads_set:
            count= len( heads_set ) -1
        else:
            count= len( heads_set )
        all_count.append(count)

    return all_count


def get_HeadsSum( sentences ):
    """
    Sum heads for a list of sentences

    @param sentences: a list of sentences. Each sentence is itself a list
    @return: an integer containing the sum of all heads in all sentences
    """

    return sum( heads_count( sentences ) )
    


def get_HeadsAv( sentences ):
    """
    Compute average num of heads for a list of sentences

    @param sentences: a list of sentences. Each sentence is itself a list
    @return: an integer containing the average of all heads in all sentences
    """

    #return get_HeadsSum(sentences) / float(len(sentences))
    #debug_print('Diairesh: {0}, Mean: {1}'.format(get_HeadsSum(sentences) / float(len(sentences)), statistics.mean(heads_count(sentences) ) ))
    c = heads_count(sentences)
    return statistics.mean( c ) if len(c) > 0 else 0


def sentence_leaves(sentence):
    """

    @param sentence:
    """
    heads = set([x[6] for x in sentence])
    leaves = [x for x in sentence if x[0] not in heads]

    return leaves


def leaves_count( sentences ):
    """
    Count leaves for each of a list of conll sentences

    @rtype :  a list of integers, containing the count of leaves for each sentence
    @param sentences: a list of sentences. Each sentence is itself a list
    """

    all_count =[]

    for sent in sentences:
        # make a list with the leaf nodes (i.e. not heads) in the sentence
        #heads = set([x[6] for x in sent])
        #leaves = [x for x in sent if x[0] not in heads]
        all_count.append(len(sentence_leaves(sent)))

    return all_count


def get_LeavesSum(sentences):
    """
    Sum leaves for a list of sentences

    @param sentences: a list of sentences. Each sentence is itself a list
    @return: an integer containing the sum of all leaves in all sentences
    """

    return sum(leaves_count(sentences))



def get_LeavesAv(sentences):
    """
    Compute average num of leaves for a list of sentences

    @param sentences: a list of sentences. Each sentence is itself a list
    @return: an integer containing the average of all leqaves in all sentences
    """
    c = leaves_count(sentences)
    return statistics.mean( c ) if len(c) > 0 else 0


def get_DepDist(text_data):
    """
    Compute the mean of dependency distances for each sentence in a text

    @param text_data: text_data: data of text as a list
    @return: integer, the mean of dependency distances
    """

    #find dependency distance for each token
    token_depdist = [abs(int(token[0])-int(token[6])) for token in text_data]

    return statistics.mean(token_depdist) if len(token_depdist)>0 else 0


def find_node_depth(node, sentence):
    #debug_print(node[6])
    node_id = int(node[6])
    #debug_print(node_id)
    #debug_print(sentence)
    if node_id == 0:
        return 1
    elif node_id == int(node[0]): # !!! self-referencing node, it will loop, so break recursion
        write_log('ALERT! self-referencing node: {0} in sentence: {1}'.format(node_id, sentence))
        return 0
    else:
        return 1 + int( find_node_depth(sentence[node_id - 1], sentence) )


def get_DepHeight(sentences):
    """

    @param sentences:
    """
    sent_depth =[]
    for sent in sentences:
        tree_depths =[]
        for node in sentence_leaves(sent):
            tree_depths.append( find_node_depth(node, sent) )
        sent_depth.append( max(tree_depths) )
    return statistics.mean(sent_depth) if len(sent_depth) > 0 else 0


def get_DepWidth(sentences):

    dep_width =[]
    for sent in sentences:
        list = [int(x[6]) for x in sent]
        #Create a frequency distribution list
        fdist = nltk.FreqDist(list)
        dep_width += fdist
        #debug_print('dep_width list: {0}'.format(dep_width))

    return statistics.mean(dep_width) if len(dep_width) > 0 else 0


def get_syntax_features(text_data, feature_list):
    """
    Extract syntax features from text data as mentioned in a feature list from data.

    @param text_data: data of text as a list of tuples
    @param feature_list: a list of features to extract
    @rtype : a dictionary of feature - value pairs
    """

    #extract words
    sentences = conll_sentences(text_data)

    features = {}

    #Create a frequency distribution of 8th column of text_data containing syntax parts
    syntax_ids = [x[7] for x in text_data]
    debug_print('Syntax parts: {0}'.format(syntax_ids))
    syntax_ids_count = len(syntax_ids) #set to '= 1' when debugging
    debug_print('Syntax parts count: {0}'.format(syntax_ids_count))
    fd = nltk.FreqDist( syntax_ids )
    debug_print(['syntax_feat_freq', fd.most_common(100)])

    for feature in feature_list:
        if feature in ['AuxS', 'Pred', 'Sb', 'Obj', 'IObj', 'Pnom', 'Atv', 'Atr', 'AuxP', 'AuxC', 'Coord', 'Apos',\
                       'AuxX', 'AuxK', 'AuxG', 'ExD', 'AuxY', 'AuxV' ]:
            features[feature] = fd[feature] / syntax_ids_count
        elif feature in [ 'all_Co', 'all_Ap', 'all_Pa' ]:
            features[feature] = len( [ x for x in syntax_ids if feature[-3:]==x[-3:] ] ) / syntax_ids_count
        elif feature == 'DepDist':
            features[feature] = get_DepDist(text_data)
        elif feature == 'HeadsSum':
            features[feature] = get_HeadsSum(sentences)
        elif feature == 'HeadsAv':
            features[feature] = get_HeadsAv(sentences)
        elif feature == 'LeavesSum':
            features[feature] = get_LeavesSum(sentences)
        elif feature == 'LeavesAv':
            features[feature] = get_LeavesAv(sentences)
        elif feature == 'DepHeight':
            features[feature] = get_DepHeight(sentences)
        elif feature == 'DepWidth':
            features[feature] = get_DepWidth(sentences)
        else:
            # Unknown feature
            write_log('Unable to extract feature: "' + feature + '". Unknown feature, skipped.')

    return features


def av_phrase_len(data, phrase_id):
    """
    Calculate the average phrase length in text data for the given phrase

    @param phrase_id:
    @param data:
    @return: a number indicating the mean phrase length of all phrases in data
    """
    len_list = []
    word_counter = 0
    for item in data:
        if item[2] == '[' + phrase_id : # Begin of phrase
            # Start counting for the new phrase
            word_counter = 0
        elif item[2] == '/' + phrase_id + ']': # End of phrase
            # Counter holds the length of phrase. Append it to the list of phrase lengths
            len_list.append(word_counter)
            #word_counter = 0
        elif item[1] in ['TOK', 'ABBR', 'DIG']: # Word token
            word_counter += 1
    #debug_print("List of phrase lengths: {0}".format(len_list))

    return (statistics.mean(len_list) if len_list!=[] else 0)


def get_phrase_features(text_data, feature_list):
    """
    Extract phrase features from text data as mentioned in a feature list from data.

    @param text_data: data of text as a list of tuples
    @param feature_list: a list of features to extract
    @rtype : a dictionary of feature - value pairs
    """

    phrase_list = [x[2] for x in text_data]
    debug_print('Phrase list {0}'.format(phrase_list))

    features = {}

    for feature in feature_list:
        if feature in ['Np_nm', 'Np_ac', 'Np_ge', 'Np_da', 'Adjp_nm', 'Adjp_ac', 'Adjp_ge', 'Adjp_da', 'Advp', 'Pp', \
                       'Vg', 'Vg_s', 'Vg_g', 'Cl', 'Cl_r', 'Cl_ri', 'Cl_q', 'Cl_o', 'Cl_t', 'Cl_c' ]:
            features[feature] = phrase_list.count('[' + feature.lower())
        elif feature == 'Pou_np':
            # Sum-up 3 tags: Pou_np_nm, Pou_np_ac and Pou_np_ge
            features[feature] = phrase_list.count('[pou_np_nm') + phrase_list.count('[pou_np_ac') + \
                                phrase_list.count('[pou_np_ge')
        elif feature in ['L_Np_nm', 'L_Np_ac', 'L_Np_ge', 'L_Np_da', 'L_Adjp_nm', 'L_Adjp_ac', 'L_Adjp_ge', \
                         'L_Adjp_da', 'L_Advp', 'L_Pp', 'L_Vg', 'L_Vg_s', 'L_Vg_g', 'L_Cl', 'L_Cl_r', 'L_Cl_ri', \
                         'L_Cl_q', 'L_Cl_o', 'L_Cl_t', 'L_Cl_c']:
            features[feature] = av_phrase_len( text_data, feature[2:].lower() )
        elif feature == 'L_Pou_np':
            # Sum-up 3 tags: L_Pou_np_nm, L_Pou_np_ac and L_Pou_np_ge
            features[feature] = av_phrase_len( text_data, 'pou_np_nm') + av_phrase_len( text_data, 'pou_np_ac') + \
                                av_phrase_len( text_data, 'pou_np_ge')
        else:
            # Unknown feature
            write_log('Unable to extract feature: "' + feature + '". Unknown feature, skipped.')

    return features


def extract_grammar_features(features_list, path, text_ids):
    """
    Extract grammar features from files corresponding to a
     list of text id's

    @rtype : object
    @param features_list: the requested features
    @param path: path where the data files reside
    @param text_ids: a list of text id's
    """

    write_log('Now extracting grammar features.')
    write_log('grammar feature list: {0}'.format(features_list))

    result = []

    # Iterate  texts and extract features
    for text_id in text_ids:
        #Create file name from text id
        file = os.path.join(path, text_id + '.' + chunk_file_extension)
        write_log('Extracting grammar features for text: {0} from file: {1}'.format(text_id, file))
        #Check if file exists, skip if not
        if not os.path.exists(file):
            write_log('ERROR: could not find file {0}. Skipping.'.format(file))
            continue

        file_data = extract_data_from_tabbed_file(file)
        #debug_print(['file_data', file_data])
        write_log(file_data)
        result.append((
            text_id,
            file_data[0], #filename
            get_grammar_features(file_data[1],grammar_features_list),
            ))

    return result


def extract_syntax_features(features_list, path, text_ids):
    """
    Extract syntax features from files corresponding to a
     list of text id's

    @rtype : object
    @param features_list: the requested features
    @param path: path where the data files reside
    @param text_ids: a list of text id's
    """

    write_log('Now extracting syntax features.')
    write_log('Syntax feature list: {0}'.format(features_list))

    result = []

    # Iterate  data files and extract features
    for text_id in text_ids:
        #Create file name from text id
        file = os.path.join(path, text_id + '.' + conll_file_extension)
        write_log('Extracting syntax features for text: {0} from file: {1}'.format(text_id, file))
        #Check if file exists, skip if not
        if not os.path.exists(file):
            write_log('ERROR: could not find file {0}. Skipping.'.format(file))
            continue

        file_data = extract_data_from_tabbed_file(file)
        debug_print(['file_data', file_data])
        write_log(file_data)
        result.append((
            text_id,
            file_data[0], #filename
            get_syntax_features(file_data[1],features_list),
            ))

    return result




def extract_phrase_features(features_list, path, text_ids):
    """
    Extract phrase features from files corresponding to a
     list of text id's

    @rtype : object
    @param features_list: the requested features
    @param path: path where the data files reside
    @param text_ids: a list of text id's
    """

    write_log('Now extracting phrase features.')
    write_log('Phrase feature list: {0}'.format(features_list))

    result = []

    # Iterate  texts and extract features
    for text_id in text_ids:
        #Create file name from text id
        file = os.path.join(path, text_id + '.' + chunk_file_extension)
        write_log('Extracting phrase features for text: {0} from file: {1}'.format(text_id, file))
        #Check if file exists, skip if not
        if not os.path.exists(file):
            write_log('ERROR: could not find file {0}. Skipping.'.format(file))
            continue

        file_data = extract_data_from_tabbed_file(file)
        debug_print(['file_data', file_data])
        write_log(file_data)
        result.append((
            text_id,
            file_data[0], #filename
            get_phrase_features(file_data[1],phrase_features_list),
            ))
    return result




#______________________________________________________________________________________________________

if __name__ == "__main__":
    # Define default configuration file. NOTE: specify full path if different from cwd.
    default_config_file = 'def_config.cfg'

    #Parse command-line arguments
    parser = argparse.ArgumentParser(description='Extract features from corpus')
    #config_file: settings and configuration file. Optional, use default file if not specified.
    parser.add_argument("-c", "--config_file", help="settings and configuration file")
    args = parser.parse_args()
    debug_print('Command-line arguments: "{0}"'.format(args))
    if args.config_file:
        config_file = args.config_file
    else:
        print('No configuration file given. Will try to use default configuration file "{0}" instead.' \
              .format(default_config_file))
        config_file = default_config_file
    debug_print('Configuration file is "{0}"'.format(config_file))

    #Get settings from configuration file and initialize
    #Open configuration file.
    try:
        cfg_f = codecs.open(config_file, "r", "utf-8")
    except :
        # Erro if unable to open the configuration file. Should abort execution
        print('Unable to open configuration file "{0}".'.format(config_file))
        raise

    try:
        # Get Settings from configuration file.

        #Define paths for folders: Project, Data, Results.
        config=configparser.ConfigParser(allow_no_value=True)
        config.read_file(cfg_f) #codecs.open(default_config_file, "r", "utf-8"))
        paths = config['PATHS AND FILES']

        # Get Features list from configuration file
        grammar_features_list = config['FEATURES']['grammar_features_list'].split()
        syntax_features_list = config['FEATURES']['syntax_features_list'].split()
        phrase_features_list = config['FEATURES']['phrase_features_list'].split()
        # If all feature lists are empty, no features can be extracted
        if grammar_features_list == syntax_features_list == phrase_features_list == []: raise Exception
    except :
        #Terminate program if failed to get settings from configuration file.
        sys.exit('Error reading configuration file, or no features found in it: {0} . Unable to extract any features.'.\
              format(config_file))

    # Working path. All other paths are relative to this.
    working_path = os.path.abspath( paths.get('working dir', '..'))
    debug_print(['working path', working_path])
    data_path = os.path.join(working_path, paths.get('data dir', 'data'))
    debug_print(['data path', data_path])
    corpus_path = os.path.join(working_path, paths.get('corpus dir', 'corpus'))
    debug_print(['corpus path', corpus_path])
    results_path = os.path.join( working_path, paths.get('results dir', 'results'))
    debug_print(['results path', results_path])
    # Define output files
    output_filename = os.path.join( results_path, paths.get('output filename', 'featext.txt'))
    debug_print('output file: {}'.format(output_filename))
    log_filename = os.path.join( results_path, paths.get('log filename', 'feature_extract.log'))
    debug_print('logfile: {}'.format(log_filename))
    # data_path = os.path.normpath(working_path + '\\' + paths.get('data dir', 'data'))
    # debug_print(['data path', data_path])
    # corpus_path = os.path.normpath(working_path + '\\' + paths.get('corpus dir', 'corpus'))
    # debug_print(['corpus path', corpus_path])
    # results_path = working_path + '\\' + paths.get('results dir', 'results')
    # Define output files
    # output_filename = results_path + '\\' + paths.get('output filename', 'featext.txt')
    # log_filename = results_path + '\\' + paths.get('log filename', 'feature_extract.log')
    # debug_print('logfile: {}'.format(log_filename))

    # Define file extensions
    conll_file_extension = paths.get('conll file extension', 'conll')
    lem_file_extension = paths.get('lem file extension', 'lem')
    chunk_file_extension = paths.get('chunk file extension', 'chunk')
    debug_print('{0} {1} {2}'.format(conll_file_extension, lem_file_extension, chunk_file_extension))
    #Define text id's by searching for connl files and removing file extension
    text_ids = get_basenames(corpus_path, conll_file_extension)
    lem_datafiles = glob.glob(corpus_path + '\\*.lem')
    debug_print(lem_datafiles)
    #Define data files
    functional_words_filename = data_path + '\\' + paths.get('functional words filename', 'functional words.txt')

    # Write initial information to the log file
    init_log(log_filename)

    # Extract grammar features
    results_grammar_features = extract_grammar_features(grammar_features_list, corpus_path, text_ids)
    #write_log('Grammar features results: {0}'.format(results_grammar_features))
    #debug_print('Grammar features results: {0}'.format(results_grammar_features))
    # Extract syntax features
    results_syntax_features = extract_syntax_features(syntax_features_list, corpus_path, text_ids)
    #write_log('Syntax features results: {0}'.format(results_syntax_features))
    #debug_print('Syntax features results: {0}'.format(results_syntax_features))
    # Extract phrase features
    results_phrase_features = extract_phrase_features(phrase_features_list, corpus_path, text_ids)
    #debug_print('Phrase features results: {0}'.format(results_phrase_features))

    #Write to output files
    write_log('Writing results to files ...')
    write_log('Writing grammar features')
    write_results(output_filename[:-4] + '_grammar.txt', results_grammar_features, grammar_features_list)
    write_log('Writing syntax features')
    write_results(output_filename[:-4] + '_syntax.txt', results_syntax_features, syntax_features_list)
    write_log('Writing phrase features')
    write_results(output_filename[:-4] + '_phrase.txt', results_phrase_features, phrase_features_list)
    write_log('  ... done')
    write_log('---END OF PROGRAM---')

