from formfyxer import lit_explorer
import glob
import os
import json

all_files = glob.glob("../../../../forms2/*")
all_stats = {}
all_scores = {}

openai_creds = {
  "org": os.environ.get("OPENAI_ORG"),
  "key": os.environ.get("OPENAI_KEY")
}

for f in reversed(sorted(all_files)):
  f_name = f.split('/')[-1]
  try:
    all_stats[f_name] = lit_explorer.parse_form(f, openai_creds=openai_creds, normalize=True, debug=True)
    for key in all_stats[f_name].keys():
        print(f"{key}: {type(all_stats[f_name][key])}")
    with open("stats.json", "w") as stats_file:
        stats_file.write(json.dumps(all_stats))
  except Exception as ex:
    print(ex)
    continue
  all_scores[f_name] = lit_explorer.form_complexity(all_stats[f_name])
  print(f"{f_name}: {all_scores[f_name]}")

for f in all_stats.keys():
  print(f"{f}: {all_scores[f]}")
  print(all_stats[f])
  print()

[print(f"{f}: {score}") for score, f in sorted([(score, f) for f, score in all_scores.items()])]
