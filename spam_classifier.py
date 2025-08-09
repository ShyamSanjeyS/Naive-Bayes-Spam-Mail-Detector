# spam_classifier.py
import os
import numpy as np
from collections import Counter
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

class SpamMailClassifier:
    def __init__(self, train_path, test_path, model_type='gaussian'):
        self.train_path = train_path
        self.test_path = test_path
        self.model_type = model_type.lower()
        self.words_dict = []
        self.model = None

    def create_dict(self):
        all_email_words = []
        all_emails = [os.path.join(self.train_path, file) for file in os.listdir(self.train_path)]
        for email in all_emails:
            with open(email, encoding="latin1") as e:
                for text in e:
                    all_email_words += text.split()
        words_dict = Counter(all_email_words)
        for word in list(words_dict):
            if not word.isalpha() or len(word) == 1:
                del words_dict[word]
        self.words_dict = words_dict.most_common(3000)

    def get_features(self, folder):
        email_files = [os.path.join(folder, f) for f in os.listdir(folder)]
        freq_matrix = np.zeros((len(email_files), 3000))
        labels = np.zeros(len(email_files))
        for i, file in enumerate(email_files):
            with open(file, encoding="latin1") as fi:
                for pos, line in enumerate(fi):
                    if pos == 2:
                        words = line.split()
                        for word in words:
                            for j, w in enumerate(self.words_dict):
                                if w[0] == word:
                                    freq_matrix[i, j] = words.count(word)
            filename = os.path.basename(file)
            labels[i] = 1 if filename.startswith("spmsg") else 0
        return freq_matrix, labels

    def train_and_evaluate(self):
        self.create_dict()
        train_X, train_y = self.get_features(self.train_path)
        test_X, test_y = self.get_features(self.test_path)

        if self.model_type == 'gaussian':
            self.model = GaussianNB()
        elif self.model_type == 'multinomial':
            self.model = MultinomialNB()
        elif self.model_type == 'bernoulli':
            self.model = BernoulliNB()
        else:
            raise ValueError("Invalid model type. Choose from 'gaussian', 'multinomial', 'bernoulli'.")

        self.model.fit(train_X, train_y)
        predictions = self.model.predict(test_X)
        acc = accuracy_score(test_y, predictions)
        conf_matrix = confusion_matrix(test_y, predictions)
        report = classification_report(test_y, predictions, target_names=["Non-Spam", "Spam"])
        return acc, conf_matrix, report

    def predict_text(self, text):
        freq_vector = np.zeros((1, 3000))
        words = text.split()
        for word in words:
            for i, w in enumerate(self.words_dict):
                if w[0] == word:
                    freq_vector[0, i] = words.count(word)
        pred = self.model.predict(freq_vector)
        return "Spam" if pred[0] == 1 else "Non-Spam"
