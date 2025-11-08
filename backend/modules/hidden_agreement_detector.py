"""
Hidden Agreement Detector Module
Identifies shared values and common ground between seemingly opposing viewpoints
"""

from typing import List, Dict, Any
from itertools import combinations

class HiddenAgreementDetector:
    """
    Detects hidden agreements between speakers based on:
    - Shared values
    - Similar Pramana (knowledge sources)
    - Compatible reasoning patterns
    """
    
    def __init__(self):
        """Initialize the detector"""
        self.agreement_threshold = 0.1  # Lower threshold to find more agreements
        
    def detect_agreements(
        self,
        analyses: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find hidden agreements between all pairs of speakers.
        
        Args:
            analyses: Dictionary mapping speaker names to their individual analyses
            
        Returns:
            List of detected agreements with details
        """
        agreements = []
        speakers = list(analyses.keys())
        
        # Check all pairs of speakers
        for person_a, person_b in combinations(speakers, 2):
            analysis_a = analyses[person_a]
            analysis_b = analyses[person_b]
            
            # Calculate agreement based on multiple factors
            shared_values = self._find_shared_values(analysis_a, analysis_b)
            pramana_similarity = self._compare_pramana(analysis_a, analysis_b)
            reasoning_compatibility = self._compare_reasoning(analysis_a, analysis_b)
            
            # Calculate overall agreement strength
            agreement_strength = self._calculate_agreement_strength(
                shared_values,
                pramana_similarity,
                reasoning_compatibility
            )
            
            # If agreement exists, add it
            if agreement_strength > self.agreement_threshold or len(shared_values) > 0:
                agreement = {
                    'person_a': person_a,
                    'person_b': person_b,
                    'shared_values': shared_values,
                    'agreement_strength': agreement_strength,
                    'pramana_similarity': pramana_similarity,
                    'reasoning_compatibility': reasoning_compatibility,
                    'dialogue_insight': self._generate_insight(
                        person_a, person_b,
                        shared_values,
                        analysis_a, analysis_b,
                        pramana_similarity
                    )
                }
                agreements.append(agreement)
        
        # Sort by agreement strength
        agreements.sort(key=lambda x: x['agreement_strength'], reverse=True)
        
        return agreements
    
    def _find_shared_values(
        self,
        analysis_a: Dict[str, Any],
        analysis_b: Dict[str, Any]
    ) -> List[str]:
        """Find values that both speakers share"""
        values_a = set(analysis_a.get('values', {}).get('top_values', []))
        values_b = set(analysis_b.get('values', {}).get('top_values', []))
        
        # Direct overlap
        shared = list(values_a & values_b)
        
        # Also check for related values (expanded matching)
        related_values = {
            'health_and_wellbeing': ['family_protection', 'community_wellbeing'],
            'economic_security': ['family_protection', 'community_wellbeing'],
            'justice_and_fairness': ['human_dignity', 'equality'],
            'community_wellbeing': ['family_protection', 'health_and_wellbeing'],
            'family_protection': ['health_and_wellbeing', 'economic_security']
        }
        
        for val_a in values_a:
            for val_b in values_b:
                if val_a in related_values.get(val_b, []) or val_b in related_values.get(val_a, []):
                    if val_a not in shared:
                        shared.append(val_a)
                    if val_b not in shared:
                        shared.append(val_b)
        
        return shared[:5]  # Return top 5 shared/related values
    
    def _compare_pramana(
        self,
        analysis_a: Dict[str, Any],
        analysis_b: Dict[str, Any]
    ) -> float:
        """Compare knowledge sources (Pramana) between speakers"""
        pramana_a = analysis_a.get('pramana', {}).get('dominant_pramana', '')
        pramana_b = analysis_b.get('pramana', {}).get('dominant_pramana', '')
        
        if not pramana_a or not pramana_b:
            return 0.3  # Default moderate similarity
        
        # Same pramana = high similarity
        if pramana_a == pramana_b:
            return 0.9
        
        # Compatible pramanas (different but complementary)
        compatible_pairs = [
            {'pratyaksha', 'anumana'},  # Experience + inference
            {'sabda', 'anumana'},       # Testimony + inference
            {'pratyaksha', 'sabda'}      # Experience + testimony
        ]
        
        for pair in compatible_pairs:
            if {pramana_a, pramana_b} == pair:
                return 0.6
        
        return 0.3  # Different approaches
    
    def _compare_reasoning(
        self,
        analysis_a: Dict[str, Any],
        analysis_b: Dict[str, Any]
    ) -> float:
        """Compare reasoning patterns"""
        # Check if both use structured reasoning
        reasoning_a = analysis_a.get('reasoning', {})
        reasoning_b = analysis_b.get('reasoning', {})
        
        has_chain_a = len(reasoning_a.get('chain', [])) > 0
        has_chain_b = len(reasoning_b.get('chain', [])) > 0
        
        if has_chain_a and has_chain_b:
            return 0.7  # Both use logical reasoning
        elif has_chain_a or has_chain_b:
            return 0.4  # One uses logical reasoning
        else:
            return 0.2  # Neither has clear reasoning chain
    
    def _calculate_agreement_strength(
        self,
        shared_values: List[str],
        pramana_similarity: float,
        reasoning_compatibility: float
    ) -> float:
        """
        Calculate overall agreement strength.
        
        Weighted formula:
        - Shared values: 60% weight
        - Pramana similarity: 25% weight
        - Reasoning compatibility: 15% weight
        """
        # Normalize shared values (0-1 scale)
        value_score = min(len(shared_values) / 3.0, 1.0)  # 3+ shared values = max
        
        # Weighted combination
        strength = (
            value_score * 0.6 +
            pramana_similarity * 0.25 +
            reasoning_compatibility * 0.15
        )
        
        return strength
    
    def _generate_insight(
        self,
        person_a: str,
        person_b: str,
        shared_values: List[str],
        analysis_a: Dict[str, Any],
        analysis_b: Dict[str, Any],
        pramana_similarity: float
    ) -> str:
        """Generate human-readable insight about the agreement"""
        
        if not shared_values:
            pramana_a = analysis_a.get('pramana', {}).get('dominant_pramana', 'different sources')
            pramana_b = analysis_b.get('pramana', {}).get('dominant_pramana', 'different sources')
            
            return (
                f"While {person_a} and {person_b} may disagree on policy, "
                f"they use similar epistemological approaches ({pramana_a} and {pramana_b}). "
                f"This suggests potential for productive dialogue if they can identify shared goals."
            )
        
        # Format shared values nicely
        if len(shared_values) == 1:
            values_str = shared_values[0].replace('_', ' ')
        elif len(shared_values) == 2:
            values_str = ' and '.join([v.replace('_', ' ') for v in shared_values])
        else:
            values_str = ', '.join([v.replace('_', ' ') for v in shared_values[:-1]]) + ', and ' + shared_values[-1].replace('_', ' ')
        
        # Get pramana info
        pramana_a = analysis_a.get('pramana', {}).get('dominant_pramana', 'unknown')
        pramana_b = analysis_b.get('pramana', {}).get('dominant_pramana', 'unknown')
        
        # Generate contextual insight
        if pramana_similarity > 0.7:
            pramana_insight = (
                f"Both primarily use {pramana_a} (same way of knowing), "
                f"so disagreement likely stems from different interpretations or priorities, not fundamental epistemology."
            )
        else:
            pramana_insight = (
                f"{person_a} relies on {pramana_a} while {person_b} uses {pramana_b}. "
                f"Bridging this gap could help them find common ground despite different reasoning approaches."
            )
        
        return (
            f"Both people value {values_str}, but reach different conclusions. "
            f"{pramana_insight} "
            f"A mediator could highlight their shared concern for {shared_values[0].replace('_', ' ')} "
            f"to build consensus on specific action steps."
        )
    
    def generate_dialogue_recommendations(
        self,
        agreements: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations based on detected agreements"""
        
        if not agreements:
            return [
                "No clear hidden agreements detected. Focus on establishing common ground.",
                "Try identifying shared experiences or concerns as a starting point.",
                "Consider using a neutral facilitator to explore potential areas of agreement."
            ]
        
        recommendations = []
        
        # Recommendation based on strongest agreement
        strongest = agreements[0]
        if strongest['agreement_strength'] > 0.6:
            recommendations.append(
                f"Strong agreement detected between {strongest['person_a']} and {strongest['person_b']}. "
                f"Build on their shared values: {', '.join(strongest['shared_values'][:2])}."
            )
        
        # Count total shared values
        all_shared_values = set()
        for agreement in agreements:
            all_shared_values.update(agreement['shared_values'])
        
        if len(all_shared_values) >= 3:
            recommendations.append(
                f"Multiple shared values detected across speakers: {', '.join(list(all_shared_values)[:3])}. "
                f"Frame discussion around these common concerns."
            )
        
        # Pramana-based recommendation
        high_pramana_similarity = [a for a in agreements if a['pramana_similarity'] > 0.6]
        if high_pramana_similarity:
            recommendations.append(
                f"{len(high_pramana_similarity)} speaker pair(s) use similar reasoning methods. "
                f"They may disagree on conclusions but share epistemological common ground."
            )
        
        # General recommendations
        if len(agreements) > 3:
            recommendations.append(
                "Multiple hidden agreements suggest this group has more common ground than apparent. "
                "Focus dialogue on shared values to find compromise solutions."
            )
        
        return recommendations


# Testing
if __name__ == "__main__":
    print("="*60)
    print("Hidden Agreement Detector Module Test")
    print("="*60)
    
    # Sample data
    test_analyses = {
        'Alice': {
            'pramana': {'dominant_pramana': 'pratyaksha'},
            'values': {'top_values': ['health_and_wellbeing', 'justice_and_fairness']},
            'reasoning': {'chain': [{'type': 'premise'}]}
        },
        'Bob': {
            'pramana': {'dominant_pramana': 'anumana'},
            'values': {'top_values': ['economic_security', 'community_wellbeing']},
            'reasoning': {'chain': []}
        }
    }
    
    detector = HiddenAgreementDetector()
    agreements = detector.detect_agreements(test_analyses)
    
    print(f"\n✓ Found {len(agreements)} hidden agreement(s)")
    
    for i, agreement in enumerate(agreements, 1):
        print(f"\nAgreement #{i}:")
        print(f"  Between: {agreement['person_a']} & {agreement['person_b']}")
        print(f"  Shared values: {agreement['shared_values']}")
        print(f"  Strength: {agreement['agreement_strength']:.2f}")
