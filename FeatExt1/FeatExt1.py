__author__ = 'Yorgos'

import os, codecs, re, glob
import nltk

projectPath = os.getcwd() + '\\..'
dataPath = projectPath + '\\data'
resultsPath = projectPath + '\\results'
dataFiles = glob.glob(dataPath + '\\*.lem')
print dataFiles
# Open output file for writing
with  codecs.open(resultsPath + '\\featext.txt', "w", "utf-8") as fout:
    # Write header to output file
    fout.write('filename\ttokens\ttypes\tawl\tlemma_types\tsentences\tasl\tnouns\tverbs\tadjectives\tadverbs\tpronouns\tconjunctions\tfreq1\tfreq2\tfreq3\tfreq4\tfreqn\n')
    for file in dataFiles:
        with codecs.open(file, 'r', 'utf-8') as f:
            # Initialize feature variables
            numofSents = 0
            numofTokens = 0
            charsofTokens = 0
            types = []
            lemmas = []
            # Iterate lines
            for line in f:
                # print line
                tknAttr = line.split('\t')
                if tknAttr[1] == '(SENT': # Encountered beginning of sentence
                    numofSents += 1
                elif tknAttr[1] in ['TOK', 'ABBR', 'DIG']:  # Encountered token (excl. punctuation
                    # Calculate the Number of tokens (TOK+ABBR+DIG)
                    numofTokens += 1
                    # Calculate the total number of characters of all tokens
                    charsofTokens += len(tknAttr[2])
                    # Check if new type
                    if tknAttr[2] not in types:
                        types.append(tknAttr[2])
                        # Check if new lemma
                    if tknAttr[3] not in lemmas:
                        lemmas.append(tknAttr[3])

        # Calculate computed features
        awl = charsofTokens / numofTokens # Average word length
        numofTypes = len(types)
        numofLemmas = len(lemmas)
        tokensperSentence = numofTokens / numofSents


        print file
        print numofTokens
        print awl
        print numofTypes
        print numofLemmas
        print numofSents
        print tokensperSentence
        # Write output to file
        lineout = '{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(os.path.basename(file), numofTokens, numofTypes, awl, numofLemmas, numofSents, tokensperSentence)
        fout.write(lineout)
fout.close()
