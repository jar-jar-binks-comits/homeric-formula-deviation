# Homeric Formula Deviation Detection

**Computational Analysis of Pattern-Breaking at Narrative Climaxes in the Iliad**

*An ongoing research project exploring how Homer uses formulaic deviations as cognitive markers for narrative significance.*

---

## 🎯 Project Overview

This project applies **information-theoretic analysis** to detect deviations from formulaic patterns in Homer's *Iliad*, testing the hypothesis that pattern-breaking serves as a cognitive marker for narrative significance.

### Research Question
Does Homer deliberately break formulaic patterns at emotionally significant moments, exploiting predictive processing to mark narrative importance? Is this analogous to how Dante deploys distinctive sound patterns (like Beatrice's *-ice* rhyme) in unexpected contexts?

### Current Status: **In Progress** 🚧
- ✅ Phase 1: Formula extraction complete
- ✅ Phase 2: Vocabulary building complete  
- ✅ Phase 3: Deviation detection functional
- ✅ Phase 4: Interactive visualization working
- 🔄 **Ongoing**: Expanding formula catalogue, refining annotations, analyzing Book-level patterns
- 📝 **Next**: Metrical analysis, rhythm patterns, cross-book comparisons

---

## 💡 Inspiration & Theoretical Background

### The Dante Connection
This project was inspired by a pattern in Dante's *Inferno* Canto V (Francesca's episode). In that canto about forbidden love, Dante never explicitly names Beatrice—yet her presence is felt through sound. Notice the *-ice* rhyme pattern:

> *"Nessun maggior dolore  
> che ricordarsi del tempo fel**ice**  
> ne la miseria..."*
>
> *"Ma s'a conoscer la prima rad**ice**  
> del nostro amor tu hai cotanto affetto,  
> dirò come colui che piange e d**ice**."*

This *-ice* rhyme is distinctively associated with Beatrice throughout the *Commedia*. Its appearance in Francesca's speech about illicit love creates a subliminal echo—pattern recognition working at the phonological level. The audience *feels* Beatrice's presence through sound alone.

**Question**: Does Homer do something similar? When he breaks an established formulaic pattern, does the deviation itself carry meaning?

### Key Influences

**On Oral Poetry & Formulae:**
- **Leonard Muellner** - *Homer's Living Language: Formularity, Dialect, and Creativity in Oral-Traditional Poetry* (ongoing reference for understanding formulaic flexibility)
- **Milman Parry** & **Albert Lord** - Foundational oral-formulaic theory
- The role of rhythm and sound in persuasion and memory

**On Greek Language & Sound:**
- **Geoffrey Horrocks** - *Greek: A History of the Language and Its Speakers* (linguistic context)
- **Marc Lauxtermann** - *Rhetoric and Rhythm in Byzantium: The Sound of Persuasion* (rhythm's cognitive role in Greek literature)
- Byzantine and Medieval Greek prosody traditions

**On Predictive Processing:**
- **Andy Clark** - Predictive brain theories
- **Roger Levy** - Expectation-based comprehension
- Information theory in cognitive science

---

## 🧠 Theoretical Framework

**Predictive Processing Hypothesis**: When audiences expect formula X but encounter Y (or nothing), the prediction error creates cognitive salience. This might be a cross-cultural pattern:
- **Homer**: Formulaic deviations at Hector's death, armor exchanges
- **Dante**: Sound pattern deviations (Beatrice rhyme in "wrong" context)

**Method**: 
- **Surprisal** = -log₂(P(formula|context))
- High surprisal → unexpected → cognitively salient
- Hypothesis: Correlates with narrative significance

---

## 📊 Preliminary Results

From analysis of the *Iliad* (work in progress):
- **581 character mentions** analyzed across 15,683 lines
- **23.1% deviation rate** detected
- **Hector's death scene** (line 355): 4.34 bits surprisal
  - Formula: *kataqnh/|skwn prose/fh koruqai/olos* ("dying, spoke helmet-glancing")
  - Appears only at death scenes
- **Armor formulae**: 6.07 bits surprisal (1.49% probability)
  - *ge teu/xe' e)/xei koruqai/olos* ("has the armor")
  - Context: Patroclus wearing Achilles's armor (leads to his death)

**Note**: These are preliminary findings. Further analysis needed to establish robust correlations between high-surprisal moments and narrative structure.

---

## 🛠️ Technical Implementation

### Phase 1: Formula Extraction
**Script**: `homeric_formula_analyser.py`

- Parses Perseus Digital Library XML (Beta Code format)
- Identifies character mentions in all grammatical forms
- Extracts formulaic patterns (epithets, speech formulae, patronymics)
- Outputs: `homer_analysis.json`

### Phase 2: Formula Vocabulary Building
**Script**: `formula_vocabulary_builder.py` + `formula_review_assistant.py`

- Automatic n-gram extraction (bigrams, trigrams, 4-grams)
- Frequency analysis of patterns around character names
- Interactive categorization interface
- Outputs: `formulae_database.json`, `formula_report.txt`

### Phase 3: Deviation Detection
**Script**: `deviation_detection_engine.py`

- Calculates base probabilities P(formula | character)
- Computes information-theoretic surprisal
- Identifies high-surprisal moments
- Outputs: `deviation_analysis.json`, `deviation_report.txt`

### Phase 4: Interactive Visualization
**File**: `homeric_visualization.html`

- Browser-based scatter plot (line × surprisal)
- Narrative event markers
- Character filtering
- Click for detailed analysis

---

## 🚀 Usage

### Requirements
```bash
pip install lxml  # For XML parsing (optional)
```

### Quick Start
```bash
# 1. Extract character mentions
python homeric_formula_analyser.py

# 2. Build formula vocabulary
python formula_vocabulary_builder.py
python formula_review_assistant.py

# 3. Detect deviations
python deviation_detection_engine.py

# 4. Visualize (open in browser)
# Load deviation_analysis.json in homeric_visualization.html
```

---

## 📁 Project Structure

```
homeric-formula-deviation/
├── README.md
├── homeric_formula_analyser.py      # Phase 1: Extract formulae
├── formula_vocabulary_builder.py     # Phase 2: Build vocabulary
├── formula_review_assistant.py       # Phase 2: Review tool
├── deviation_detection_engine.py     # Phase 3: Detect deviations
├── homeric_visualization.html        # Phase 4: Visualization
├── iliad_book1.xml                   # Input: Greek text (Beta Code)
└── [generated files]                 # JSON outputs, reports
```

---

## 🔍 Current Findings (Preliminary)

### Character Patterns

**Achilles** (206 mentions):
- 6.8% deviation rate (highly formulaic consistency)
- Common: *prose/fh po/das w)ku\s* (28×) - speech introduction
- Rare: *poda/rkhs di=os* at specific moments (3.88 bits)

**Hector** (202 mentions):
- 18.8% deviation rate (more variable)
- Common: *me/gas koruqai/olos* (12×)
- Death scene: unique formula (4.34 bits)

### Questions for Further Research
1. Do deviations cluster at specific narrative moments (deaths, recognitions, turning points)?
2. Is there a relationship between metrical irregularity and formulaic deviation?
3. How do Book-level patterns differ (e.g., battle books vs. council scenes)?
4. Can we predict narrative significance from surprisal scores alone?

---

## 🔮 Next Steps

**Immediate (Current Work)**:
- [ ] Expand formula catalogue (currently ~40 confirmed formulae)
- [ ] Add narrative event annotations across all 24 Books
- [ ] Correlate with metrical analysis
- [ ] Test on *Odyssey* for comparison

**Future Directions**:
- [ ] Cross-linguistic analysis (Vedic Sanskrit, Old English)
- [ ] Neural language models trained on formulaic poetry
- [ ] Rhythm and sound pattern analysis (building on Lauxtermann)
- [ ] Computational analysis of Dante's sound patterns (test the *-ice* rhyme hypothesis)

---

## 📚 Key References

### Primary Texts
- Homer, *Iliad* (Greek text from Perseus Digital Library)
- Dante Alighieri, *Divina Commedia* (Inferno V - Francesca episode)

### Oral-Formulaic Theory
- Muellner, L. (2022). *Homer's Living Language: Formularity, Dialect, and Creativity in Oral-Traditional Poetry*
- Parry, M. (1971). *The Making of Homeric Verse*
- Lord, A. B. (1960). *The Singer of Tales*

### Greek Language & Sound
- Horrocks, G. (2010). *Greek: A History of the Language and Its Speakers* (2nd ed.)
- Lauxtermann, M. D. (2019). *Rhetoric and Rhythm in Byzantium: The Sound of Persuasion*

### Predictive Processing & Information Theory
- Clark, A. (2013). "Whatever next? Predictive brains, situated agents, and the future of cognitive science." *Behavioral and Brain Sciences*, 36(3)
- Levy, R. (2008). "Expectation-based syntactic comprehension." *Cognition*, 106(3)
- Shannon, C. E. (1948). "A Mathematical Theory of Communication." *Bell System Technical Journal*

---

## 🙏 Acknowledgments

**Huge thanks to:**
- **The Perseus Digital Library** - For making Ancient Greek texts freely accessible and computationally usable. This project would not exist without Perseus. Their commitment to open-access classical scholarship is inspiring.
- **The CLTK community** - Classical Language Toolkit resources

**Personal Inspiration:**
- Dante's *Inferno* V - for showing how pattern-breaking carries meaning:

    Ma dimmi: al tempo d'i dolci sospiri,
    a che e come concedette amore
    che conosceste i dubbiosi disiri?».
    E quella a me: «Nessun maggior dolore 
    che ricordarsi del tempo felice
    ne la miseria; e ciò sa 'l tuo dottore.
    Ma s'a conoscer la prima radice
    del nostro amor tu hai cotanto affetto,
    dirò come colui che piange e dice.

- The oral poets who created these patterns we're now computationally detecting

---

## 🤝 Contributing

This is an active research project. Contributions, suggestions, and extensions welcome:
- Additional formula identification
- Narrative event annotations
- Metrical analysis integration
- Cross-linguistic applications
- Bug reports and code improvements

Open an issue or pull request!

---

## 📧 Contact

**Author**: Ella Capellini  
**Interests**: Digital Humanities, Psycholinguistics, Computational Philology, Computational Auditory, Ancient Greek  
**GitHub**: github.com/jar-jar-binks-comits

---

## 📄 License

MIT License - Feel free to use this methodology for research. Citation appreciated if you build on this work.

---

## 📊 How to Cite (if using this work)

```bibtex
@software{capellini_homeric_2024,
  author = {Capellini, Ella},
  title = {Homeric Formula Deviation Detection: Computational Analysis of Pattern-Breaking in the Iliad},
  year = {2025},
  note = {Work in progress},
  url = {https://github.com/jar-jar-binks-comits/homeric-formula-deviation}
}
```

---

*"μῆνιν ἄειδε θεὰ Πηληϊάδεω Ἀχιλῆος"*  
*Sing, goddess, the wrath of Achilles... but notice when Homer breaks the song.*

---

**Status**: 🚧 Active Development | Last Updated: December 2024