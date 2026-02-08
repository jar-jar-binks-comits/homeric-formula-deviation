"""
Homeric Formulaic Pattern Analyzer
Phase 1: Extract and analyze character epithets in Iliad

This script:
1. Fetches the Greek text of Iliad (in Beta Code from Perseus)
2. Identifies character names and their contexts
3. Extracts epithets and formulaic patterns
4. Builds frequency distributions
"""

import re
from collections import defaultdict, Counter
import json
import xml.etree.ElementTree as ET

# Key characters to track (in Beta Code format)
# Beta Code uses: * for capitals, ) for smooth breathing, ( for rough, / for acute, etc.
CHARACTERS = {
    'Achilles': [
        '*)axilleu/s', '*)axilh=os', '*)axilh=i', '*)axille/a', 
        '*)axilleu=', '*)axileu=', '*)axilh=',
        'a)xilleu/s', 'a)xilh=os', 'a)xilh=i', 'a)xille/a'  # lowercase variants
    ],
    'Agamemnon': [
        '*a)game/mnwn', '*a)game/mnoni', '*a)game/mnona',
        'a)game/mnwn', 'a)game/mnoni', 'a)game/mnona'
    ],
    'Hector': [
        '*(/ektwr', '*e(/ktoros', '*e(/ktori', '*e(/ktora',
        'e(/ktwr', 'e(/ktoros', 'e(/ktori', 'e(/ktora'
    ],
    'Odysseus': [
        '*o)dusse/u/s', '*o)dussh=os', '*o)dussh=i', '*o)dussh=a',
        'o)dusse/u/s', 'o)dussh=os', 'o)dussh=i', 'o)dussh=a'
    ],
    'Patroclus': [
        '*pa/troklos', '*patro/klou', '*patro/klw|', '*pa/troklon',
        'pa/troklos', 'patro/klou', 'patro/klw|', 'pa/troklon'
    ],
    'Zeus': [
        '*zeu/s', '*dio/s', '*dii/', '*di/a',
        'zeu/s', 'dio/s', 'dii/', 'di/a'
    ],
    'Athena': [
        '*a)qh/nh', '*a)qh/nhs', '*a)qh/nh|', '*a)qh/nhn',
        'a)qh/nh', 'a)qh/nhs', 'a)qh/nh|', 'a)qh/nhn'
    ],
    'Apollo': [
        '*a)po/llwn', '*a)po/llwnos', '*a)po/llwni', '*a)po/llwna',
        'a)po/llwn', 'a)po/llwnos', 'a)po/llwni', 'a)po/llwna'
    ]
}

# Common epithets in Beta Code
KNOWN_EPITHETS = [
    'poda/rkhs',  # swift-footed
    'po/das w)ku/s',  # swift-footed (different form)
    'diogenh/s',  # Zeus-born
    'di=os',  # divine/noble
    'krei/wn',  # lord/ruler
    'mega/qumos',  # great-hearted
    'polu/mhtis',  # of many counsels
    'glaukw=pis',  # gleaming-eyed
    'e(khbo/los',  # far-shooter
    'a)/nac a)ndrw=n',  # lord of men
    'koruqai/olos',  # of the glancing helmet
    'ptoli/porqos',  # sacker of cities
    'podi/=s w)ku\s',  # swift-footed alt
]

def load_text_from_xml(filepath='iliad_book1.xml'):
    """
    Load Greek text from Perseus XML file (Beta Code format)
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # Perseus uses TEI namespace
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        
        lines = []
        
        # Try with namespace first
        line_elements = root.findall('.//tei:l', ns)
        
        # If no namespace, try without
        if not line_elements:
            line_elements = root.findall('.//l')
        
        print(f"Found {len(line_elements)} line elements in XML")
        
        for line_elem in line_elements:
            line_num = line_elem.get('n', '')
            line_text = ''.join(line_elem.itertext()).strip()
            if line_text:
                lines.append({
                    'num': line_num,
                    'text': line_text
                })
        
        return lines, 'structured'
        
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return None, None
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None, None

def normalize_beta_code(text):
    """Basic normalisation - lowercase for easier matching"""
    return text.lower()

def find_character_mentions(line_data):
    """
    Find character mentions in a line (Beta Code format)
    Returns list of mention dictionaries
    """
    line = line_data['text']
    line_num = line_data['num']
    line_lower = normalize_beta_code(line)
    
    mentions = []
    for char_name, forms in CHARACTERS.items():
        for form in forms:
            form_lower = normalize_beta_code(form)
            if form_lower in line_lower:
                mentions.append({
                    'character': char_name,
                    'form': form,
                    'line_num': line_num,
                    'line': line
                })
                break  # Only count each character once per line
    return mentions

def extract_context_window(line, character_form, window=5):
    """
    Extract words around the character mention
    window: number of words before and after
    """
    words = line.split()
    form_lower = normalize_beta_code(character_form)
    
    for i, word in enumerate(words):
        if form_lower in normalize_beta_code(word):
            start = max(0, i - window)
            end = min(len(words), i + window + 1)
            context = words[start:end]
            return ' '.join(context)
    return line

def find_epithets_in_context(context, known_epithets):
    """Check if any known epithets appear in the context"""
    context_lower = normalize_beta_code(context)
    found = []
    for epithet in known_epithets:
        epithet_lower = normalize_beta_code(epithet)
        if epithet_lower in context_lower:
            found.append(epithet)
    return found

def analyze_text(data):
    """
    Main analysis function
    """
    all_mentions = []
    epithet_frequency = Counter()
    character_epithet_pairs = defaultdict(list)
    character_line_numbers = defaultdict(list)
    
    print(f"\nAnalyzing {len(data)} lines...")
    
    for line_data in data:
        mentions = find_character_mentions(line_data)
        
        for mention in mentions:
            context = extract_context_window(
                mention['line'], 
                mention['form'], 
                window=5
            )
            
            epithets = find_epithets_in_context(context, KNOWN_EPITHETS)
            
            mention['context'] = context
            mention['epithets'] = epithets
            
            all_mentions.append(mention)
            
            # Track frequencies
            for epithet in epithets:
                epithet_frequency[epithet] += 1
                character_epithet_pairs[mention['character']].append(epithet)
            
            # Track which lines each character appears in
            character_line_numbers[mention['character']].append(mention['line_num'])
    
    return all_mentions, epithet_frequency, character_epithet_pairs, character_line_numbers

def print_results(all_mentions, epithet_frequency, character_epithet_pairs, character_line_numbers):
    """Print analysis results"""
    
    print("\n" + "="*70)
    print("FORMULAIC PATTERN ANALYSIS - ILIAD")
    print("="*70)
    
    print(f"\nTotal character mentions found: {len(all_mentions)}")
    
    print("\n--- CHARACTER APPEARANCE COUNTS ---")
    for character in sorted(character_line_numbers.keys()):
        count = len(character_line_numbers[character])
        print(f"{character}: {count} mentions")
    
    if epithet_frequency:
        print("\n--- MOST COMMON EPITHETS ---")
        for epithet, count in epithet_frequency.most_common(10):
            print(f"{epithet}: {count} times")
    else:
        print("\n--- NO EPITHETS DETECTED YET ---")
        print("This is normal! We need to expand the KNOWN_EPITHETS list.")
        print("Let's look at actual contexts to discover the formulaic patterns...")
    
    print("\n--- CHARACTER-EPITHET ASSOCIATIONS ---")
    for character, epithets in character_epithet_pairs.items():
        if epithets:
            epithet_counts = Counter(epithets)
            print(f"\n{character}:")
            for epithet, count in epithet_counts.most_common():
                print(f"  {epithet}: {count} times")
    
    print("\n--- SAMPLE MENTIONS WITH CONTEXT (First 20) ---")
    for i, mention in enumerate(all_mentions[:20], 1):
        print(f"\n{i}. Line {mention['line_num']}: {mention['character']}")
        print(f"   Form: {mention['form']}")
        print(f"   Context: {mention['context']}")
        if mention['epithets']:
            print(f"   Epithets: {', '.join(mention['epithets'])}")

def save_results_to_json(all_mentions, epithet_frequency, character_epithet_pairs, 
                         character_line_numbers, filename='homer_analysis.json'):
    """Save results to JSON for further analysis"""
    
    results = {
        'total_mentions': len(all_mentions),
        'all_mentions': all_mentions,
        'epithet_frequency': dict(epithet_frequency),
        'character_epithet_pairs': {k: list(v) for k, v in character_epithet_pairs.items()},
        'character_line_numbers': {k: v for k, v in character_line_numbers.items()}
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    print("Homeric Formulaic Pattern Analyzer")
    print("===================================\n")
    
    # Load XML file
    data, file_type = load_text_from_xml('iliad_book1.xml')
    
    if data is None:
        print("\nError: Could not load iliad_book1.xml")
    else:
        print(f"Successfully loaded {len(data)} lines from XML")
        
        all_mentions, epithet_freq, char_epithet, char_lines = analyze_text(data)
        print_results(all_mentions, epithet_freq, char_epithet, char_lines)
        save_results_to_json(all_mentions, epithet_freq, char_epithet, char_lines)
        
        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)
        print("1. Review the contexts where characters appear")
        print("2. Identify common epithets in Beta Code format")
        print("3. Add those epithets to KNOWN_EPITHETS list")
        print("4. Re-run to see epithet-character patterns")
        print("5. Then build the deviation detection system")