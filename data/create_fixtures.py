import json

FILE_NAME: str = 'ingredients.json'

with open(FILE_NAME, 'r') as read_file:
    data = json.load(read_file)
    new_data = []

for i in range(len(data)):
    new_data.append(
        {
            "model": "api.ingredient",
            "pk": i + 1,
            "fields": data[i]
        }
    )

with open(FILE_NAME, 'w', encoding='utf8') as write_file:
    json.dump(new_data, write_file, ensure_ascii=False)
