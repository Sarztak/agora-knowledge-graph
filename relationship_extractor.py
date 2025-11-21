import spacy

class RelationExtractor:
    def __init__(self, nlp):
        self.nlp = nlp
        # dictionary of available rule methods
        self.strategies = {
            'grammar': self.extract_grammar,
            'position': self.extract_position,
            'legal': self.extract_legal,
            'child': self.extract_child,
            'free': self.extract_free,
        }

    def extract(self, text, parser_type='legal'):
        """main entry point. selects a parser strategy."""
        doc = self.nlp(text)
        if parser_type not in self.strategies:
            raise ValueError(f"unknown parser type: {parser_type}")
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

                    # fallbacks for missing subject or object
                    if not subs and objs:
                        subs = [w for w in sent if w.ent_type_ in ("ROLE", "ORGANIZATION", "GOVERNMENT")]
                    if subs and not objs:
                        objs = [w for w in sent if w.ent_type_ in ("TECHNOLOGY", "POLICY", "PROGRAM", "SAFETY")]
                    
                    for s in subs:
                        for o in objs: 
                            s_ent = [(ent.text, ent.label_) for ent in doc.ents if ent.start <= s.i <= ent.end]
                            o_ent = [(ent.text, ent.label_) for ent in doc.ents if ent.start <= o.i <= ent.end]
                            if s_ent and o_ent and s_ent[0] != o_ent[0]:
                                relations.append((s_ent[0], token.lemma_, o_ent[0]))
        return relations

    def extract_child(self, doc):

        def merge_entities_into_phrase(entities):
            # entities is a list of Ent objects
            # still experiemental
            if not entities:
                return None
            # convert each span to text
            parts = [ent.text for ent in entities]
            # join with ' and ' if multiple
            if len(parts) == 1:
                return parts[0]
            return " and ".join(parts)

        def get_governing_verb_and_role(ent):
            head = ent.root
            # if the head itself is a noun with a verb child, use that child
            if head.pos_ in ("NOUN", "PROPN"):
                for child in head.children:
                    if child.pos_ == "VERB" and child.dep_ in ("appos", "acl", "relcl"):
                        return child, "nsubj"  # treat the entity as subject
            # otherwise walk upward
            while head.pos_ != "VERB" and head != head.head:
                head = head.head
            if head.pos_ == "VERB":
                return head, ent.root.dep_
            return None, None


        subj_deps = {"nsubj", "nsubjpass"}
        obj_deps  = {"dobj", "pobj", "attr", "obl", "xcomp", "ccomp"}

        triplets = []
        for sent in doc.sents:
            sent_entities = [ent for ent in doc.ents if sent.start <= ent.start < sent.end]
            verb_roles = {token: {"subj": [], "obj": []} for token in sent if token.pos_ == 'VERB'}
            _vr = [get_governing_verb_and_role(ent) for ent in sent_entities]
    

            for ent in sent_entities:
                verb, role = get_governing_verb_and_role(ent)
                if verb not in verb_roles:
                    continue

                if role in subj_deps:
                    verb_roles[verb]["subj"].append(ent)
                elif role in obj_deps:
                    verb_roles[verb]["obj"].append(ent)


            for verb, roles in verb_roles.items():
                for s in roles["subj"]:
                    for o in roles["obj"]:
                        triplets.append((s.text, verb.lemma_, o.text))
        return triplets

    def extract_free(self, doc):
        relations = []        
        entity_spans = list(doc.ents)

        # Extend entity spans with noun chunks not already covered
        known_span_set = {(ent.start, ent.end) for ent in entity_spans}
        for np in doc.noun_chunks:
            if (np.start, np.end) not in known_span_set:
                entity_spans.append(np)


        def collect_direct_objects_only(verb_token, entity_spans):
            """Collect only the DIRECT objects of this specific verb, not subordinate clauses"""
            collected = []
            visited = set()

            def walk(t):
                if t.i in visited:
                    return
                visited.add(t.i)

                # Check if in entity
                in_entity = False
                for ent in entity_spans:
                    if ent.start <= t.i < ent.end:
                        collected.append(ent.text)
                        in_entity = True
                        break
                
                # For nouns, get full noun phrase with left modifiers
                if not in_entity and t.pos_ in ("NOUN", "PROPN") and not t.is_stop:
                    phrase_tokens = [t]
                    for left_child in t.lefts:
                        if left_child.dep_ in ("amod", "compound"):
                            phrase_tokens.insert(0, left_child)
                    
                    phrase = " ".join([tok.text for tok in phrase_tokens])
                    collected.append(phrase)

                # Traverse right, but STOP at subordinate verbs
                for child in t.rights:
                    if child.pos_ == "VERB" and child.dep_ in ("acl", "xcomp", "ccomp", "relcl"):
                        continue  
                    walk(child)

            walk(verb_token)
            return list(set(collected))



        for sent in doc.sents:
            for token in sent:
                if token.pos_ == "VERB":
                    
                    # Find the subject for this verb
                    if token.dep_ == "ROOT":
                        # Root verb: look for nsubj on the left
                        subs = [w for w in token.lefts if w.dep_.startswith("nsubj")]
                        if subs:
                            subj_text = None
                            for ent in entity_spans:
                                if ent.start <= subs[0].i < ent.end:
                                    subj_text = ent.text
                                    break
                            if not subj_text:
                                subj_text = subs[0].text
                        else:
                            subj_text = "LAW_NAME"
                    
                    elif token.dep_ in ("acl", "relcl"):
                        # Subordinate clause: subject is what this verb modifies (its head)
                        subj_text = None
                        for ent in entity_spans:
                            if ent.start <= token.head.i < ent.end:
                                subj_text = ent.text
                                break
                        if not subj_text:
                            # Build noun phrase for the head
                            phrase_tokens = [token.head]
                            for left_child in token.head.lefts:
                                if left_child.dep_ in ("amod", "compound"):
                                    phrase_tokens.insert(0, left_child)
                            subj_text = " ".join([tok.text for tok in phrase_tokens])
                    
                    elif token.dep_ in ("xcomp", "ccomp"):
                        # Complement clause: subject is the subject of the main verb
                        subj_text = None
                        main_verb = token.head
                        subs = [w for w in main_verb.lefts if w.dep_.startswith("nsubj")]
                        if subs:
                            for ent in entity_spans:
                                if ent.start <= subs[0].i < ent.end:
                                    subj_text = ent.text
                                    break
                            if not subj_text:
                                subj_text = subs[0].text
                        else:
                            subj_text = "LAW_NAME"
                    else:
                        continue  # Skip other verb types
                    
                    # Get objects for this verb
                    obj_entities = collect_direct_objects_only(token, entity_spans)
                    for obj in obj_entities:
                        if subj_text != obj:
                            relations.append((subj_text, token.lemma_, obj))

        return list(set(relations))

    # you can easily add new rule sets here
    def add_strategy(self, name, func):
        """register a new extraction rule dynamically."""
        self.strategies[name] = func.__get__(self)


if __name__ == "__main__":
    
    # example usage:
    nlp = spacy.load("en_core_web_sm")
    ruler = nlp.add_pipe("entity_ruler", before="ner")

    entity_patterns = [
        {"label": "organization", "pattern": "department of commerce"},
        {"label": "role", "pattern": "secretary of commerce"},
        {"label": "technology", "pattern": "ai"},
        {"label": "technology", "pattern": "automation technologies"},
        {"label": "safety", "pattern": "cybersecurity"},
        {"label": "government", "pattern": "state and local governments"},
        {"label": "requirement", "pattern": "federally mandated"},
    ]

    text = """appropriates $500 million to the department of commerce for fy 2025 to modernize federal it systems using ai and automation technologies.
    authorizes the secretary of commerce to use funds to replace legacy systems, adopt efficient ai models, and enhance cybersecurity with ai solutions.
    enacts a 10-year moratorium preventing state and local governments from regulating ai models or systems.
    exempts laws facilitating ai deployment or removing legal barriers, provided they do not impose additional requirements unless federally mandated or generally applicable."""

    ruler.add_patterns(entity_patterns)
    extractor = RelationExtractor(nlp)
    relations = extractor.extract(text, parser_type='legal')
    for r in relations:
        print(r)
