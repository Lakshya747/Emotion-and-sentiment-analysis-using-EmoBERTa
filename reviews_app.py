import random
import sys
from datasets import load_dataset
from emotion_analyzer import EmotionAnalyzer

class MovieReviewsApp:
    def __init__(self):
        print("Loading Rotten Tomatoes movie reviews dataset from local cache...")
        dataset = load_dataset("cornell-movie-review-data/rotten_tomatoes", split="train")
        self.reviews = [
            {
                "text": item["text"],
                "original_sentiment": "Positive" if item["label"] == 1 else "Negative"
            }
            for item in dataset
        ]
        print(f"Loaded {len(self.reviews)} movie reviews successfully.")
        print("Initializing EmoBERTa emotion analyzer...")
        self.analyzer = EmotionAnalyzer()
        print("Analyzer ready.\n")

    def display_analysis(self, review_text, original_sentiment=None):
        print("=" * 70)
        print(f"REVIEW:\n\"{review_text}\"")
        if original_sentiment:
            print(f"\nORIGINAL DATASET LABEL: {original_sentiment}")
        print("-" * 70)

        res = self.analyzer.predict(review_text)

        sentiment_info = res["sentiment"]
        print(f"PREDICTED SENTIMENT: {sentiment_info['label'].upper()} (Score: {sentiment_info[sentiment_info['label']]})")
        print(f"  Positive: {sentiment_info['positive']} | Negative: {sentiment_info['negative']} | Neutral: {sentiment_info['neutral']}")

        ekman_info = res["ekman"]
        print(f"\nEKMAN 6 BASIC EMOTIONS: [Dominant: {ekman_info['dominant'].upper()}]")
        for emotion, score in ekman_info["scores"].items():
            bar = "#" * int(score * 30)
            print(f"  {emotion.capitalize():<10}: {score:.4f} {bar}")

        plutchik_info = res["plutchik"]
        print(f"\nPLUTCHIK'S WHEEL OF EMOTION: [Dominant: {plutchik_info['dominant'].upper()}]")
        for emotion, score in plutchik_info["scores"].items():
            bar = "#" * int(score * 30)
            print(f"  {emotion.capitalize():<12}: {score:.4f} {bar}")
        print("=" * 70 + "\n")

    def analyze_random_review(self):
        sample = random.choice(self.reviews)
        self.display_analysis(sample["text"], sample["original_sentiment"])

    def search_and_analyze_review(self):
        query = input("Enter a keyword, movie, or phrase to search: ").strip()
        if not query:
            print("Search query cannot be empty.\n")
            return

        matches = [r for r in self.reviews if query.lower() in r["text"].lower()]
        match_count = len(matches)

        if match_count == 0:
            print(f"No reviews found containing '{query}'.\n")
            return

        if match_count == 1:
            self.display_analysis(matches[0]["text"], matches[0]["original_sentiment"])
            return

        print(f"\nFound {match_count} reviews matching '{query}':")
        display_matches = matches[:6]
        for idx, item in enumerate(display_matches):
            snippet = item["text"][:75] + ("..." if len(item["text"]) > 75 else "")
            print(f"  [{idx + 1}] ({item['original_sentiment']}) \"{snippet}\"")

        choice = input(f"\nSelect a review [1-{len(display_matches)}] or press Enter to cancel: ").strip()
        if choice.isdigit():
            chosen_idx = int(choice) - 1
            if 0 <= chosen_idx < len(display_matches):
                selected = display_matches[chosen_idx]
                self.display_analysis(selected["text"], selected["original_sentiment"])
            else:
                print("Invalid selection.\n")
        else:
            print("Search cancelled.\n")

    def analyze_custom_review(self):
        user_text = input("Enter your custom review text: ").strip()
        if not user_text:
            print("Review text cannot be empty.\n")
            return
        self.display_analysis(user_text, original_sentiment="Custom User Input")

    def run_menu(self):
        while True:
            print("****************************************")
            print("     MOVIE REVIEWS EMOTION ANALYZER     ")
            print("****************************************")
            print("1. Randomly choose a review and analyze")
            print("2. Search reviews by keyword and analyze")
            print("3. Enter your own custom review to analyze")
            print("4. Exit")
            print("****************************************")

            choice = input("Enter your choice (1/2/3/4): ").strip()
            print()

            if choice == "1":
                self.analyze_random_review()
            elif choice == "2":
                self.search_and_analyze_review()
            elif choice == "3":
                self.analyze_custom_review()
            elif choice == "4":
                print("Exiting application. Goodbye!")
                break
            else:
                print("Invalid option. Please enter 1, 2, 3, or 4.\n")

if __name__ == "__main__":
    app = MovieReviewsApp()
    app.run_menu()
