import spacy
from spacy.matcher import Matcher
import networkx as nx
from spacy.pipeline import EntityRuler
from pathlib import Path

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

    # 9) Build a tiny in-memory graph (networkx or  DB of choice)

    G = nx.DiGraph()
    for s,r,o in kg_triples:
        G.add_edge(s, o, relation=r)

    # 10) Query  mini-KG: "what did gebru get fired from?"
    answers = [(u,v,d['relation']) for u,v,d in G.edges(data=True)
            if u.startswith("timnit") and d['relation'].startswith("fire_from")]

def example2():
    nlp = spacy.load("en_core_web_sm")

    text = """Appropriates $500 million to the Department of Commerce for FY 2025 
    to modernize federal IT systems using AI and automation technologies."""
    doc = nlp(text)

    for token in doc:
        print(f"{token.text:<15} {token.dep_:<12} {token.head.text:<12} {token.pos_:<8}")

if __name__ == "__main__":
    # example1()
    # example2()
    pass 


