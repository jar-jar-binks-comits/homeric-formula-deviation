"""
Homeric Formula Deviation Detection Engine - Phase 2

This system:
1. Loads confirmed formulae database
2. Analyses each character mention
3. Determines expected formula based on context
4. Detects deviations (unexpected formulae or absences)
5. Calculates surprisal scores
6. Maps deviations to narrative structure
"""

import json
import math
from collections import defaultdict, Counter
import re

def load_formula_database(filepath='formulae_database.json'):
    """Load the confirmed formulae database"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_mentions(filepath='homer_analysis.json'):
    """Load all character mentions from Phase 1"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['all_mentions']

def build_formula_patterns(database):
    """
    Build searchable formula patterns from database
    Returns dict: character -> list of formula patterns
    """
    patterns = {}
    
    for character, data in database.items():
        character_patterns = []
        
        for formula_type, formulae in data['formulae_by_type'].items():
            for formula in formulae:
                pattern_lower = formula['pattern'].lower()
                character_patterns.append({
                    'pattern': pattern_lower,
                    'original': formula['pattern'],
                    'type': formula_type,
                    'position': formula['position'],
                    'frequency': formula['frequency'],
                    'semantic': formula.get('semantic_category', '')
                })
        
        patterns[character] = character_patterns
    
    return patterns

def detect_formulae_in_mention(mention, formula_patterns):
    """
    Check which formulae (if any) appear in this mention
    Returns list of detected formulae
    """
    character = mention['character']
    line_lower = mention['line'].lower()
    
    if character not in formula_patterns:
        return []
    
    detected = []
    for formula in formula_patterns[character]:
        if formula['pattern'] in line_lower:
            detected.append(formula)
    
    return detected

def calculate_formula_expectations(mentions, formula_patterns, database):
    """
    For each character, calculate:
    - Base rate of each formula (P(formula | character))
    - Contextual rates (P(formula | character, context))
    """
    
    expectations = {}
    
    for character in formula_patterns.keys():
        char_mentions = [m for m in mentions if m['character'] == character]
        total_mentions = len(char_mentions)
        
        # Count formula occurrences
        formula_counts = Counter()
        
        for mention in char_mentions:
            detected = detect_formulae_in_mention(mention, formula_patterns)
            for formula in detected:
                formula_counts[formula['pattern']] += 1
        
        # Calculate base probabilities
        formula_probs = {}
        for pattern, count in formula_counts.items():
            formula_probs[pattern] = count / total_mentions if total_mentions > 0 else 0
        
        expectations[character] = {
            'total_mentions': total_mentions,
            'formula_counts': dict(formula_counts),
            'formula_probabilities': formula_probs
        }
    
    return expectations

def calculate_surprisal(probability):
    """
    Calculate information-theoretic surprisal
    Surprisal = -log2(P(event))
    Higher surprisal = more unexpected
    """
    if probability == 0:
        return float('inf')
    return -math.log2(probability)

def analyze_mention_surprisal(mention, formula_patterns, expectations):
    """
    Analyse a single mention:
    - What formulae are present?
    - What's the expected formula?
    - What's the surprisal?
    """
    character = mention['character']
    
    if character not in expectations:
        return None
    
    detected = detect_formulae_in_mention(mention, formula_patterns)
    
    # Case 1: No formula detected (bare mention)
    if not detected:
        # Calculate probability of bare mention
        total = expectations[character]['total_mentions']
        formula_count = sum(expectations[character]['formula_counts'].values())
        bare_count = total - formula_count
        bare_prob = bare_count / total if total > 0 else 0
        
        return {
            'mention': mention,
            'detected_formulae': [],
            'type': 'bare_mention',
            'probability': bare_prob,
            'surprisal': calculate_surprisal(bare_prob) if bare_prob > 0 else float('inf'),
            'is_deviation': bare_prob < 0.3  # Less than 30% of mentions are bare
        }
    
    # Case 2: Formula(e) detected
    # Use most frequent formula if multiple detected
    primary_formula = max(detected, key=lambda f: f['frequency'])
    formula_prob = expectations[character]['formula_probabilities'].get(
        primary_formula['pattern'], 0
    )
    
    return {
        'mention': mention,
        'detected_formulae': detected,
        'primary_formula': primary_formula,
        'type': 'formulaic',
        'probability': formula_prob,
        'surprisal': calculate_surprisal(formula_prob) if formula_prob > 0 else float('inf'),
        'is_deviation': formula_prob < 0.1  # Rare formula (less than 10% usage)
    }

def find_deviations(mentions, formula_patterns, expectations):
    """
    Analyze all mentions and find deviations
    Returns list of mentions with high surprisal
    """
    analyses = []
    
    for mention in mentions:
        analysis = analyze_mention_surprisal(mention, formula_patterns, expectations)
        if analysis:
            analyses.append(analysis)
    
    return analyses

def identify_high_surprisal_moments(analyses, surprisal_threshold=3.0):
    """
    Find moments with high surprisal (deviations from expected patterns)
    Surprisal > 3.0 means probability < 12.5%
    """
    high_surprisal = [a for a in analyses if a['surprisal'] > surprisal_threshold]
    high_surprisal.sort(key=lambda x: x['surprisal'], reverse=True)
    
    return high_surprisal

def generate_deviation_report(analyses, high_surprisal, database, output_file='deviation_report.txt'):
    """
    Generate comprehensive deviation analysis report
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("HOMERIC FORMULA DEVIATION ANALYSIS\n")
        f.write("Detecting Moments Where Homer Breaks Formulaic Patterns\n")
        f.write("="*80 + "\n\n")
        
        # Overall statistics
        total_mentions = len(analyses)
        formulaic = len([a for a in analyses if a['type'] == 'formulaic'])
        bare = len([a for a in analyses if a['type'] == 'bare_mention'])
        deviations = len([a for a in analyses if a.get('is_deviation', False)])
        
        f.write("OVERALL STATISTICS:\n")
        f.write(f"  Total character mentions analyzed: {total_mentions}\n")
        f.write(f"  Formulaic mentions: {formulaic} ({formulaic/total_mentions*100:.1f}%)\n")
        f.write(f"  Bare mentions (no formula): {bare} ({bare/total_mentions*100:.1f}%)\n")
        f.write(f"  Identified deviations: {deviations} ({deviations/total_mentions*100:.1f}%)\n\n")
        
        # High surprisal moments
        f.write("="*80 + "\n")
        f.write(f"HIGH SURPRISAL MOMENTS (Top {min(50, len(high_surprisal))})\n")
        f.write("These are moments where Homer's formula usage is most unexpected\n")
        f.write("="*80 + "\n\n")
        
        for i, analysis in enumerate(high_surprisal[:50], 1):
            mention = analysis['mention']
            f.write(f"\n{i}. Line {mention['line_num']}: {mention['character']}\n")
            f.write(f"   Surprisal: {analysis['surprisal']:.2f} bits\n")
            f.write(f"   Probability: {analysis['probability']*100:.2f}%\n")
            
            if analysis['type'] == 'bare_mention':
                f.write(f"   Type: BARE MENTION (no formula)\n")
            else:
                f.write(f"   Formula used: {analysis['primary_formula']['original']}\n")
                f.write(f"   Formula type: {analysis['primary_formula']['type']}\n")
                f.write(f"   Semantic: {analysis['primary_formula']['semantic']}\n")
            
            f.write(f"   Line: {mention['line']}\n")
            
            # Context hint
            if 'context' in mention:
                f.write(f"   Context: {mention['context']}\n")
        
        # By character breakdown
        f.write("\n" + "="*80 + "\n")
        f.write("DEVIATIONS BY CHARACTER\n")
        f.write("="*80 + "\n\n")
        
        for character in database.keys():
            char_analyses = [a for a in analyses if a['mention']['character'] == character]
            char_deviations = [a for a in char_analyses if a.get('is_deviation', False)]
            
            if char_analyses:
                f.write(f"\n{character}:\n")
                f.write(f"  Total mentions: {len(char_analyses)}\n")
                f.write(f"  Deviations: {len(char_deviations)} ({len(char_deviations)/len(char_analyses)*100:.1f}%)\n")
                
                # Show top 3 most surprising for this character
                char_high = sorted(char_analyses, key=lambda x: x['surprisal'], reverse=True)[:3]
                f.write(f"  Most surprising moments:\n")
                for ca in char_high:
                    f.write(f"    Line {ca['mention']['line_num']}: surprisal {ca['surprisal']:.2f}\n")
    
    print(f"\n✓ Deviation report saved to {output_file}")

def save_deviation_data(analyses, high_surprisal, output_file='deviation_analysis.json'):
    """Save deviation analysis data as JSON for further processing"""
    
    # Convert to serialisable format
    serializable_analyses = []
    for analysis in analyses:
        entry = {
            'line_num': analysis['mention']['line_num'],
            'character': analysis['mention']['character'],
            'line': analysis['mention']['line'],
            'type': analysis['type'],
            'probability': analysis['probability'],
            'surprisal': analysis['surprisal'] if analysis['surprisal'] != float('inf') else 999,
            'is_deviation': analysis.get('is_deviation', False)
        }
        
        if analysis['type'] == 'formulaic':
            entry['detected_formulae'] = [f['original'] for f in analysis['detected_formulae']]
            entry['primary_formula'] = analysis['primary_formula']['original']
        
        serializable_analyses.append(entry)
    
    data = {
        'all_analyses': serializable_analyses,
        'high_surprisal_count': len(high_surprisal),
        'high_surprisal_threshold': 3.0
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Deviation data saved to {output_file}")

if __name__ == "__main__":
    print("Homeric Formula Deviation Detection Engine - Phase 2")
    print("="*80 + "\n")
    
    # Load data
    print("Loading formula database...")
    database = load_formula_database('formulae_database.json')
    
    print("Loading character mentions...")
    mentions = load_mentions('homer_analysis.json')
    
    print(f"Loaded {len(mentions)} mentions across {len(database)} characters\n")
    
    # Build formula patterns
    print("Building formula patterns...")
    formula_patterns = build_formula_patterns(database)
    
    # Calculate expectations
    print("Calculating formula expectations...")
    expectations = calculate_formula_expectations(mentions, formula_patterns, database)
    
    # Analyse all mentions
    print("Analyzing all mentions for deviations...")
    analyses = find_deviations(mentions, formula_patterns, expectations)
    
    # Find high surprisal moments
    print("Identifying high surprisal moments...")
    high_surprisal = identify_high_surprisal_moments(analyses, surprisal_threshold=3.0)
    
    print(f"\nFound {len(high_surprisal)} high surprisal moments\n")
    
    # Generate reports
    print("Generating deviation report...")
    generate_deviation_report(analyses, high_surprisal, database, 'deviation_report.txt')
    save_deviation_data(analyses, high_surprisal, 'deviation_analysis.json')
    
    print("\n" + "="*80)
    print("PHASE 2 COMPLETE!")
    print("="*80)
    print("\nFiles created:")
    print("  1. deviation_report.txt - Human-readable analysis")
    print("  2. deviation_analysis.json - Data for visualization/further analysis")
    print("\nNext: Phase 3 will map these deviations to narrative structure")
    print("(deaths, recognitions, turning points, emotional climaxes)")
    print("="*80)