import nltk
import numpy as np
from nltk import word_tokenize, pos_tag


class SentenceSubjectAnalyzer:
    def __init__(self):
        print("SubjectAnalyzer created")
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('maxent_ne_chunker')
        nltk.download('words')
        nltk.download('wordnet')
        print("NLTK downloaded")

    def parse_sentence_subject(self, sentence):
        # Tokenize the sentence
        tokens = nltk.word_tokenize(sentence)

        # Tag the tokens with their part of speech
        tags = nltk.pos_tag(tokens)

        # Extract the nouns, named entities, and adjectives
        relevant_words = []
        for token, tag in tags:
            # TODO if two nnp's are next to each other than make them one entity

            if (tag.startswith("NN") 
                or tag.startswith("NNP") 
                or tag.startswith("JJ")):
                relevant_words.append(token)

        # Remove duplicates from the lists
        # relevant_words = list(set(relevant_words))

        # Return the nouns, verbs, and entities in the order they appeared
        
        #make a string out of the list
        newSetence = ""
        
        for word in relevant_words:
            newSetence = newSetence + word + " "
        
        return newSetence



# Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# analyzer = SentenceSubjectAnalyzer()

# sentenceContent = analyzer.parse_sentence_subject("The night of christmas eve, all the children prepare cookies for Santa Claus because its a western tradition.")
# print(sentenceContent)
# newSetence = ""

# for word in sentenceContent:
#     newSetence = newSetence + word + " "

# print(newSetence)
       
# print(analyzer.parse_sentence_subject("The quick brown fox jumps over the lazy dog."))

# print(analyzer.parse_sentence_subject("Um I of course celebrate Quanza but for today I'm making um, and we have all of this. I am Jewish. I am Jewish and muslim."))
