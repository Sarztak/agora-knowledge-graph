import pandas as pd
df = pd.read_csv("./data/documents_normalized.csv")
df = pd.read_csv("./data/documents.csv")
for i, text in enumerate(df["Long summary"].fillna("")):
    last = i
    last_text = text
print(last)
print(last_text)


#print(len(df['doc_id'].drop_duplicates()))
print(len(df['Long summary'].dropna()))