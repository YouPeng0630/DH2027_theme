from pathlib import Path
import json
import pandas as pd

file_path = r"annotation_poets_05162026-20261118T210406Z-1-001\annotation_poets_05162026"

# Use NA false because there is an group called NA
groups = pd.read_csv("poet_group.csv", keep_default_na=False)
author_groups = groups.set_index("AUTHOR")["GROUP"].to_dict()

record = []
for file in Path(file_path).rglob("*.json"):
    data = json.loads(file.read_text(encoding="utf-8-sig"))
    record.append({
        "title": data["title"],
        "website_url": data["poem_url"],
        "author": data.get("author"),
        "annotator": data["username"],
        "human_theme": json.dumps(data["tags"], ensure_ascii=False),
        "poem_uuid": data.get("poem_meta", {}).get("poem_uuid"),
        "group": author_groups.get(data.get("author"), "OTHERS")
    }
    )

annotations = pd.DataFrame(record)

# save_path = Path("annotations_theme.csv")
# annotations.to_csv(save_path, index=False, encoding="utf-8-sig")


# print(annotations.head(10))


poem_metadata_path = Path("poem_metadata.csv")
poem_metadata = pd.read_csv(poem_metadata_path, usecols=["poem_uuid", "link", "themes"])

poem_metadata = poem_metadata[
    poem_metadata["poem_uuid"].isin(annotations["poem_uuid"])
]

web_themes = poem_metadata.set_index("poem_uuid")["themes"]
annotations["web_theme"] = annotations["poem_uuid"].map(web_themes)
annotations = annotations.sort_values(["poem_uuid", "annotator"])

poem_list = []

uuid = None

for _, row in annotations.iterrows():
    if row["poem_uuid"] != uuid:
        poem_list.append({
            "poem_uuid": row["poem_uuid"],
            "human_1": "",
            "human_2": "",
            "human_3": "",
            "web_theme": row["web_theme"],
            "group": row["group"],
            "url": row["website_url"],
            "title": row["title"],
        })

        uuid = row["poem_uuid"]
        number = 1

    poem_list[-1][f"human_{number}"] = row["human_theme"]
    number += 1

result = pd.DataFrame(poem_list)

result.to_csv("dataset.csv", index=False, encoding="utf-8-sig")