import nltk

class Analyzer():
    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        self.positives = set()
        self.negatives = set()
        file = open(positives, "r")
        for line in file:
            if line.startswith("\n") == True:
                line = line.strip()
            if line.startswith(";") == False:
                self.positives.add(line.rstrip("\n"))
        file.close()
        file = open(negatives, "r")
        for line in file:
            if line.startswith("\n") == True:
                line = line.strip()
            if line.startswith(";") == False:
                self.negatives.add(line.rstrip("\n"))
        file.close()
        

    def analyze(self, text):
        sent = 0
        """Analyze text for sentiment, returning its score."""
        tokenizer = nltk.tokenize.TweetTokenizer()
        tokens = tokenizer.tokenize(text)
        for token in tokens:
            if token in self.positives:
                sent += 1
            elif token in self.negatives:
                sent += -1
            else:
                sent += 0
    
        return sent
