"""
Tarka Engine Module
Traces logical reasoning chains
"""

import re
from typing import Dict, List

class TarkaEngine:
    """
    Analyzes logical reasoning structure
    """
    
    def __init__(self):
        """Initialize with reasoning patterns"""
        self.reasoning_patterns = {
            'premise': [
                r'\b(because|since|given that|as)\b',
                r'\bthe fact (that|is)\b'
            ],
            'inference': [
                r'\b(therefore|thus|hence|consequently)\b',
                r'\bit follows that\b',
                r'\bthis (means|implies)\b'
            ],
            'evidence': [
                r'\b(studies|research|data|evidence) (show|suggest|indicate)\b',
                r'\baccording to\b'
            ],
            'conclusion': [
                r'\b(in conclusion|ultimately|finally)\b',
                r'\bwe (must|should|need to)\b'
            ]
        }
    
    def analyze_reasoning(self, text: str) -> Dict:
        """
        Analyze reasoning structure.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with reasoning chain
        """
        text_lower = text.lower()
        chain = []
        
        # Find reasoning elements
        for element_type, patterns in self.reasoning_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    chain.append({
                        'type': element_type,
                        'position': match.start(),
                        'text': match.group()
                    })
        
        # Sort by position
        chain.sort(key=lambda x: x['position'])
        
        return {
            'chain': chain,
            'has_logical_structure': len(chain) > 0
        }


if __name__ == "__main__":
    print("Tarka Engine Test")
    engine = TarkaEngine()
    
    test_text = "Because healthcare costs are rising, therefore we need reform."
    result = engine.analyze_reasoning(test_text)
    
    print(f"Chain length: {len(result['chain'])}")
    print(f"Has structure: {result['has_logical_structure']}")
