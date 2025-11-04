from relationship_extractor import RelationExtractor
import pandas as pd
import numpy as np
import spacy
from rich.traceback import install

install()

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

if __name__ == "__main__":
    # import spacy
    # # Example usage:
    nlp = spacy.load("en_core_web_sm")
    docs_df = pd.read_csv('./data/documents.csv')
    docs_df.rename(columns={'Long summary': 'long_summary'}, inplace=True)

    ent_df = pd.read_parquet('./output/entity_label.parquet')

    ent_docs_df = pd.merge(ent_df, docs_df, on='AGORA ID', how='inner')
    
    ent_list_df = (
        ent_docs_df
        .groupby('doc_index')
        .apply(lambda df: create_ner_list(df), include_groups=False)
        .reset_index()
    )
    ent_list_df[['patterns', 'long_summary']] = pd.DataFrame(ent_list_df[0].tolist(), index=ent_list_df.index)
    ent_list_df = ent_list_df.drop(columns=0)
    ent_list_df['dependency'] = ent_list_df.apply(lambda row: extract_dependency(row, nlp), axis=1)
    dep_df = ent_list_df[['doc_index', 'dependency']]
    dep_df = dep_df.explode('dependency')
    dep_df[['sub', 'verb', 'obj']] = pd.DataFrame(dep_df['dependency'].tolist(), index=dep_df.index)
    dep_df = dep_df.drop(columns='dependency').replace({None: np.nan}).reset_index(drop=True)
    dep_df = pd.merge(dep_df, ent_docs_df[['AGORA ID', 'doc_index']].drop_duplicates(), on='doc_index', how='left')[['doc_index', 'AGORA ID', 'sub', 'verb', 'obj']]
    dep_df.to_parquet('output/dependency.parquet')




