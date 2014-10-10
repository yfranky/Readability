"""
Extract features from corpus (set of text files) for later readability assessment
"""
__author__ = 'Yorgos'

#Import modules
import os
import codecs
import glob
import re
import operator
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

#Functions


def extract_data_from_tabbed_files(files, separator='\t'):
    """
    Extract tuples of data from files containing tabbed data
    Arguments:  files: a list of files
                separator: separates the tabbed data in the file
    Returns: A list of tuples
    """
    data = []
    for file in files:
        list_of_tuples = []
        with codecs.open(file, 'r', 'utf-8') as f:
            for line in f:
                tuple = line.split(separator)
                list_of_tuples.append(tuple)
        f.close()
        data.append((os.path.basename(file), list_of_tuples))
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
    #Make dictionary from list
    d = dict(freqfreq)
    debug_print(['d', d])
    #Find the dictionary's biggest key
    max_key = sorted(d.keys(), reverse=True)[0]
    debug_print(['d keys', sorted(d.keys(), reverse=True)])
    debug_print(['biggest d key', max_key])
    #Make new list from dictionary
    new_list = [(x, d.get(x, 0)) for x in range(1,max_key+1) ]
    debug_print(['new_list', new_list])
    return new_list

"""
Initialize
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
output_filename = 'featext.txt'
log_filename = 'feature_extract.log'

# read a list of functional words from file
func_words = func_words_list(functional_words_filename)
# Define how many type frequencies are significant
#TODO: parameterize this
type_freqs_num = 10

# Open output file for writing
with  codecs.open(resultsPath + '\\' + output_filename, "w", "utf-8") as fout:
    #Write header to output file
    fout.write( 'filename\tN\tT\tChar\tawl\tS\tSL10\tSL20\tSL30\tasl\tLemT\tNoun\tVerb\tAdj'
                '\tAdv\tPrn\tPnPe\tPnPe1\tPnPe2\tPnRe\tCnj\tPrep\tPt\tPtSj\tPVerb\tVb1\tVb2\tVbPr'
                '\tVbPa\tPp\tPpPv\tCjCo\tCjSb\tNoGe\tTNoun\tTVerb\tTAdj\tTAdv\tFuncT')
    FreqT_header = ''
    for i in range(1,type_freqs_num+1):
        FreqT_header = FreqT_header + '\tFreq' + str(i)
    fout.write(FreqT_header + '\n')

    #Iterate through data files
    for file in lem_datafiles:
        with codecs.open(file, 'r', 'utf-8') as f:
            #Initialize feature variables
            numofSents = 0
            numofSents10 = 0 #Sentences of word length 10
            numofSents20 = 0
            numofSents30 = 0
            numofWords = 0
            numofChars = 0
            numofNouns = 0
            numofVerbs = 0
            numofAdjectives = 0
            numofAdverbs = 0
            numofPrn = 0
            numofPnPe = 0
            numofPnPe1 = 0
            numofPnPe2 = 0
            numofPnRe = 0
            numofCnj = 0
            numofPrep = 0
            numofPt = 0
            numofPtSj = 0
            numofPVerb = 0
            numofVb1 = 0
            numofVb2 = 0
            numofVbPr = 0
            numofVbPa = 0
            numofPp = 0
            numofPpPv = 0
            numofCjCo = 0
            numofCjSb = 0
            numofNoGe = 0
            numofTypes = 0
            numofLemmas = 0
            numofTNoun = 0
            numofTVerb = 0
            numofTAdj = 0
            numofTAdv = 0
            numofFuncT = 0


            words = []
            types = []
            type_instances = []
            lemmas = []
            noun_types = []
            verb_types = []
            adj_types = []
            adv_types = []
            # Iterate lines
            for line in f:
                tknAttr = line.split('\t')
                if tknAttr[1] == '(SENT': # Encountered beginning of sentence
                    numofSents += 1
                    sentence_words = 0
                elif tknAttr[1] == ')SENT': # Encountered end of sentence
                    #Update number of sentences with words count over 10, 20 or 30
                    if sentence_words > 30:
                        numofSents30 += 1
                    elif sentence_words > 20:
                        numofSents20 += 1
                    elif sentence_words > 10:
                        numofSents10 += 1
                elif tknAttr[1] in ['TOK', 'ABBR', 'DIG']:  # Encountered token (excl. punctuation
                    #Add token to the list of words
                    words.append(tknAttr[2])
                    #Add type instance to list of type-instances
                    type_instances.append(tknAttr[2].lower())
                    #add 1 to the total Number of tokens (TOK+ABBR+DIG)
                    numofWords += 1
                    #add 1 to the total Number of tokens (TOK+ABBR+DIG)
                    sentence_words += 1
                    #Calculate the total number of characters of all tokens
                    numofChars += len(tknAttr[2])
                    #new type
                    tkn = tknAttr[2].lower()
                    if tkn not in types:
                        types.append(tkn)
                    #new lemma
                    tkn = tknAttr[3].lower()
                    if tkn not in lemmas:
                        lemmas.append(tkn)
                    #count nouns
                    if re.match('No', tknAttr[4]):
                        numofNouns += 1
                        #check for new noun type
                        tkn = tknAttr[2].lower()
                        if tkn not in noun_types:
                            noun_types.append(tkn)
                    #count verbs
                    if re.match('Vb', tknAttr[4]):
                        numofVerbs += 1
                        #check for new verb type
                        tkn = tknAttr[2].lower()
                        if tkn not in verb_types:
                            verb_types.append(tkn)
                    #count adjectives
                    if re.match('Aj' , tknAttr[4]):
                        numofAdjectives += 1
                        #check for new adjective type
                        tkn = tknAttr[2].lower()
                        if tkn not in adj_types:
                            adj_types.append(tkn)
                    #count adverbs
                    if re.match('Ad' ,tknAttr[4]):
                        numofAdverbs += 1
                        #check for new adverb type
                        tkn = tknAttr[2].lower()
                        if tkn not in adv_types:
                            adv_types.append( tkn )
                    #count pronouns
                    if re.match('Pn', tknAttr[4]):
                        numofPrn += 1
                    #count personal pronouns
                    if re.match('PnPe', tknAttr[4]):
                        numofPnPe += 1
                    #count personal 1st ... pronouns
                    if re.match('PnPe..01', tknAttr[4]):
                        numofPnPe1 += 1
                    #count personal 2nd ... pronouns
                    if re.match('PnPe..02', tknAttr[4]):
                        numofPnPe2 += 1
                    #count PnRe pronouns
                    if re.match('PnRe', tknAttr[4]):
                        numofPnRe += 1
                    #count conjunctions
                    if re.match('Cj', tknAttr[4]):
                        numofCnj += 1
                    #count prepositions
                    if re.match('AsPp', tknAttr[4]):
                        numofPrep += 1
                    if re.match('Pt', tknAttr[4]):
                        numofPt += 1
                    if re.match('PtSj', tknAttr[4]):
                        numofPtSj += 1
                    if re.match('Vb(..){7}Pv' , tknAttr[4]):
                        numofPVerb += 1
                    if re.match('Vb(..){3}01' , tknAttr[4]):
                        numofVb1 += 1
                    if re.match('Vb(..){3}02' , tknAttr[4]):
                        numofVb2 += 1
                    if re.match('Vb(..){2}Pr' , tknAttr[4]):
                        numofVbPr += 1
                    if re.match('Vb(..){2}Pa' , tknAttr[4]):
                        numofVbPa += 1
                    if re.match('VbMnPp(..){5}Pv' , tknAttr[4]):
                        numofPpPv += 1
                    if re.match('CjCo' , tknAttr[4]):
                        numofCjCo += 1
                    if re.match('CjSb' , tknAttr[4]):
                        numofCjSb += 1
                    if re.match('No.*Ge', tknAttr[4]):
                        numofNoGe += 1





        #Calculate computed features
        awl = numofChars / numofWords #Average word length
        asl = numofWords / numofSents #Average Sentence Length (in tokens)
        numofTypes = len(types)
        numofLemmas = len(lemmas)
        numofTNoun = len(noun_types)
        numofTVerb = len(verb_types)
        numofTAdj = len(adj_types)
        numofTAdv = len(adv_types)
        #Get number of functional words
        FuncT = getFuncT(words, func_words)
        #Get frequencies of type instances
        FreqT = freq_of_freqs(type_instances)


        debug_print(['file', file])
        debug_print(['numofWords', numofWords])
        debug_print(['words', len(words)])
        debug_print(['numofTypes', numofTypes])
        debug_print(['type_instances', len(type_instances)])
        debug_print(['types', len(list(set(type_instances)))])
        debug_print(awl)
        debug_print(numofLemmas)
        debug_print(numofSents)
        debug_print(asl)


        #Write row of data to output file
        Feat_out = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t'\
                  '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.\
                   format(os.path.basename(file), numofWords, numofTypes, numofChars, awl,
                          numofSents, numofSents10, numofSents20, numofSents30, asl,
                          numofLemmas, numofNouns,
                          numofVerbs, numofAdjectives, numofAdverbs, numofPrn,
                          numofPnPe, numofPnPe1, numofPnPe2, numofPnRe,
                          numofCnj, numofPrep, numofPt, numofPtSj, numofPVerb, numofVb1,
                          numofVb2, numofVbPr, numofVbPa, numofPp, numofPpPv, numofCjCo,
                          numofCjSb, numofNoGe, numofTNoun, numofTVerb, numofTAdj, numofTAdv,
                          FuncT)
        #String with all FreqT's
        FreqT_out = ''
        for item in FreqT:
            FreqT_out = FreqT_out + '\t' + str(item[1])
        #write one row to file
        fout.write(Feat_out)
        fout.write(FreqT_out + '\n')
fout.close()
print(extract_data_from_tabbed_files(lem_datafiles))
