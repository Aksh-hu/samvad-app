"""
Value Extractor Module
Identifies core values in text
"""

import re
from typing import Dict, List

class ValueExtractor:
    """
    Extracts human values from text
    """
    
    def __init__(self):
        """Initialize with value keywords"""
        self.value_keywords = {
            'justice_and_fairness': [
                'justice', 'fair', 'fairness', 'equal', 'equality', 'rights',
                'deserve', 'ought', 'should', 'moral', 'ethical', 'unjust'
            ],
            'health_and_wellbeing': [
                'health', 'wellbeing', 'wellness', 'care', 'medical', 'hospital',
                'patient', 'illness', 'disease', 'treatment', 'safety'
            ],
            'economic_security': [
                'job', 'employment', 'economy', 'economic', 'business', 'income',
                'financial', 'money', 'wage', 'salary', 'afford', 'cost'
            ],
            'family_protection': [
                'family', 'children', 'kids', 'parents', 'home', 'household',
                'father', 'mother', 'son', 'daughter', 'protect'
            ],
            'community_wellbeing': [
                'community', 'society', 'neighbor', 'local', 'town', 'city',
                'people', 'citizens', 'public', 'collective'
            ],
            'progress_and_innovation': [
                'innovation', 'progress', 'technology', 'future', 'advance',
                'develop', 'improve', 'growth', 'modern', 'new'
            ],
            'freedom_and_autonomy': [
                'freedom', 'liberty', 'choice', 'autonomy', 'independent',
                'free', 'choose', 'decide', 'control'
            ]
        }
    
    def extract_values(self, text: str) -> Dict:
        """
        Extract values from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with top values and scores
        """
        text_lower = text.lower()
        scores = {value: 0 for value in self.value_keywords}
        
        # Count keyword matches
        for value, keywords in self.value_keywords.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\w*\b'
                matches = re.findall(pattern, text_lower)
                scores[value] += len(matches)
        
        # Sort by score
        sorted_values = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_values = [v for v, s in sorted_values if s > 0][:5]
        
        return {
            'top_values': top_values,
            'scores': scores
        }


if __name__ == "__main__":
    print("Value Extractor Test")
    extractor = ValueExtractor()
    
    test_text = "Healthcare is a human right. Families deserve access to medical treatment."
    result = extractor.extract_values(test_text)
    
    print(f"Top values: {result['top_values']}")
