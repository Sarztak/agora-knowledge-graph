import pandas as pd 
import os 
from pathlib import Path
import json
from rich.traceback import install 
import pandas as pd
import numpy as np
import spacy 
from entity_remapping import *
from collections import defaultdict
from relationship_extractor import RelationExtractor

install()

def map_doc_id_to_agora_id(path):
    """Add doc_index column which maps to AGORA Document ID and return a new df. This is used to map the extracted entities to the document from which they were extracted"""

    docs_df = (
        pd.read_csv(path)
        .rename(columns={'Long summary': 'long_summary'})
        .dropna(subset='long_summary')
    )
    
    docs_df['doc_index'] = [f"{str(i + 1).zfill(3)}" for i in range(len(docs_df))]
    
    return docs_df

def tabulate_extracted_entities():
    """Save the extracted entities pattern and label as a tabular data in a parquet format"""
    docs_path = Path('./data/documents.csv')
    docs_df = map_doc_id_to_agora_id(docs_path)
    output = Path('output')
    ent_label_list = []
    for i, filename in enumerate(os.listdir(output)):
        # if i == 2: break
        if not filename.endswith('.json'):
            continue
        try:
            with open(output / filename, 'r', encoding='utf-8') as file:
                docs_entities = json.load(file)
                for ent_dict in docs_entities:
                    doc_index = ent_dict.get('document_id').split('_')[1]
                    entity_list = ent_dict.get('entities')
                    ent_label_df = pd.DataFrame(entity_list)
                    ent_label_df['doc_index'] = doc_index
                    ent_label_list.append(ent_label_df)
        except json.JSONDecodeError as e:
            print(f"{e}: Something wrong with file: {filename}")
            break
    ent_label_df = pd.concat(ent_label_list)
    
    doc_idx1 = set(docs_df.doc_index.values)
    doc_idx2 = set(ent_label_df.doc_index.values)
    flag_idx = doc_idx1.difference(doc_idx2)
    assert len(flag_idx) == 0 # check if all the doc index match exactly
    ent_label_df = ent_label_df[['doc_index', 'label', 'pattern']]
    ent_label_df = pd.merge(
        ent_label_df,
        docs_df[['doc_index', 'AGORA ID']],
        on='doc_index',
        how='left'
    )[['doc_index', 'AGORA ID', 'label', 'pattern']]

    ent_label_df.to_parquet(output / 'entity_label.parquet')

def extract_dependency(row, nlp):
    name = f"ruler_{row['doc_index']}"
    ruler = nlp.add_pipe("entity_ruler", before="ner", name=name)
    ruler.add_patterns(row['patterns'])
    extractor = RelationExtractor(nlp)
    doc = nlp(row['long_summary'])
    rels = extractor.extract(doc, parser_type='legal') 
    nlp.remove_pipe(name)           # remove to keep pipeline clean
    del extractor                   # clean up memory
    return rels

def create_ner_list(df):
    return [[{'label': row['label'], 'pattern': row['pattern']} for _, row in df.iterrows()], df['long_summary'].iloc[0]]

def tabular_extracted_dependency():
    # Load spaCy model
    nlp = spacy.load("en_core_web_sm")

    # Load data
    docs_df = pd.read_csv('./data/documents.csv')
    docs_df.rename(columns={'Long summary': 'long_summary'}, inplace=True)

    ent_df = pd.read_parquet('./output/entity_label.parquet')

    # Merge entity and document data
    ent_docs_df = pd.merge(ent_df, docs_df, on='AGORA ID', how='inner')

    # Create NER pattern list
    ent_list_df = (
        ent_docs_df
        .groupby('doc_index')
        .apply(lambda df: create_ner_list(df), include_groups=False)
        .reset_index()
    )

    # Unpack NER output into separate columns
    ent_list_df[['patterns', 'long_summary']] = pd.DataFrame(
        ent_list_df[0].tolist(), index=ent_list_df.index
    )
    ent_list_df.drop(columns=0, inplace=True)

    # Extract dependencies
    ent_list_df['dependency'] = ent_list_df.apply(
        lambda row: extract_dependency(row, nlp), axis=1
    )

    # Flatten dependencies
    dep_df = ent_list_df[['doc_index', 'dependency']].explode('dependency')
    dep_df[['sub', 'verb', 'obj']] = pd.DataFrame(
        dep_df['dependency'].tolist(), index=dep_df.index
    )
    dep_df.drop(columns='dependency', inplace=True)
    dep_df.replace({None: np.nan}, inplace=True)

    # Merge back AGORA ID
    dep_df = pd.merge(
        dep_df,
        ent_docs_df[['AGORA ID', 'doc_index']].drop_duplicates(),
        on='doc_index',
        how='left'
    )[['doc_index', 'AGORA ID', 'sub', 'verb', 'obj']]

    # Save output
    dep_df.to_parquet('output/dependency.parquet')

def prompt():
    return """
SYSTEM ROLE
You are an expert NER annotator specializing in labeling regulatory and policy documents using a predefined taxonomy.
Follow every instruction exactly — do not generate Python code or pseudocode.
Your sole task is to read the provided documents, match entities according to the taxonomy below, and return a single JSON file with the labeled output.

Entity Tag Schema - Listed below. Each tag defines an allowed entity type and its description.

ENTITY TAG SCHEMA
ORGANIZATION    Agencies, companies, bodies, institutions
ROLE            People, positions, officers, officials
LAW             Formal legislation, acts, statutes
POLICY          Guidelines, frameworks, executive orders
STANDARD        Technical standards, protocols
REQUIREMENT     Specific obligations, mandates
PROGRAM         Initiatives, projects, pilot programs
TECHNOLOGY      Systems, platforms, tools, models
DOCUMENT        Reports, records, assessments, inventories
GEOGRAPHIC      Locations, jurisdictions, regions
PRIVACY         Data protection, confidentiality, personal information
FAIRNESS        Non-discrimination, equity, bias mitigation
TRANSPARENCY    Explainability, disclosure, interpretability
SAFETY          Reliability, security, robustness
ACCOUNTABILITY  Responsibility, oversight, governance
HUMAN_RIGHTS    Fundamental rights protection, civil liberties

# Application Domains
HEALTHCARE      Medical, health applications, clinical tools
FINANCE         Banking, financial services, insurance
EDUCATION       Learning, educational tools, training
TRANSPORTATION  Autonomous vehicles, logistics, aviation
JUSTICE         Legal, criminal justice systems, law enforcement
EMPLOYMENT      Hiring, workplace AI, labor
GOVERNMENT      Public sector applications, civic services
MILITARY        Defense, national security, intelligence
CONSUMER        Consumer-facing applications, retail

# Risk and Harm Types
DISCRIMINATION_HARM  Bias, unfair treatment, algorithmic discrimination
PRIVACY_HARM         Data breaches, surveillance, unauthorized access
SAFETY_HARM          Physical injury, system failures, accidents
ECONOMIC_HARM        Job loss, financial damage, market disruption
SECURITY_HARM        Cyber attacks, weaponization, vulnerabilities
SOCIAL_HARM          Polarization, misinformation, manipulation
AUTONOMY_HARM        Loss of human control, coercion

# Lifecycle Stages
RESEARCH_STAGE       Basic research, development, ideation
TRAINING_STAGE       Model training, data collection, fine-tuning
TESTING_STAGE        Validation, evaluation, auditing
DEPLOYMENT_STAGE     Implementation, launch, operationalization
MONITORING_STAGE     Ongoing oversight, auditing, tracking
DECOMMISSION_STAGE   Retirement, sunsetting, phase-out

# Risk Categories
ALIGNMENT_RISK       Goal misalignment, value drift
EMERGENCE_RISK       Unexpected capabilities, emergent behaviors
MISUSE_RISK          Malicious use cases, dual-use concerns
STRUCTURAL_RISK      Systemic impacts, cascading failures

# AI System Types
FRONTIER_AI          Highly capable, cutting-edge systems
GENERAL_PURPOSE_AI   Broad capability systems, foundation models
NARROW_AI            Domain-specific applications, specialized systems
EMERGENT_CAPABILITY  Unexpected abilities, novel behaviors

# Data Types
TRAINING_DATA        Data used for model training
PERSONAL_DATA        Individual identifiable information
SENSITIVE_DATA       Protected category data (race, health, etc.)
PUBLIC_DATA          Openly available data
SYNTHETIC_DATA       AI-generated data

# Other Categories
STAKEHOLDER          Affected groups, communities, civil society, developers, users
MECHANISM            Implementation tools, processes, enforcement methods
BENCHMARK            Metrics, measurements, impact estimates
PENALTY              Fines, sanctions, civil or criminal remedies


TASK DESCRIPTION
1. You must label all complete entity mentions in the provided documents that correspond to the definitions above.
2. Each labeled entity must be associated with exactly one tag from the schema.

ANNOTATION RULES
1. Case-insensitive matching — “Department of Energy” and “department of energy” are treated the same.
2. Exact phrase matching only — No partial or fuzzy matches.
3. No guessing — Label only if the text clearly matches a known entity or fits the description.
4. Repeatable labeling — If the same entity appears multiple times, label every occurrence.
5. Mutual exclusivity — Each phrase can have only one label.
6. Non-overlapping spans — Do not assign two labels to overlapping text.
7. Precision over recall — Avoid false positives.

OUTPUT FORMAT
Return your result as a single JSON array.
 Each item represents one document and must follow this structure:
{
  "document_id": "doc_001",
  "entities": [
    { "pattern": "Department of Energy", "label": "ORGANIZATION" },
    { "pattern": "Executive Order 14110", "label": "LAW" },
    { "pattern": "machine learning", "label": "TECHNOLOGY" }
  ]
}

Document IDs in the document_id field must match the document ids given for each document in the input.

EXPECTED OUTPUT
1. Output only the JSON data — no explanations, summaries, or commentary.
2. Include every entity that matches the schema definitions.
3. Ensure the JSON is well-formatted and valid.
4. The output must be complete, covering all documents in the input file.


EXAMPLE OUTPUT
[
  {
    "document_id": "doc_001",
    "entities": [
      { "pattern": "Defense Advanced Research Projects Agency", "label": "ORGANIZATION" },
      { "pattern": "AI Bill of Rights", "label": "POLICY" },
      { "pattern": "reinforcement learning", "label": "TECHNOLOGY" },
      { "pattern": "United States", "label": "GEOGRAPHIC" }
    ]
  }
]


FINAL INSTRUCTION
1. Go through every document and identify all valid entity mentions based on the taxonomy above, and output a single JSON file exactly in the format specified.
2. Do not provide code or intermediate explanations — only the final JSON file as your complete answer.
3. Provide the answers in a downloadable json file with name as <start document id>-<end document id>.json

NOW PROCESS THE FOLLOWING DOCUMENTS:

"""

def chunk_writer():
    doc_chunk_write_path = Path("data/document_chunks")
    docs_df = pd.read_csv("data/documents.csv")
    
    
    docs_df = (
        docs_df
        .rename(columns={'Long summary': 'long_summary'}) # rename the column
        .dropna(subset=['long_summary'])  # drop null summaries
    )

    for i in range(0, len(docs_df), 10):
        chunk = docs_df.iloc[i: i + 10]
        filename = f"{str(i+1).zfill(3)}-{str(i+10).zfill(3)}.txt"         
        with open(doc_chunk_write_path / filename, 'w', encoding='utf-8') as w:
            w.write(prompt())
            arr = chunk.long_summary.values
            for j, text in enumerate(arr):
                w.write(f'doc_{str(i + 1 + j).zfill(3)}\n')
                w.write(text)
                w.write('\n\n---\n\n')

def clean_dependency(path):

    df = pd.read_parquet(path)
    ent_label_df = pd.read_parquet('./output/entity_label.parquet')

    # Only keep valid triples
    clean_df = df.dropna(subset=["sub", "verb", "obj"])

    clean_df = clean_df[
        (clean_df["sub"].str.strip() != "") &
        (clean_df["verb"].str.strip() != "") &
        (clean_df["obj"].str.strip() != "")
    ]

    clean_df['label'] = (
        clean_df['verb']
        .map(verb_map) # verb remapping
        .fillna('OTHER')
    )

    clean_df = clean_df[clean_df.label != 'OTHER'] # drop unmapped verbs

    nodes_df = pd.DataFrame(
        pd.concat([clean_df['sub'], clean_df['obj']])
        .drop_duplicates(),
        columns=['pattern']
    )
    

    # get entites label for each entity
    nodes_df = pd.merge(
        nodes_df,
        ent_label_df,
        on='pattern',
        how='inner',
    )

    nodes_df['category'] = (
        nodes_df['label']
        .map(label_map)
        .fillna('OTHER')
    )

    nodes_df['name'] = (
        nodes_df['pattern']
        .str
        .strip()
        .replace(entity_map)
    )
    
    nodes_df = (
        nodes_df
        .drop_duplicates(subset=['name'])
        .reset_index(drop=True)
        .loc[:, ['name', 'category', 'AGORA ID']]
        .rename(columns={'AGORA ID': 'doc_id'})
    )

    nodes_df.reset_index(drop=True, inplace=True)
    nodes_df['id'] = nodes_df.index
    mapping = {row['name']: row['id'] for _, row in nodes_df.iterrows()}

    clean_df['source'] = clean_df['sub'].map(mapping)
    clean_df['target'] = clean_df['obj'].map(mapping)
    
    edges_df = (
        clean_df
        .dropna(subset=['source', 'target'])
        .loc[:, ['source', 'target', 'verb', 'label', 'AGORA ID']]
        .rename(columns={'AGORA ID': 'doc_id', 'label': 'name'})
    )
    
    edges_df = edges_df.assign(
        source=edges_df.source.astype(int), 
        target=edges_df.target.astype(int),
    )


    nodes_df.to_csv("./output/nodes.csv", index=False)
    edges_df.to_csv("./output/edges.csv", index=False)

def count_ner_labels():

    tag_counter = defaultdict(int)

    with open('ner_results.json', 'r', encoding='utf-8') as file:
        ner_dict = json.load(file)
        for ner in ner_dict:
            entities_list = ner.get('entities')
            for txt_label in entities_list:
                tag_counter[txt_label.get('label')] += 1

# def collapse_verbs(verb_map):
#     df = pd.read_csv('./output/edges.csv')
#     df['label'] = df['relationship'].map(verb_map).fillna('OTHER')
#     df = df[df.label != 'OTHER']
#     df.to_csv("./output/edges_remapped.csv", index=False)
#     return df 

# def create_labels_remapped_nodes(mapping_dict):
#     df = pd.read_parquet('./output/entity_label.parquet')
#     df['category'] = df['label'].map(mapping_dict).fillna('OTHER')
#     df['name'] = df['pattern'].str.strip().replace(entity_map)
#     breakpoint()
#     df = df.reset_index(drop=True)
#     df['id'] = df.index.astype(int)

#     nodes_df = (
#         df[['id', 'name', 'category', 'AGORA ID']]
#         .rename(columns={'AGORA ID': 'doc_id'})
#     )

#     nodes_df.to_csv('./output/nodes_clean.csv', index=False)

def build_doc_kg():
    path = Path('./data/documents.csv')
    output = Path('./output')

    df = pd.read_csv(path)
    doc_df = df[
        [
            'AGORA ID', 
            'Casual name', 
            'Authority', 
            'Primarily applies to the government',
            'Primarily applies to the private sector',
            'Long summary',
        ]
    ]

    doc_df.columns = ['doc_id', 'name', 'authority', 
                      'applies_gov','applies_private', 'summary']
    
    doc_df.to_csv(output / 'neo_docs.csv', index=False)

    prefix_map = {
        "Strategies": "STRATEGY",
        "Risk factors": "RISK",
        "Harms": "HARM",
        "Incentives": "INCENTIVE",
        "Applications": "APPLICATION",
    }

    tag_cols = [
        col for col in df.columns
        for pref in prefix_map.keys()
        if col.startswith(pref)
    ]
    
    def normalize_tags(s): 
        category, *subcategories = [p.strip() for p in s.split(':')]
        norm_tag = f"{prefix_map[category]}: {' - '.join(subcategories)}"
        return norm_tag 
 
    tags = [normalize_tags(col) for col in tag_cols]
    tags_df = df[['AGORA ID'] + tag_cols] 
    tags_df.columns = ['doc_id'] + tags

    tag_id_map = {tag: i for i, tag in enumerate(tags)}

    tags_df = pd.melt(
        tags_df, 
        value_vars=tags, 
        var_name='name', 
        value_name='tag_true', 
        id_vars=['doc_id']
    )

    tags_df['tag_id'] = tags_df.name.map(tag_id_map)
    tags_df = tags_df[tags_df.tag_true]

    tags_df.drop(columns='tag_true', inplace=True)

    (
        pd.DataFrame(tag_id_map.items(), columns=['name', 'tag_id'])
        .to_csv(output / 'tags.csv', index=False)
    )

    tags_df.to_csv(output / 'doc_tag_edges.csv', index=False)

if __name__ == "__main__":
    
    # tabulate_extracted_entities()
    # ent_df = pd.read_parquet('./output/entity_label.parquet')
    # clean_dependency("./output/dependency.parquet")
    # count_ner_labels()
    # create_labels_remapped_nodes(label_map)
    # df = collapse_verbs(verb_map)
    # build_doc_kg()
    pass 
    # breakpoint()
    