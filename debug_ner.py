import json
import re
from pathlib import Path


import json
import re
from pathlib import Path
import json
import re

def mask_single_law(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    masked_records = []

    for item in data:
        text = item.get("text", "")
        entities = item.get("entities", [])

        # assume exactly one BILL_NAME
        law_ents = [e for e in entities if e.get("label") == "BILL_NAME"]
        if not law_ents:
            continue

        law_text = law_ents[0]["text"]
        masked_text = re.sub(re.escape(law_text), "LAW_ENTITY", text)

        # also update the entity list to reflect the masked token
        new_entities = []
        for ent in entities:
            ent_copy = dict(ent)
            if ent_copy.get("label") == "BILL_NAME":
                ent_copy["text"] = "LAW_ENTITY"
            new_entities.append(ent_copy)

        masked_records.append({
            "index": item.get("index"),
            "masked_text": masked_text,
            "entities": new_entities,
            "law_map": {"LAW_ENTITY": law_text}
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(masked_records, f, indent=2, ensure_ascii=False)

    print(f"Saved masked JSON to {output_path}")


if __name__ == "__main__":
    mask_single_law("ner_results.json", "masked_output.json")
