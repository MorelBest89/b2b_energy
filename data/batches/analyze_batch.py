import json
import sys

with open(r'C:\Users\marco\Projects\consulenza_energy\data\batches\batch_0.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(r'C:\Users\marco\Projects\consulenza_energy\data\batches\batch_dump.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total entries: {len(data)}\n\n")
    for item in data:
        out.write(f"--- Index {item['index']} ---\n")
        out.write(f"  Nome: {item['nome']}\n")
        out.write(f"  Citta: {item['citta']}\n")
        out.write(f"  Categoria: {item['categoria']}\n")
        out.write(f"  Telefono: {item['telefono']}\n")
        out.write(f"  Sito: {item['sito']}\n")
        out.write(f"  Title: {item['title']}\n")
        out.write(f"  Meta: {item['meta']}\n")
        txt = item['text']
        if len(txt) > 800:
            txt = txt[:800] + "..."
        out.write(f"  Text: {txt}\n")
        out.write("\n")

print("Done - written to batch_dump.txt")
