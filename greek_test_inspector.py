"""
Quick diagnostic to see what the Greek text actually looks like
"""
import xml.etree.ElementTree as ET

def inspect_xml(filepath='iliad_book1.xml'):
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Get first 10 lines
    line_elements = root.findall('.//tei:l', ns)
    if not line_elements:
        line_elements = root.findall('.//l')
    
    print("="*70)
    print("SAMPLE OF GREEK TEXT (First 10 lines)")
    print("="*70)
    
    for i, line_elem in enumerate(line_elements[:10], 1):
        line_num = line_elem.get('n', '')
        line_text = ''.join(line_elem.itertext()).strip()
        print(f"\nLine {line_num}:")
        print(f"  Text: {line_text}")
        print(f"  Length: {len(line_text)} characters")
        
        # Show first few characters in detail
        if line_text:
            print(f"  First word: {line_text.split()[0] if line_text.split() else 'EMPTY'}")
            print(f"  Unicode codepoints (first 20 chars):")
            for j, char in enumerate(line_text[:20]):
                print(f"    [{j}] {char} = U+{ord(char):04X}")
    
    # Search for Achilles in various forms
    print("\n" + "="*70)
    print("SEARCHING FOR ACHILLES...")
    print("="*70)
    
    achilles_forms = ['Ἀχιλλεύς', 'Ἀχιλλῆος', 'Ἀχιλλῆι', 'Ἀχιλλέα', 'Ἀχιλεῦ', 
                      'Αχιλλεύς', 'Αχιλλῆος', 'Αχιλλῆι', 'Αχιλλέα', 'Αχιλεῦ',  # without breathing
                      'Αχιλλευς', 'Αχιλληος', 'Αχιλλει', 'Αχιλλεα', 'Αχιλλευ']  # no accents
    
    found_count = 0
    for line_elem in line_elements[:100]:  # Check first 100 lines
        line_text = ''.join(line_elem.itertext()).strip()
        line_num = line_elem.get('n', '')
        
        for form in achilles_forms:
            if form in line_text:
                print(f"\nFound '{form}' in line {line_num}:")
                print(f"  {line_text}")
                found_count += 1
                break
    
    if found_count == 0:
        print("No Achilles forms found in first 100 lines.")
        print("\nLet's check what names ARE in the text...")
        print("\nSearching for common Greek words:")
        
        test_words = [
            ('μῆνιν', 'wrath - first word of Iliad'),
            ('θεά', 'goddess'),
            ('Ἀχαιῶν', 'Achaeans'),
            ('μηνιν', 'wrath - no accents'),
            ('θεα', 'goddess - no accents'),
            ('Αχαιων', 'Achaeans - no accents'),
        ]
        
        for word, description in test_words:
            for line_elem in line_elements[:10]:
                line_text = ''.join(line_elem.itertext()).strip()
                if word in line_text:
                    print(f"\n  Found '{word}' ({description})")
                    print(f"    {line_text}")
                    break

if __name__ == "__main__":
    inspect_xml('iliad_book1.xml')