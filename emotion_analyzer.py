import pprint
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class EmotionAnalyzer:
    def __init__(self, model_name="tae898/emoberta-large"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
        self.model.eval()
        self.labels = [self.model.config.id2label[i].lower() for i in range(self.model.config.num_labels)]

    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)[0].tolist()

        raw_scores = dict(zip(self.labels, probabilities))

        ekman_emotions = ["anger", "disgust", "fear", "joy", "sadness", "surprise"]
        ekman_scores = {emotion: raw_scores.get(emotion, 0.0) for emotion in ekman_emotions}
        dominant_ekman = max(ekman_scores, key=ekman_scores.get)

        plutchik_scores = {
            "joy": raw_scores.get("joy", 0.0),
            "sadness": raw_scores.get("sadness", 0.0),
            "anger": raw_scores.get("anger", 0.0),
            "fear": raw_scores.get("fear", 0.0),
            "disgust": raw_scores.get("disgust", 0.0),
            "surprise": raw_scores.get("surprise", 0.0),
            "trust": (raw_scores.get("joy", 0.0) * 0.6) + (raw_scores.get("neutral", 0.0) * 0.4),
            "anticipation": (raw_scores.get("surprise", 0.0) * 0.5) + (raw_scores.get("joy", 0.0) * 0.5)
        }
        dominant_plutchik = max(plutchik_scores, key=plutchik_scores.get)

        pos_score = raw_scores.get("joy", 0.0)
        neg_score = sum(raw_scores.get(e, 0.0) for e in ["anger", "disgust", "fear", "sadness"])
        neu_score = raw_scores.get("neutral", 0.0)

        if pos_score > neg_score and (pos_score > 0.15 or pos_score > neu_score):
            sentiment_label = "positive"
        elif neg_score > pos_score and (neg_score > 0.15 or neg_score > neu_score):
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        return {
            "input_text": text,
            "sentiment": {
                "label": sentiment_label,
                "positive": round(pos_score, 4),
                "negative": round(neg_score, 4),
                "neutral": round(neu_score, 4)
            },
            "ekman": {
                "dominant": dominant_ekman,
                "scores": {k: round(v, 4) for k, v in ekman_scores.items()}
            },
            "plutchik": {
                "dominant": dominant_plutchik,
                "scores": {k: round(v, 4) for k, v in plutchik_scores.items()}
            }
        }

if __name__ == "__main__":
    analyzer = EmotionAnalyzer()
    samples = [
        "I am so excited and proud of what we have achieved today!",
        "I cannot believe they lied to me, this is completely unacceptable and infuriating.",
        "I'm terrified of what might happen next, everything feels so uncertain.",
        "The package arrived at 3 PM as scheduled."
    ]
    for sample in samples:
        print("=" * 60)
        output = analyzer.predict(sample)
        pprint.pprint(output)
