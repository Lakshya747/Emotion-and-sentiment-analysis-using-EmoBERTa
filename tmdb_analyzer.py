import json
import os
import pandas as pd
from emotion_analyzer import EmotionAnalyzer

class TMDBEmotionPipeline:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.analyzer = EmotionAnalyzer()

    def parse_genres(self, genre_str):
        try:
            items = json.loads(genre_str)
            return ", ".join([item["name"] for item in items[:2]])
        except:
            return "Unknown"

    def run(self, sample_size=6):
        df = pd.read_csv(self.csv_path)
        df = df.dropna(subset=["overview", "title"])
        selected_movies = df.head(sample_size).copy()

        results = []
        for _, row in selected_movies.iterrows():
            title = row["title"]
            genres = self.parse_genres(row["genres"])
            overview = row["overview"]

            prediction = self.analyzer.predict(overview)
            results.append({
                "title": title,
                "genres": genres,
                "overview": overview,
                "sentiment": prediction["sentiment"]["label"],
                "sentiment_confidence": prediction["sentiment"][prediction["sentiment"]["label"]],
                "dominant_ekman": prediction["ekman"]["dominant"],
                "ekman_score": prediction["ekman"]["scores"][prediction["ekman"]["dominant"]],
                "dominant_plutchik": prediction["plutchik"]["dominant"],
                "plutchik_score": prediction["plutchik"]["scores"][prediction["plutchik"]["dominant"]],
                "all_ekman": prediction["ekman"]["scores"],
                "all_plutchik": prediction["plutchik"]["scores"]
            })

        return results

    def print_summary(self, results):
        header = f"{'Title':<30} | {'Genres':<20} | {'Sentiment':<10} | {'Ekman':<10} | {'Plutchik':<12}"
        print(header)
        print("-" * len(header))
        for r in results:
            print(f"{r['title'][:28]:<30} | {r['genres'][:18]:<20} | {r['sentiment']:<10} | {r['dominant_ekman']:<10} | {r['dominant_plutchik']:<12}")

if __name__ == "__main__":
    dataset_file = r"C:\Users\Luckyboi\.gemini\antigravity\scratch\neurosymbolic_sentiment\data\tmdb_5000_movies.csv"
    pipeline = TMDBEmotionPipeline(dataset_file)
    analysis_results = pipeline.run(sample_size=6)
    pipeline.print_summary(analysis_results)
    print("\nDetailed Movie Analysis:")
    for item in analysis_results[:2]:
        print("\n" + "=" * 60)
        print(f"Title: {item['title']} ({item['genres']})")
        print(f"Overview: {item['overview']}")
        print(f"Sentiment: {item['sentiment']} (score: {item['sentiment_confidence']})")
        print(f"Ekman Model: {item['dominant_ekman']} -> {item['all_ekman']}")
        print(f"Plutchik Wheel: {item['dominant_plutchik']} -> {item['all_plutchik']}")
