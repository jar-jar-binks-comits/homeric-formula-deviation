"""
Homeric Formula Vocabulary Builder
Automatically extracts repeated patterns around character names
and presents them for review and categorisation
"""

import json
from collections import Counter, defaultdict
import re

def load_analysis_results(filepath='homer_analysis.json'):
    """Load the results from phase 1"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_ngrams(text, n, position='all'):
    """
    Extract n-grams from text
    position: 'before', 'after', or 'all'
    """
    words = text.split()
    ngrams = []
    
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.append(ngram)
    
    return ngrams

def find_patterns_around_character(mentions, character_name, window_before=3, window_after=3):
    """
    For a specific character, find all repeated patterns before and after their name
    """
    patterns_before = []
    patterns_after = []
    
    for mention in mentions:
        if mention['character'] != character_name:
            continue
            
        line = mention['line'].lower()
        form = mention['form'].lower()
        
        # Find position of character name in line
        words = line.split()
        char_index = None
        
        for i, word in enumerate(words):
            if form in word:
                char_index = i
                break
        
        if char_index is None:
            continue
        
        # Extract words before
        start_before = max(0, char_index - window_before)
        before_words = words[start_before:char_index]
        if before_words:
            patterns_before.append(' '.join(before_words))
        
        # Extract words after
        end_after = min(len(words), char_index + window_after + 1)
        after_words = words[char_index+1:end_after]
        if after_words:
            patterns_after.append(' '.join(after_words))
    
    return patterns_before, patterns_after

def extract_repeated_bigrams_trigrams(patterns, min_frequency=3):
    """
    Find bigrams and trigrams that appear frequently
    """
    all_bigrams = []
    all_trigrams = []
    all_fourgrams = []
    
    for pattern in patterns:
        words = pattern.split()
        
        # Bigrams
        for i in range(len(words) - 1):
            all_bigrams.append(f"{words[i]} {words[i+1]}")
        
        # Trigrams
        for i in range(len(words) - 2):
            all_trigrams.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        # 4-grams
        for i in range(len(words) - 3):
            all_fourgrams.append(f"{words[i]} {words[i+1]} {words[i+2]} {words[i+3]}")
    
    bigram_freq = Counter(all_bigrams)
    trigram_freq = Counter(all_trigrams)
    fourgram_freq = Counter(all_fourgrams)
    
    # Filter by minimum frequency
    frequent_bigrams = {k: v for k, v in bigram_freq.items() if v >= min_frequency}
    frequent_trigrams = {k: v for k, v in trigram_freq.items() if v >= min_frequency}
    frequent_fourgrams = {k: v for k, v in fourgram_freq.items() if v >= min_frequency}
    
    return frequent_bigrams, frequent_trigrams, frequent_fourgrams

def find_formulaic_phrases_per_character(mentions):
    """
    For each character, extract their most common formulaic phrases
    """
    characters = set(m['character'] for m in mentions)
    character_formulae = {}
    
    for character in characters:
        print(f"\nAnalyzing formulae for {character}...")
        
        patterns_before, patterns_after = find_patterns_around_character(
            mentions, character, window_before=4, window_after=4
        )
        
        print(f"  Found {len(patterns_before)} 'before' patterns")
        print(f"  Found {len(patterns_after)} 'after' patterns")
        
        # Extract n-grams
        before_bi, before_tri, before_four = extract_repeated_bigrams_trigrams(patterns_before, min_frequency=3)
        after_bi, after_tri, after_four = extract_repeated_bigrams_trigrams(patterns_after, min_frequency=3)
        
        character_formulae[character] = {
            'patterns_before': {
                'bigrams': before_bi,
                'trigrams': before_tri,
                'fourgrams': before_four
            },
            'patterns_after': {
                'bigrams': after_bi,
                'trigrams': after_tri,
                'fourgrams': after_four
            },
            'total_mentions': len([m for m in mentions if m['character'] == character])
        }
    
    return character_formulae

def generate_formula_report(character_formulae, output_file='formula_report.txt'):
    """
    Generate a human-readable report of discovered formulae
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("HOMERIC FORMULAIC PATTERNS - AUTOMATIC EXTRACTION REPORT\n")
        f.write("="*80 + "\n\n")
        
        for character in sorted(character_formulae.keys()):
            data = character_formulae[character]
            
            f.write(f"\n{'='*80}\n")
            f.write(f"{character.upper()} - {data['total_mentions']} total mentions\n")
            f.write(f"{'='*80}\n")
            
            # Patterns BEFORE the name
            f.write("\n--- PATTERNS BEFORE NAME ---\n\n")
            
            if data['patterns_before']['fourgrams']:
                f.write("4-word phrases (most formulaic):\n")
                for phrase, count in sorted(data['patterns_before']['fourgrams'].items(), 
                                           key=lambda x: x[1], reverse=True):
                    f.write(f"  {count:3d}x  {phrase}\n")
            
            if data['patterns_before']['trigrams']:
                f.write("\n3-word phrases:\n")
                for phrase, count in sorted(data['patterns_before']['trigrams'].items(), 
                                           key=lambda x: x[1], reverse=True)[:15]:
                    f.write(f"  {count:3d}x  {phrase}\n")
            
            if data['patterns_before']['bigrams']:
                f.write("\n2-word phrases:\n")
                for phrase, count in sorted(data['patterns_before']['bigrams'].items(), 
                                           key=lambda x: x[1], reverse=True)[:15]:
                    f.write(f"  {count:3d}x  {phrase}\n")
            
            # Patterns AFTER the name
            f.write("\n--- PATTERNS AFTER NAME ---\n\n")
            
            if data['patterns_after']['fourgrams']:
                f.write("4-word phrases (most formulaic):\n")
                for phrase, count in sorted(data['patterns_after']['fourgrams'].items(), 
                                           key=lambda x: x[1], reverse=True):
                    f.write(f"  {count:3d}x  {phrase}\n")
            
            if data['patterns_after']['trigrams']:
                f.write("\n3-word phrases:\n")
                for phrase, count in sorted(data['patterns_after']['trigrams'].items(), 
                                           key=lambda x: x[1], reverse=True)[:15]:
                    f.write(f"  {count:3d}x  {phrase}\n")
            
            if data['patterns_after']['bigrams']:
                f.write("\n2-word phrases:\n")
                for phrase, count in sorted(data['patterns_after']['bigrams'].items(), 
                                           key=lambda x: x[1], reverse=True)[:15]:
                    f.write(f"  {count:3d}x  {phrase}\n")
            
            f.write("\n")
    
    print(f"\nReport saved to {output_file}")

def generate_interactive_review(character_formulae, mentions, output_file='formula_review_template.json'):
    """
    Generate a JSON template for manual review and categorization
    Format allows you to mark each formula as:
    - epithet_type: 'single_word', 'phrase', 'half_line'
    - semantic_category: 'physical', 'divine', 'martial', 'relational', etc.
    - confirmed: true/false
    """
    review_template = {}
    
    for character in sorted(character_formulae.keys()):
        data = character_formulae[character]
        
        # Collect all frequent patterns
        all_patterns = []
        
        # From before patterns
        for phrase, count in data['patterns_before']['fourgrams'].items():
            all_patterns.append({
                'pattern': phrase,
                'frequency': count,
                'position': 'before',
                'length': 4
            })
        for phrase, count in data['patterns_before']['trigrams'].items():
            all_patterns.append({
                'pattern': phrase,
                'frequency': count,
                'position': 'before',
                'length': 3
            })
        for phrase, count in data['patterns_before']['bigrams'].items():
            if count >= 5:  # Only include very frequent bigrams
                all_patterns.append({
                    'pattern': phrase,
                    'frequency': count,
                    'position': 'before',
                    'length': 2
                })
        
        # From after patterns
        for phrase, count in data['patterns_after']['fourgrams'].items():
            all_patterns.append({
                'pattern': phrase,
                'frequency': count,
                'position': 'after',
                'length': 4
            })
        for phrase, count in data['patterns_after']['trigrams'].items():
            all_patterns.append({
                'pattern': phrase,
                'frequency': count,
                'position': 'after',
                'length': 3
            })
        for phrase, count in data['patterns_after']['bigrams'].items():
            if count >= 5:
                all_patterns.append({
                    'pattern': phrase,
                    'frequency': count,
                    'position': 'after',
                    'length': 2
                })
        
        # Sort by frequency
        all_patterns.sort(key=lambda x: x['frequency'], reverse=True)
        
        # Create review entries
        review_entries = []
        for pattern_data in all_patterns:
            review_entries.append({
                'pattern': pattern_data['pattern'],
                'frequency': pattern_data['frequency'],
                'position': pattern_data['position'],
                'length': pattern_data['length'],
                # Fields for manual review:
                'confirmed': None,  # true/false - is this a real formula?
                'formula_type': None,  # 'epithet', 'verb_phrase', 'half_line', 'noise'
                'semantic_category': None,  # 'physical', 'divine', 'martial', 'speech', etc.
                'notes': ''
            })
        
        review_template[character] = {
            'total_mentions': data['total_mentions'],
            'patterns': review_entries
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(review_template, f, ensure_ascii=False, indent=2)
    
    print(f"Review template saved to {output_file}")
    print("\nYou can now:")
    print("1. Open this JSON file")
    print("2. Review each pattern and fill in the fields:")
    print("   - confirmed: true/false")
    print("   - formula_type: 'epithet', 'verb_phrase', 'half_line', 'noise'")
    print("   - semantic_category: describe the meaning")
    print("3. Save and we'll use this as our formula database")

def find_example_contexts(mentions, character, pattern, max_examples=5):
    """
    Find actual line examples where a pattern appears with a character
    """
    examples = []
    pattern_lower = pattern.lower()
    
    for mention in mentions:
        if mention['character'] == character:
            line_lower = mention['line'].lower()
            if pattern_lower in line_lower:
                examples.append({
                    'line_num': mention['line_num'],
                    'line': mention['line'],
                    'context': mention.get('context', mention['line'])
                })
                if len(examples) >= max_examples:
                    break
    
    return examples

if __name__ == "__main__":
    print("Homeric Formula Vocabulary Builder")
    print("="*80)
    print("\nThis script will:")
    print("1. Automatically extract repeated patterns around character names")
    print("2. Generate a readable report of formulaic phrases")
    print("3. Create a review template for you to categorize the formulae")
    print("="*80 + "\n")
    
    # Load previous analysis
    try:
        results = load_analysis_results('homer_analysis.json')
        mentions = results['all_mentions']
        print(f"Loaded {len(mentions)} character mentions from previous analysis\n")
    except FileNotFoundError:
        print("Error: homer_analysis.json not found.")
        print("Please run homeric_formula_analyser.py first!")
        exit(1)
    
    # Extract formulaic patterns
    print("Extracting formulaic patterns...")
    character_formulae = find_formulaic_phrases_per_character(mentions)
    
    # Generate outputs
    print("\nGenerating reports...")
    generate_formula_report(character_formulae, 'formula_report.txt')
    generate_interactive_review(character_formulae, mentions, 'formula_review_template.json')
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("\n1. Read 'formula_report.txt' to see all discovered patterns")
    print("2. Open 'formula_review_template.json'")
    print("3. Review each pattern and mark:")
    print("   - confirmed: true (it's a real formula) or false (it's noise)")
    print("   - formula_type: 'epithet', 'verb_phrase', 'half_line', etc.")
    print("   - semantic_category: what does it mean?")
    print("\n4. Once reviewed, we'll build Phase 2 using your confirmed formulae!")
    print("\nThis will give us a comprehensive, accurate formula database.")