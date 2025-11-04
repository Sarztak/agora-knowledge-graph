import spacy

class RelationExtractor:
    def __init__(self, nlp):
        self.nlp = nlp
        # dictionary of available rule methods
        self.strategies = {
            'grammar': self.extract_grammar,
            'position': self.extract_position,
            'legal': self.extract_legal
        }

    def extract(self, text, parser_type='legal'):
        """Main entry point. Selects a parser strategy."""
        doc = self.nlp(text)
        if parser_type not in self.strategies:
            raise ValueError(f"Unknown parser type: {parser_type}")
        return sorted(list(set(self.strategies[parser_type](doc))))

    def extract_grammar(self, doc):
        relations = []
        for sent in doc.sents:
            for token in sent:
                if token.pos_ == "VERB":
                    subj = [w for w in token.lefts if w.dep_.startswith("nsubj")]
                    obj = [w for w in token.rights if w.dep_ in ("dobj", "attr", "pobj")]
                    if subj and obj:
                        subj_ent = [ent.text for ent in doc.ents if ent.start <= subj[0].i <= ent.end]
                        obj_ent = [ent.text for ent in doc.ents if ent.start <= obj[0].i <= ent.end]
                        if subj_ent and obj_ent:
                            relations.append((subj_ent[0], token.lemma_, obj_ent[0]))
        return relations

    def extract_position(self, doc):
        relations = []
        for sent in doc.sents:
            ents = [ent for ent in sent.ents]
            for i, subj in enumerate(ents):
                for obj in ents[i + 1:]:
                    for token in sent:
                        if token.pos_ == "VERB":
                            if subj.start < token.i < obj.end or obj.start < token.i < subj.end:
                                relations.append((subj.text, token.lemma_, obj.text))
        return relations

    def extract_legal(self, doc):
        relations = []
        for sent in doc.sents:
            for token in sent:
                if token.pos_ == "VERB":
                    subs = [w for w in token.lefts if w.dep_.startswith("nsubj")]
                    objs = [w for w in token.rights if w.dep_ in ("dobj", "attr", "pobj", "xcomp")]

                    # Fallbacks for missing subject or object
                    if not subs and objs:
                        subs = [w for w in sent if w.ent_type_ in ("ROLE", "ORGANIZATION", "GOVERNMENT")]
                    if subs and not objs:
                        objs = [w for w in sent if w.ent_type_ in ("TECHNOLOGY", "POLICY", "PROGRAM", "SAFETY")]

                    for s in subs:
                        for o in objs:
                            s_ent = [ent.text for ent in doc.ents if ent.start <= s.i <= ent.end]
                            o_ent = [ent.text for ent in doc.ents if ent.start <= o.i <= ent.end]
                            if s_ent and o_ent and s_ent[0] != o_ent[0]:
                                relations.append((s_ent[0], token.lemma_, o_ent[0]))
        return relations

    # You can easily add new rule sets here
    def add_strategy(self, name, func):
        """Register a new extraction rule dynamically."""
        self.strategies[name] = func.__get__(self)


if __name__ == "__main__":
    
    # Example usage:
    nlp = spacy.load("en_core_web_sm")
    ruler = nlp.add_pipe("entity_ruler", before="ner")

    entity_patterns = [
        {"label": "ORGANIZATION", "pattern": "Department of Commerce"},
        {"label": "ROLE", "pattern": "Secretary of Commerce"},
        {"label": "TECHNOLOGY", "pattern": "AI"},
        {"label": "TECHNOLOGY", "pattern": "automation technologies"},
        {"label": "SAFETY", "pattern": "cybersecurity"},
        {"label": "GOVERNMENT", "pattern": "state and local governments"},
        {"label": "REQUIREMENT", "pattern": "federally mandated"},
    ]

    text = """Appropriates $500 million to the Department of Commerce for FY 2025 to modernize federal IT systems using AI and automation technologies.
    Authorizes the Secretary of Commerce to use funds to replace legacy systems, adopt efficient AI models, and enhance cybersecurity with AI solutions.
    Enacts a 10-year moratorium preventing state and local governments from regulating AI models or systems.
    Exempts laws facilitating AI deployment or removing legal barriers, provided they do not impose additional requirements unless federally mandated or generally applicable."""

    ruler.add_patterns(entity_patterns)
    extractor = RelationExtractor(nlp)
    relations = extractor.extract(text, parser_type='legal')
    for r in relations:
        print(r)
