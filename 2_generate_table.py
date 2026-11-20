import pandas as pd 
import json

file_path = "manually_corrected_dataset.csv"
df = pd.read_csv(file_path, encoding="gbk", keep_default_na=False)

df = df[["group", "human_1", "human_2", "human_3", "web_theme"]]

human_theme_count = {}
web_theme_count = {}
total_count = len(df)

for _, row in df.iterrows():
    group = row["group"]

    if group == "OTHERS":
        group = "General"

    if group not in human_theme_count:
        human_theme_count[group] = {}
        web_theme_count[group] = {}

    human_annotations = []

    for col in ["human_1", "human_2", "human_3"]:
        if row[col].strip() != "":
            human_annotations.append(json.loads(row[col]))
    

    weight = 1 / len(human_annotations)

    for labels in human_annotations:
        for theme in set(labels):
            if theme not in human_theme_count[group]:
                human_theme_count[group][theme] = 0
            human_theme_count[group][theme] += weight

    web_themes = []
    for label in row["web_theme"].split(";"):
        theme = label.strip().lower()

        if theme != "" and theme not in web_themes:
            web_themes.append(theme)
    for theme in web_themes:    
        if theme not in web_theme_count[group]:
            web_theme_count[group][theme] = 0
        web_theme_count[group][theme] += 1

# print(human_theme_count)
# print(web_theme_count)  
human_pct = {}
web_pct = {}

# Using 70 beacause each group has 70 poems
for group in human_theme_count:
    human_pct[group] = {}
    web_pct[group] = {}

    for theme, count in human_theme_count[group].items():
        human_pct[group][theme] = count / 70 * 100

    for theme, count in web_theme_count[group].items():
        web_pct[group][theme] = count / 70 * 100

human_df = pd.DataFrame(human_pct).fillna(0)
web_df = pd.DataFrame(web_pct).fillna(0)

human_df.to_csv("human_theme_percentage.csv", encoding="utf-8-sig", index_label="theme")
web_df.to_csv("web_theme_percentage.csv", encoding="utf-8-sig", index_label="theme")

def make_ranked_table(percentages):
    result = {}

    for group in percentages:
        sorted_themes = sorted(
            percentages[group].items(),
            key=lambda item: item[1],
            reverse=True
        )

        cells = []

        for theme, percentage in sorted_themes:
            cells.append(f"{theme} ({percentage:.1f}%)")

        result[group] = pd.Series(cells)

    table = pd.DataFrame(result).fillna("")
    table.index = range(1, len(table) + 1)

    return table


human_table = make_ranked_table(human_pct)

# Use this to remove public domain and audio from web themes
# for group in web_pct:
#     for theme in ["public domain", "audio"]:
#         if theme in web_pct[group]:
#             del web_pct[group][theme]


web_table = make_ranked_table(web_pct)

human_table.to_csv(
    "human_theme_ranked.csv",
    encoding="utf-8-sig",
    index_label="Rank"
)

web_table.to_csv(
    "web_theme_ranked.csv",
    encoding="utf-8-sig",
    index_label="Rank"
)
groups = ["AA", "APA-AA", "LXA", "NA"]

human_relative = human_df[groups].sub(human_df["General"], axis=0)
web_relative = web_df[groups].sub(web_df["General"], axis=0)

LABELCOLS = ['nature', 'body', 'death', 'love', 'existential', 'identity', 'self', 'beauty', 'america', 'loss', 'animals', 'history', 'memories', 'family', 'writing', 'ancestry', 'thought', 'landscapes', 'war', 'time', 'religion', 'grief', 'violence', 'aging', 'childhood', 'desire', 'night', 'mothers', 'language', 'birds', 'social justice', 'music', 'flowers', 'politics', 'hope', 'heartache', 'fathers', 'gender', 'environment', 'spirituality', 'loneliness', 'oceans', 'dreams', 'survival', 'cities', 'earth', 'despair', 'anxiety', 'weather', 'illness']
human_relative = human_relative.loc[human_relative.index.isin(LABELCOLS)]
web_relative = web_relative.loc[web_relative.index.isin(LABELCOLS)]

human_relative_table = make_ranked_table(human_relative)
web_relative_table = make_ranked_table(web_relative)


human_relative_table.to_csv(
    "human_theme_relative.csv", encoding="utf-8-sig", index_label="Rank"
)
web_relative_table.to_csv(
    "web_theme_relative.csv", encoding="utf-8-sig", index_label="Rank"
)