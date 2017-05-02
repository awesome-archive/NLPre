import pattern
import operator
import nlpre.identify_parenthetical_phrases as IPP


class replace_acronyms():

    """
    Replaces acronyms and abbreviations found in a document with their
    corresponding phrase. A counter dictionary is passed in __init__
    to determine phrases.

    If an acronym is explicitly identified with a phrase in a document, then
    all instances of that acronym in the document will be replaced with the
    given phrase.

    Example:
        input: "The Environmental Protection Agency (EPA) protects trees. The
                EPA was created by Nixon"
        output: "The Environmental Protection Agency
                 (Environmental_Protection_Agency) protects trees. The
                 Environmental_Protection_Agency was created by Nixon"

    If there is no explicit indication what the phrase is within the document,
    then the most common phrase associated with the acronym in the given
    counter is used.

    Example:
        input: "The EPA protects trees"
        output: "The Environmental_Protection_Agency protects trees"
    """

    def __init__(self, counter, underscore=True, preprocessed=False):
        '''
        Initialize the parser, the acronym dictionary, and flags

        Args:
            counter: A counter object of acronyms and their counts found in a
                     larger corpus
            underscore: A boolean to indicate whether to insert phrases
                        as a single underscored token
            preprocessed: A boolean to indicate if input text is raw,
                          or has been processed by other NLPre modules
        '''

        self.counter = counter
        self.underscore = underscore
        self.preprocessed = preprocessed
        self.IPP = IPP.identify_parenthetical_phrases()

        self.parse = lambda x: pattern.en.tokenize(x)

        self.acronym_dict = {}

        for acronym_tuple, count in self.counter.iteritems():
            if acronym_tuple[1] in self.acronym_dict:
                self.acronym_dict[acronym_tuple[1]].append(
                    [acronym_tuple[0], count])
            else:
                self.acronym_dict[acronym_tuple[1]] = [(acronym_tuple[0],
                                                        count)]

    def check_acronym(self, token):
        '''
        Check if a token is an acronym to be replaced

        Args:
            token: a string token
        Returns:
            a boolean
        '''

        if token.lower() == token:
            return False

        if token in self.acronym_dict:
            return True
        else:
            return False

    def check_self_counter(self, token, doc_counter):
        '''
        Check if an acronym token is defined within the document

        Args:
            token: a string token
            doc_counter: a counter object of acronyms defined within a document
        Returns:
            a boolean
        '''

        for acronym_tuple in doc_counter.iterkeys():
            if acronym_tuple[1] == token:
                highest_phrase = list(acronym_tuple[0])
                return highest_phrase
        return False

    def __call__(self, document, doc_counter=None):
        '''
        Identify and replace all acronyms in the document

        Args:
            document: a string
            doc_counter: a counter object of acronyms defined within a
                         document. If missing, identify_parenthetical_phrases
                         is run.
        Returns:
            new_doc: a string
        '''

        if doc_counter is None:
            doc_counter = self.IPP(document)

        if self.preprocessed:
            sentences = document.split('\n')
        else:
            sentences = self.parse(document)

        new_doc = []

        for sentence in sentences:
            tokens = sentence.split()
            new_sentence = []
            for token in tokens:
                if self.check_acronym(token):
                    # check if acronym is used within document
                    highest_phrase = self.check_self_counter(
                        token, doc_counter)

                    if not highest_phrase:
                        acronym_counts = self.acronym_dict[token]
                        acronym_counts.sort(
                            key=operator.itemgetter(1), reverse=True)
                        highest_phrase = acronym_counts[0][0]

                    if self.underscore:
                        new_sentence.append('_'.join(highest_phrase))
                    else:
                        new_sentence.extend(highest_phrase)

                else:
                    new_sentence.append(token)
            new_doc.append(' '.join(new_sentence))

        return '\n'.join(new_doc)