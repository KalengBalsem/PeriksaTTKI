import re
import pandas as pd
import string

# BINARY SEARCH ALGO
def binary_search(words, target):
  low = 0
  high = len(words) - 1

  while low <= high:
    mid = (low + high) // 2
    if words[mid] == target:
      return mid
    elif words[mid] < target:
      low = mid + 1
    else:
      high = mid - 1

  return -1

# INITIALIZING DICTIONARY
def words(text):
    return re.findall(r'\w+', text.lower())

path_corpus = r'C:\Users\balse\Documents\VScode\PeriksaTTKI\PeriksaTTKI\model_api\kbbi.csv'

WORDS = pd.read_csv(path_corpus)
WORDS = [str(i).strip() for i in WORDS['kata']]
####


# PICKING CANDIDATES
def candidates(word):
    return known(edits1(word)) or known(edits2(word)) or [word]

# Peter Norvig algorithm
def known(words):
    bst = [binary_search(WORDS, _) for _ in words]
    return set(WORDS[_] for _ in bst if _ != -1)

def edits1(word):
    letters = "abcdefghijklmnopqrstvwxyz"
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces = [L + c + R[1:] for L, R in splits for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))
####


# RUN SPELL CHECK
def spell_check(sentence):
    # initializing typo_words and corrected_words
    typo_words = []
    word_suggestions = {}
    corrected_words = []
    # Define a regular expression pattern to split text while preserving punctuation
    pattern = r'(\w+|[^\w\s]|\s)'
    words = re.findall(pattern, sentence)
    ####
    punctuation = string.punctuation
    for word in words:
        found_word = word.lower() in WORDS

        # THIS PART CAN BE OPTIMIZED
        if not found_word and word not in string.punctuation and not word.isspace():
            typo_words.append(f'<span class="wrong">{word}</span>')

            # performing spell checker
            word_suggestions[word] = [i for i in candidates(word)]
            word = word_suggestions[word][0]  # still inefficient)

        ####
        else:
            typo_words.append(word)

        corrected_words.append(word)

    return ''.join(typo_words), ''.join(corrected_words), word_suggestions
