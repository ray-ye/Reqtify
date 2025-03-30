from sentence_transformers import SentenceTransformer
import csv

class MusicFeatureGuesser:
    # terrible name but whatever
    def __init__(self, file_path: str = None):
        """Initializes the MusicFeatureGuesser class"""
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.features = None
        self.mean_vectors = []

        if file_path is not None:
            with open(file_path, 'r', encoding="utf-8") as file:
                reader = csv.DictReader(file)
                header = reader.fieldnames
                self.features = header[1:]
                self.mean_vectors = [0] * len(self.features)

                for row in reader:
                    # Convert the row to a list of floats
                    vector = [float(row[feature]) for feature in self.features]
                    self.mean_vectors.append(vector) 

    def predict_features(self, user_input: str):
        """Predicts the music features based on the user input"""
        sentence_embedding = self.embedder.encode(user_input)
        for feature in self.features:
            pass
            
        # similarity = self.embedder.similarity(sentence_embedding, base)
        # print(f"Similarity': {similarity}")

        # is_explicit = 0
        # if similarity > 0.5:
        #     is_explicit = 1
        # return is_explicit
