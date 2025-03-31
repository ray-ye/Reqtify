import csv
import torch
import numpy as np
from sentence_transformers import SentenceTransformer


class MusicFeatureGuesser:
    # awful class name. can't think of anything better
    def __init__(self, file_path: str = None):
        """Initializes the MusicFeatureGuesser class"""
        # algorithm:
        # look at the sentences -> vectorize, keep track of the features for each sentence
        # uesr input ->
        # vectorize ->
        # find similarity with the sentences ->
        # get features that are common with similar sentence
        # return the boolean values for the features
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.features = []
        self.sentence_music_features = []
        self.sentence_embeddings = []

        if file_path is not None:
            self.load_data(file_path)

    def load_data(self, file_path: str):
        """Loads the data from the CSV file"""
        with open(file_path, 'r', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            header = reader.fieldnames
            self.features = header[1:]
            self.sentences = []
            self.sentence_music_features = []
            self.sentence_embeddings = []

            for row in reader:
                self.sentences.append(row['sentence'])
                music_features = np.array([float(row[feature]) for feature in self.features])
                self.sentence_music_features.append(music_features)

        self.sentence_embeddings = self.embedder.encode(self.sentences)

    def predict_features(self, user_input: str, tolerance: int=3):
        """
        Predicts the music features based on the user input. A higher tolerance implies a lower threshold for similarity.
        Preconditions:
            - tolerance > 0
            - user_input is a non-empty string
        """
        # Calculate similarities
        sentence_embedding = self.embedder.encode(user_input)
        similarities = self.embedder.similarity(sentence_embedding, self.sentence_embeddings)[0]

        # Get indices of top k most similar sentences
        indices = torch.topk(similarities, k=tolerance)[1]

        # Get the 'normal' music features of the most similar sentences
        avg = np.mean([self.sentence_music_features[idx] for idx in indices], axis=0)
        avg = np.round(avg).astype(int)
        features = avg.tolist()

        return features


if __name__ == '__main__':
    # Example usage
    file_path = 'reference_data.csv'
    guesser = MusicFeatureGuesser(file_path)
    user_input = "Upbeat study music"
    tolerance = 5
    features = guesser.predict_features(user_input, tolerance)
    for feature_name, value in zip(guesser.features, features):
        print(feature_name, ":", value)

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })
