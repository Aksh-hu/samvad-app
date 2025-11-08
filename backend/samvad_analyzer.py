"""
SAMVAD Unified Analyzer
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'modules'))

from pramana_classifier import PramanaClassifier
from value_extractor import ValueExtractor
from tarka_engine import TarkaEngine
from hidden_agreement_detector import HiddenAgreementDetector

class SAMVADAnalyzer:
    
    def __init__(self):
        self.pramana_classifier = PramanaClassifier()
        self.value_extractor = ValueExtractor()
        self.tarka_engine = TarkaEngine()
        self.agreement_detector = HiddenAgreementDetector()
        
        print("SAMVAD Analyzer initialized with all modules.")
        print("- Pramana Classifier: Ready")
        print("- Value Extractor: Ready")
        print("- Tarka Engine: Ready")
        print("- Hidden Agreement Detector: Ready")
    
    def analyze_dialogue(self, narratives):
        individual_analyses = {}
        
        for narrative in narratives:
            speaker = narrative['speaker']
            text = narrative['text']
            
            pramana_result = self.pramana_classifier.classify_pramana(text)
            value_result = self.value_extractor.extract_values(text)
            reasoning_result = self.tarka_engine.analyze_reasoning(text)
            
            individual_analyses[speaker] = {
                'pramana': pramana_result,
                'values': value_result,
                'reasoning': reasoning_result,
                'text': text
            }
        
        hidden_agreements = self.agreement_detector.detect_agreements(individual_analyses)
        
        return {
            'individual_analyses': individual_analyses,
            'hidden_agreements': hidden_agreements,
            'narratives': narratives
        }
    
    def generate_report(self, results):
        report = []
        
        report.append("="*60)
        report.append("SAMVAD DIALOGUE ANALYSIS REPORT")
        report.append("="*60)
        report.append("")
        
        num_speakers = len(results['narratives'])
        num_agreements = len(results['hidden_agreements'])
        
        report.append(f"Total Speakers: {num_speakers}")
        report.append(f"Hidden Agreements Found: {num_agreements}")
        report.append(f"Dialogue Connections: {num_speakers * (num_speakers - 1) // 2}")
        report.append("")
        
        report.append("INDIVIDUAL NARRATIVE ANALYSIS")
        report.append("-"*60)
        report.append("")
        
        for speaker, analysis in results['individual_analyses'].items():
            report.append(f"{speaker}:")
            
            position = 'N/A'
            for narrative in results['narratives']:
                if narrative['speaker'] == speaker:
                    position = narrative['position']
                    break
            report.append(f"  Position: {position}")
            
            pramana = analysis['pramana'].get('dominant_pramana', 'unknown')
            report.append(f"  Knowledge Source: {pramana}")
            
            values = analysis['values'].get('top_values', [])
            if values:
                report.append(f"  Top Values: {', '.join(values[:3])}")
            else:
                report.append(f"  Top Values: ")
            
            report.append("")
        
        if results['hidden_agreements']:
            report.append("")
            report.append("HIDDEN AGREEMENTS DETECTED")
            report.append("-"*60)
            report.append("")
            
            for i, agreement in enumerate(results['hidden_agreements'], 1):
                report.append(f"Agreement #{i}:")
                report.append(f"  Between: {agreement['person_a']} ↔ {agreement['person_b']}")
                report.append(f"  Shared Values: {', '.join(agreement['shared_values']) if agreement['shared_values'] else 'None explicit'}")
                report.append(f"  Agreement Strength: {agreement['agreement_strength']:.0%}")
                report.append(f"  Insight: {agreement['dialogue_insight']}")
                report.append("")
        
        report.append("")
        report.append("DIALOGUE RECOMMENDATIONS")
        report.append("-"*60)
        report.append("")
        
        recommendations = self.agreement_detector.generate_dialogue_recommendations(
            results['hidden_agreements']
        )
        
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")
        
        report.append("")
        report.append("="*60)
        report.append("End of Report")
        report.append("="*60)
        
        return "\n".join(report)


if __name__ == "__main__":
    print("Testing SAMVAD Analyzer...")
    
    test_narratives = [
        {
            'speaker': 'Alice',
            'text': 'Studies show healthcare improves lives. Therefore we need reform.',
            'position': 'Pro healthcare reform'
        },
        {
            'speaker': 'Bob',
            'text': 'I have seen how markets drive innovation. My family depends on jobs.',
            'position': 'Pro market solutions'
        }
    ]
    
    analyzer = SAMVADAnalyzer()
    results = analyzer.analyze_dialogue(test_narratives)
    report = analyzer.generate_report(results)
    
    print("\n" + report)
