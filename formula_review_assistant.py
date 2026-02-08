"""
Interactive Formula Review Assistant
Guides you through categorising formulaic patterns
"""

import json
from collections import defaultdict

def load_review_template(filepath='formula_review_template.json'):
    """Load the auto-generated template"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_reviewed_formulae(data, filepath='formulae_database.json'):
    """Save the reviewed and categorized formulae"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Saved to {filepath}")

def categorize_batch_patterns():
    """
    Batch categorization based on pattern recognition
    This pre-fills obvious categories to save time
    """
    
    template = load_review_template()
    
    # Define automatic categorisation rules
    rules = {
        'speech_formula': {
            'keywords': ['prose/fh', 'prose/eipe', 'a)pameibo/menos', 'fwnh/sas'],
            'type': 'speech_formula',
            'category': 'narrative - speech introduction or response'
        },
        'epithet_only': {
            'keywords': ['poda/rkhs', 'di=os', 'koruqai/olos', 'nefelhgere/ta', 'mega/qumos', 'fai/dimos'],
            'type': 'epithet',
            'category': 'character epithet'
        },
        'emotional_state': {
            'keywords': ['o)xqh/sas', 'xolwqei/s', 'gh/qhsen'],
            'type': 'verb_phrase',
            'category': 'emotional state or reaction'
        },
        'patronymic': {
            'keywords': ['*phlhi+a/dew', '*priami/dhs', 'ui(o/s'],
            'type': 'patronymic',
            'category': 'patronymic or genealogical'
        }
    }
    
    stats = defaultdict(int)
    
    for character, data in template.items():
        for pattern in data['patterns']:
            pattern_text = pattern['pattern'].lower()
            
            # Apply rules
            categorized = False
            for rule_name, rule in rules.items():
                if any(keyword in pattern_text for keyword in rule['keywords']):
                    if pattern['confirmed'] is None:  # Only auto-fill if not manually set
                        pattern['confirmed'] = True
                        pattern['formula_type'] = rule['type']
                        pattern['semantic_category'] = rule['category']
                        stats[rule_name] += 1
                        categorized = True
                        break
            
            if not categorized:
                stats['needs_review'] += 1
    
    print("\n" + "="*70)
    print("AUTO-CATEGORIZATION RESULTS")
    print("="*70)
    for category, count in sorted(stats.items()):
        print(f"{category}: {count} patterns")
    
    return template, stats

def interactive_review_remaining(template):
    """
    Interactive review for patterns that couldn't be auto-categorised
    """
    
    print("\n" + "="*70)
    print("INTERACTIVE REVIEW - Patterns Needing Manual Review")
    print("="*70)
    print("\nFor each pattern, decide:")
    print("  [y] Yes, it's a real formula")
    print("  [n] No, it's noise/not meaningful")
    print("  [s] Skip for now")
    print("  [q] Quit and save")
    print("="*70 + "\n")
    
    for character, data in template.items():
        uncategorized = [p for p in data['patterns'] if p['confirmed'] is None]
        
        if not uncategorized:
            continue
        
        print(f"\n{'='*70}")
        print(f"{character.upper()} - {len(uncategorized)} patterns to review")
        print(f"{'='*70}\n")
        
        for i, pattern in enumerate(uncategorized, 1):
            print(f"\nPattern {i}/{len(uncategorized)}:")
            print(f"  Text: {pattern['pattern']}")
            print(f"  Frequency: {pattern['frequency']}x")
            print(f"  Position: {pattern['position']} the character name")
            print(f"  Length: {pattern['length']} words")
            
            choice = input("\n  Is this a real formula? [y/n/s/q]: ").strip().lower()
            
            if choice == 'q':
                print("\nSaving progress and exiting...")
                return template
            elif choice == 's':
                continue
            elif choice == 'y':
                pattern['confirmed'] = True
                
                print("\n  What type of formula?")
                print("    1. epithet (character description)")
                print("    2. speech_formula (introduces speech)")
                print("    3. verb_phrase (action/state)")
                print("    4. half_line (longer formulaic phrase)")
                print("    5. patronymic (genealogy/family)")
                print("    6. other")
                
                type_choice = input("  Choose [1-6]: ").strip()
                type_map = {
                    '1': 'epithet',
                    '2': 'speech_formula',
                    '3': 'verb_phrase',
                    '4': 'half_line',
                    '5': 'patronymic',
                    '6': 'other'
                }
                pattern['formula_type'] = type_map.get(type_choice, 'other')
                
                meaning = input("  Brief description of meaning: ").strip()
                pattern['semantic_category'] = meaning if meaning else 'to be defined'
                
                print("  ✓ Saved")
                
            elif choice == 'n':
                pattern['confirmed'] = False
                pattern['formula_type'] = 'noise'
                pattern['semantic_category'] = 'not a meaningful formula'
                print("  ✓ Marked as noise")
    
    return template

def generate_clean_formula_database(template):
    """
    Generate , confirmed-only formula database
    Organised by character and formula type
    """
    
    database = {}
    
    for character, data in template.items():
        confirmed_patterns = [p for p in data['patterns'] if p.get('confirmed') == True]
        
        if not confirmed_patterns:
            continue
        
        # Organise by formula type
        by_type = defaultdict(list)
        for pattern in confirmed_patterns:
            formula_entry = {
                'pattern': pattern['pattern'],
                'frequency': pattern['frequency'],
                'position': pattern['position'],
                'semantic_category': pattern.get('semantic_category', ''),
                'notes': pattern.get('notes', '')
            }
            by_type[pattern['formula_type']].append(formula_entry)
        
        database[character] = {
            'total_mentions': data['total_mentions'],
            'formulae_by_type': dict(by_type),
            'total_confirmed_formulae': len(confirmed_patterns)
        }
    
    return database

def print_summary_statistics(database):
    """Print summary statistics of the formula database"""
    
    print("\n" + "="*70)
    print("FORMULA DATABASE SUMMARY")
    print("="*70)
    
    total_formulae = 0
    for character, data in database.items():
        print(f"\n{character}:")
        print(f"  Total mentions in Iliad: {data['total_mentions']}")
        print(f"  Confirmed formulae: {data['total_confirmed_formulae']}")
        
        for formula_type, patterns in data['formulae_by_type'].items():
            print(f"    {formula_type}: {len(patterns)} patterns")
            total_formulae += len(patterns)
    
    print(f"\n{'='*70}")
    print(f"TOTAL CONFIRMED FORMULAE: {total_formulae}")
    print(f"{'='*70}")

if __name__ == "__main__":
    print("Interactive Formula Review Assistant")
    print("="*70)
    
    # Step 1: Auto-categorise obvious patterns
    print("\nStep 1: Automatic categorization of obvious patterns...")
    template, stats = categorize_batch_patterns()
    
    # Ask if you want interactive review
    print("\n" + "="*70)
    if stats['needs_review'] > 0:
        print(f"\n{stats['needs_review']} patterns need manual review.")
        do_review = input("\nDo you want to review them interactively now? [y/n]: ").strip().lower()
        
        if do_review == 'y':
            template = interactive_review_remaining(template)
    else:
        print("\n✓ All patterns have been auto-categorized!")
    
    # Step 2: Generate clean database
    print("\nStep 2: Generating clean formula database...")
    database = generate_clean_formula_database(template)
    
    # Step 3: Save both versions
    save_reviewed_formulae(template, 'formula_review_complete.json')
    save_reviewed_formulae(database, 'formulae_database.json')
    
    # Step 4: Print summary
    print_summary_statistics(database)
    
    print("\n" + "="*70)
    print("FILES CREATED:")
    print("="*70)
    print("1. formula_review_complete.json - Full review with all details")
    print("2. formulae_database.json - Clean, confirmed formulae only")
    print("\nYou can now use formulae_database.json for Phase 2!")
    print("="*70)