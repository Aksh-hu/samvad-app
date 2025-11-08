"""
Pramana Classifier Module
Identifies epistemological sources in text
"""

import re
from typing import Dict, List

class PramanaClassifier:
    """
    Classifies text based on 4 Pramanas (ways of knowing)
    """
    
    def __init__(self):
        """Initialize with keyword patterns"""
        self.pramana_patterns = {
            'pratyaksha': [
                r'\bI (see|saw|witness|observe|watch|experience)\b',
                r'\bI have (seen|witnessed|observed|experienced)\b',
                r'\bin my experience\b',
                r'\bfirsthand\b',
                r'\bI was there\b',
                r'\bwith my own eyes\b'
            ],
            'anumana': [
                r'\btherefore\b',
                r'\bthus\b',
                r'\bhence\b',
                r'\bconsequently\b',
                r'\bit follows that\b',
                r'\bwe can infer\b',
                r'\bthis implies\b',
                r'\bif .+ then\b',
                r'\bbecause .+ must\b'
            ],
            'sabda': [
                r'\bstudies show\b',
                r'\bresearch (shows|indicates|proves)\b',
                r'\bexperts say\b',
                r'\baccording to\b',
                r'\bdata (shows|indicates)\b',
                r'\bevidence suggests\b',
                r'\bscientists (agree|found)\b',
                r'\bthe literature\b'
            ],
            'upamana': [
                r'\blike\b',
                r'\bsimilar to\b',
                r'\bjust as\b',
                r'\banalogous to\b',
                r'\bcompare to\b',
                r'\bresembles\b',
                r'\bin the same way\b'
            ]
        }
    
    def classify_pramana(self, text: str) -> Dict:
        """
        Classify the dominant pramana in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with dominant pramana and scores
        """
        text_lower = text.lower()
        scores = {pramana: 0 for pramana in self.pramana_patterns}
        
        # Count pattern matches
        for pramana, patterns in self.pramana_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                scores[pramana] += len(matches)
        
        # Find dominant
        if sum(scores.values()) == 0:
            dominant = 'pratyaksha'  # Default to direct perception
        else:
            dominant = max(scores, key=scores.get)
        
        return {
            'dominant_pramana': dominant,
            'scores': scores,
            'confidence': scores[dominant] / max(sum(scores.values()), 1)
        }


if __name__ == "__main__":
    print("Pramana Classifier Test")
    classifier = PramanaClassifier()
    
    test_text = "Studies show that exercise improves health. Therefore, we should promote fitness."
    result = classifier.classify_pramana(test_text)
    
    print(f"Dominant: {result['dominant_pramana']}")
    print(f"Scores: {result['scores']}")
