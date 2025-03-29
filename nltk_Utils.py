import nltk

nltk.download("rslp")

from nltk.stem import RSLPStemmer
stemmer = RSLPStemmer()

# Separa as palavras por tokens relevantes
def tokenize(sentence):
    return nltk.word_tokenize(sentence)

# Simplifica as palavras da mesma "familia"
def stem(word):
    return stemmer.stem(word.lower())

a = "organização, organizas, organizou, organizado"
print(a)
a = tokenize(a)
print(a)

a = [stem(x) for x in a]
print(a)
