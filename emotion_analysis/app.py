import difflib
import json
import os
import random
import re
import sys
from emotion_analyzer import EmotionAnalyzer

class MovieReviewsApp:
    def __init__(self, data_path):
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Dataset not found at: {data_path}")
        self.data_path = data_path
        with open(data_path, "r", encoding="utf-8") as f:
            self.movies = json.load(f)
        print(f"Loaded {len(self.movies)} movies with respective reviews.")
        print("Initializing EmoBERTa model...")
        self.analyzer = EmotionAnalyzer()
        print("Model initialized successfully.\n")

    def normalize(self, text):
        return re.sub(r"[^a-zA-Z0-9\s]", "", str(text).lower()).strip()

    def score_match(self, query, movie):
        q = self.normalize(query)
        if not q:
            return 0.0

        title = self.normalize(movie["title"])
        if q == title:
            return 100.0
        if q in title or title in q:
            return 85.0

        aliases = [self.normalize(a) for a in movie.get("aliases", [])]
        for alias in aliases:
            if q == alias:
                return 95.0
            if q in alias or alias in q:
                return 80.0

        q_words = set(q.split())
        title_words = set(title.split())
        word_overlap = q_words.intersection(title_words)
        if word_overlap:
            return 60.0 + len(word_overlap) * 10.0

        for alias in aliases:
            alias_words = set(alias.split())
            if q_words.intersection(alias_words):
                return 55.0

        ratio = difflib.SequenceMatcher(None, q, title).ratio()
        if ratio > 0.5:
            return ratio * 50.0

        genres = self.normalize(movie.get("genres", ""))
        if any(w in genres for w in q_words if len(w) > 3):
            return 30.0

        return 0.0

    def display_movie_analysis(self, movie):
        title = movie["title"]
        year = movie.get("year", "")
        genres = movie.get("genres", "")
        reviews = movie.get("reviews", [])

        print("=" * 72)
        print(f"MOVIE: {title} ({year})")
        print(f"GENRES: {genres}")
        print(f"TOTAL REVIEWS: {len(reviews)}")
        print("=" * 72)

        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        ekman_totals = {"anger": 0.0, "disgust": 0.0, "fear": 0.0, "joy": 0.0, "sadness": 0.0, "surprise": 0.0}
        plutchik_totals = {"joy": 0.0, "sadness": 0.0, "anger": 0.0, "fear": 0.0, "disgust": 0.0, "surprise": 0.0, "trust": 0.0, "anticipation": 0.0}

        for idx, rev in enumerate(reviews):
            reviewer = rev.get("reviewer", f"Reviewer {idx + 1}")
            rating = rev.get("rating", "")
            gt = rev.get("ground_truth", "")
            text = rev["text"]

            print(f"\n--- Review [{idx + 1}] by {reviewer} (Rating: {rating} | Label: {gt}) ---")
            print(f"\"{text}\"")

            res = self.analyzer.predict(text)

            pred_sent = res["sentiment"]["label"]
            conf = res["sentiment"][pred_sent]
            sentiment_counts[pred_sent] += 1

            dom_ekman = res["ekman"]["dominant"]
            for em, sc in res["ekman"]["scores"].items():
                ekman_totals[em] += sc

            dom_plutchik = res["plutchik"]["dominant"]
            for em, sc in res["plutchik"]["scores"].items():
                plutchik_totals[em] += sc

            print(f"  Sentiment : {pred_sent.upper()} (Confidence: {conf})")
            print(f"  Ekman     : {dom_ekman.upper()} ({res['ekman']['scores'][dom_ekman]:.4f})")
            print(f"  Plutchik  : {dom_plutchik.upper()} ({res['plutchik']['scores'][dom_plutchik]:.4f})")

        total_revs = len(reviews)
        if total_revs > 0:
            avg_ekman = {k: v / total_revs for k, v in ekman_totals.items()}
            avg_plutchik = {k: v / total_revs for k, v in plutchik_totals.items()}
            consensus_ekman = max(avg_ekman, key=avg_ekman.get)
            consensus_plutchik = max(avg_plutchik, key=avg_plutchik.get)

            pos_pct = (sentiment_counts["positive"] / total_revs) * 100
            neg_pct = (sentiment_counts["negative"] / total_revs) * 100
            neu_pct = (sentiment_counts["neutral"] / total_revs) * 100

            print("\n" + "=" * 72)
            print(f"OVERALL AUDIENCE EMOTIONAL CONSENSUS FOR: {title}")
            print("=" * 72)
            print(f"Sentiment Ratio: {pos_pct:.1f}% Positive | {neg_pct:.1f}% Negative | {neu_pct:.1f}% Neutral")
            print(f"\nConsensus Ekman Emotion   : {consensus_ekman.upper()} (Avg score: {avg_ekman[consensus_ekman]:.4f})")
            for em, sc in avg_ekman.items():
                bar = "#" * int(sc * 30)
                print(f"  {em.capitalize():<10}: {sc:.4f} {bar}")

            print(f"\nConsensus Plutchik Emotion: {consensus_plutchik.upper()} (Avg score: {avg_plutchik[consensus_plutchik]:.4f})")
            for em, sc in avg_plutchik.items():
                bar = "#" * int(sc * 30)
                print(f"  {em.capitalize():<12}: {sc:.4f} {bar}")
            print("=" * 72 + "\n")

    def analyze_random_movie(self):
        movie = random.choice(self.movies)
        self.display_movie_analysis(movie)

    def search_and_analyze_movie(self):
        query = input("Enter movie title, character, or keyword (e.g. Batman, Nolan, Titanic, Spiderman): ").strip()
        if not query:
            print("Search query cannot be empty.\n")
            return

        scored_matches = []
        for m in self.movies:
            score = self.score_match(query, m)
            if score > 20.0:
                scored_matches.append((score, m))

        scored_matches.sort(key=lambda x: x[0], reverse=True)

        if not scored_matches:
            print(f"\nNo exact film found for '{query}'.")
            print("Here are all available movies in the catalog:")
            for idx, m in enumerate(self.movies):
                print(f"  [{idx + 1}] {m['title']} ({m['year']})")
            choice = input(f"\nSelect a movie [1-{len(self.movies)}] or enter 'c' to analyze a custom review: ").strip()
            if choice.lower() == "c":
                self.add_custom_review(default_title=query)
            elif choice.isdigit() and 1 <= int(choice) <= len(self.movies):
                self.display_movie_analysis(self.movies[int(choice) - 1])
            else:
                print("Search cancelled.\n")
            return

        if len(scored_matches) == 1:
            self.display_movie_analysis(scored_matches[0][1])
            return

        if top_score >= 90.0:
            self.display_movie_analysis(scored_matches[0][1])
            return

        print(f"\nFound {len(scored_matches)} close matches for '{query}':")
        display_candidates = scored_matches[:6]
        for idx, (_, m) in enumerate(display_candidates):
            print(f"  [{idx + 1}] {m['title']} ({m['year']}) - {m['genres']}")

        choice = input(f"\nSelect movie [1-{len(display_candidates)}] (Press Enter for [1]): ").strip()
        if not choice:
            self.display_movie_analysis(display_candidates[0][1])
            return

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(display_candidates):
                self.display_movie_analysis(display_candidates[idx][1])
            else:
                print("Invalid selection.\n")
        else:
            print("Search cancelled.\n")

    def add_custom_review(self, default_title=None):
        if default_title:
            target_movie = default_title
        else:
            target_movie = input("Enter movie title to review: ").strip()
            if not target_movie:
                print("Movie title cannot be empty.\n")
                return

        review_text = input(f"Enter your review for '{target_movie}': ").strip()
        if not review_text:
            print("Review text cannot be empty.\n")
            return

        print("\nAnalyzing review...")
        res = self.analyzer.predict(review_text)
        print("-" * 65)
        print(f"Movie: {target_movie}")
        print(f"Your Review: \"{review_text}\"")
        print(f"Predicted Sentiment: {res['sentiment']['label'].upper()} ({res['sentiment'][res['sentiment']['label']]})")
        print(f"Ekman Emotion      : {res['ekman']['dominant'].upper()} ({res['ekman']['scores'][res['ekman']['dominant']]})")
        print(f"Plutchik Emotion   : {res['plutchik']['dominant'].upper()} ({res['plutchik']['scores'][res['plutchik']['dominant']]})")
        print("-" * 65 + "\n")

    def run_menu(self):
        while True:
            print("************************************************")
            print("   MOVIE REVIEWS EMOTION & SENTIMENT ANALYZER   ")
            print("************************************************")
            print("1. Randomly pick a movie and analyze its reviews")
            print("2. Search a movie by title and analyze its reviews")
            print("3. Add and analyze your own movie review")
            print("4. Exit")
            print("************************************************")

            choice = input("Enter your choice (1/2/3/4): ").strip()
            print()

            if choice == "1":
                self.analyze_random_movie()
            elif choice == "2":
                self.search_and_analyze_movie()
            elif choice == "3":
                self.add_custom_review()
            elif choice == "4":
                print("Exiting application. Goodbye!")
                break
            else:
                print("Invalid option. Please enter 1, 2, 3, or 4.\n")

if __name__ == "__main__":
    dataset_file = r"C:\Users\Luckyboi\.gemini\antigravity\scratch\emotion_analysis\movies_reviews_dataset.json"
    app = MovieReviewsApp(dataset_file)
    app.run_menu()
