import spacy
from spacy.matcher import Matcher
import networkx as nx
from spacy.pipeline import EntityRuler


def example1():
    nlp = spacy.load("en_core_web_sm") 
    trf = spacy.load("en_core_web_trf")

    text = ("Timnit Gebru was unethically fired from her Ethical AI team. "
            "Later, she coauthored 'On the Dangers of Stochastic Parrots' with Bender and Mitchell.")

    doc = nlp(text)

    # entity extraction
    ents = [(e.text, e.label_) for e in doc.ents]

    # sentence segmentation
    sents = list(doc.sents)

    # conference resolution
    trf.add_pipe("coreferee")
    doc_trf = trf(text)
    chains = doc_trf._.coref_chains

    # Dependency parse to propose triples from SVO-like structures
    def triples_from_dep(sent):
        triples = []
        for token in sent:
            if token.dep_ in ("ROOT",) and token.pos_ == "VERB":
                subj = [w for w in token.lefts if w.dep_.startswith("nsubj")]
                dobj = [w for w in token.rights if w.dep_ in ("dobj", "attr", "pobj")]
                if subj and (dobj):
                    s = subj[0].text
                    o = dobj[0].text
                    r = token.lemma_
                    triples.append((s, r, o))
            # simple prepositional object pattern: "fired from team"
            if token.dep_ == "prep" and token.head.pos_ == "VERB":
                head = token.head
                pobj = [w for w in token.rights if w.dep_ == "pobj"]
                subj = [w for w in head.lefts if w.dep_.startswith("nsubj")]
                if subj and pobj:
                    triples.append((subj[0].text, f"{head.lemma_}_{token.text}", pobj[0].text))
        return triples

    triples_dep = []
    for s in sents:
        triples_dep += triples_from_dep(s)

    breakpoint()
    # 7) Pattern-based relation extraction (spaCy Matcher) for "X met Y", etc.
    matcher = Matcher(nlp.vocab)
    pattern_met = [
        {'POS': {'IN': ['PROPN','NOUN']}, 'OP': '+'},
        {'LEMMA': 'meet'},
        {'POS': {'IN': ['PROPN','NOUN']}, 'OP': '+'},
    ]
    matcher.add("MET_REL", [pattern_met])
    matches = matcher(doc)
    triples_pat = []
    for _, start, end in matches:
        span = doc[start:end]
        # naive split: assume "A met B"
        toks = [t for t in span if t.pos_ in ("PROPN","NOUN")]
        if len(toks) >= 2:
            triples_pat.append((toks[0].text, "met", toks[-1].text))

    # 8) Merge candidates, normalize lightly
    def norm(s): return s.strip().strip("''\"`.,;:").lower()
    kg_triples = {(norm(s), norm(r), norm(o)) for (s,r,o) in (triples_dep + triples_pat)}

    # 9) Build a tiny in-memory graph (networkx or your DB of choice)

    G = nx.DiGraph()
    for s,r,o in kg_triples:
        G.add_edge(s, o, relation=r)

    # 10) Query your mini-KG: "what did gebru get fired from?"
    answers = [(u,v,d['relation']) for u,v,d in G.edges(data=True)
            if u.startswith("timnit") and d['relation'].startswith("fire_from")]

def example2():
    nlp = spacy.load("en_core_web_sm")

    text = """Appropriates $500 million to the Department of Commerce for FY 2025 
    to modernize federal IT systems using AI and automation technologies."""
    doc = nlp(text)

    for token in doc:
        print(f"{token.text:<15} {token.dep_:<12} {token.head.text:<12} {token.pos_:<8}")

def example3(parser_type):

    # 1. Load spaCy English model (parser + tagger + lemmatizer)
    nlp = spacy.load("en_core_web_sm")

    # 2. Add your custom entity patterns
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    patterns = [
        {"label": "ORGANIZATION", "pattern": "Department of Commerce"},
        {"label": "ROLE", "pattern": "Secretary of Commerce"},
        {"label": "TECHNOLOGY", "pattern": "AI"},
        {"label": "TECHNOLOGY", "pattern": "automation technologies"},
        {"label": "SAFETY", "pattern": "cybersecurity"},
        {"label": "GOVERNMENT", "pattern": "state and local governments"},
        {"label": "REQUIREMENT", "pattern": "federally mandated"},
    ]
    ruler.add_patterns(patterns)

    # 3. Your document text
    text = """Appropriates $500 million to the Department of Commerce for FY 2025 to modernize federal IT systems using AI and automation technologies.
    Authorizes the Secretary of Commerce to use funds to replace legacy systems, adopt efficient AI models, and enhance cybersecurity with AI solutions.
    Enacts a 10-year moratorium preventing state and local governments from regulating AI models or systems.
    Exempts laws facilitating AI deployment or removing legal barriers, provided they do not impose additional requirements unless federally mandated or generally applicable."""

    doc = nlp(text)

    relations = []
    
    if parser_type == 'grammer':
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
    elif parser_type == 'position':            
        for sent in doc.sents:
            ents = [ent for ent in sent.ents]
            for i, subj in enumerate(ents):
                for obj in ents[i + 1:]:
                    # Find a governing verb between them
                    for token in sent:
                        if token.pos_ == "VERB":
                            if subj.start < token.i < obj.end or obj.start < token.i < subj.end:
                                relations.append((subj.text, token.lemma_, obj.text))

    elif parser_type == 'legal':
        for sent in doc.sents:
            for token in sent:
                if token.pos_ == "VERB":
                    # possible subjects and objects
                    subs = [w for w in token.lefts if w.dep_.startswith("nsubj")]
                    objs = [w for w in token.rights if w.dep_ in ("dobj", "attr", "pobj", "xcomp")]
                    # fallback: if no subject, assume the document or previous entity as implied actor
                    if not subs and objs:
                        subs = [w for w in sent if w.ent_type_ in ("ROLE", "ORGANIZATION", "GOVERNMENT")]
                    for s in subs:
                        for o in objs:
                            s_ent = [ent.text for ent in doc.ents if ent.start <= s.i <= ent.end]
                            o_ent = [ent.text for ent in doc.ents if ent.start <= o.i <= ent.end]
                            if s_ent and o_ent and s_ent[0] != o_ent[0]:
                                relations.append((s_ent[0], token.lemma_, o_ent[0]))

    print("Extracted Relations:")
    relations = list(set(relations))
    
    for r in relations:
        print(r)


if __name__ == "__main__":
    example3(parser_type='legal')