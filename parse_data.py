import csv
rows = []
with open('dataset.csv', 'r', encoding="utf-8") as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        row = {
            'track_id': row['track_id'],
            'is_explicit': True if row['explicit'] == 'True' else False,
            'is_energetic': float(row['energy']) > 0.5,
            'is_instrumental': float(row['instrumentalness']) > 0.5,
            'is_acoustic': float(row['acousticness']) > 0.5,
            'is_happy': float(row['valence']) > 0.5,
            'is_loud': float(row['loudness']) > -7,
            'is_major': int(row['mode']) == 1,
            'is_danceable': float(row['danceability']) > 0.6,
            'is_live': float(row['liveness']) > 0.8,
            'is_fast': float(row['tempo']) > 120,
        }
        rows.append(row)

with open('songs.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['track_id', 'is_explicit', 'is_energetic', 'is_instrumental', 'is_acoustic', 'is_happy',
                                              'is_loud', 'is_major', 'is_danceable', 'is_live', 'is_fast'])
    writer.writeheader()
    
    writer.writerows(rows)