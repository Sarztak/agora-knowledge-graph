import pandas as pd 
from pathlib import Path
from helper import prefix_zero, prompt 



if __name__ == "__main__":
    doc_chunk_write_path = Path("data/document_chunks")
    docs_df = pd.read_csv("data/documents.csv")
    
    
    docs_df = (
        docs_df
        .rename(columns={'Long summary': 'long_summary'}) # rename the column
        .dropna(subset=['long_summary'])  # drop null summaries
    )

    for i in range(0, len(docs_df), 10):
        chunk = docs_df.iloc[i: i + 10]
        filename = f"{prefix_zero(i+1, 3)}-{prefix_zero(i+10, 3)}.txt"         
        with open(doc_chunk_write_path / filename, 'w', encoding='utf-8') as w:
            w.write(prompt())
            arr = chunk.long_summary.values
            for j, text in enumerate(arr):
                w.write(f'doc_{prefix_zero(i + 1 + j)}\n')
                w.write(text)
                w.write('\n\n---\n\n')





