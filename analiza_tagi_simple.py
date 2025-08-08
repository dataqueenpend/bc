#!/usr/bin/env python3
"""
Uproszczona analiza tagów technicznych w projektach AI/TAI
"""

import csv
from collections import Counter, defaultdict
import json

print("=" * 60)
print("ANALIZA TAGÓW TECHNICZNYCH W PROJEKTACH AI/TAI")
print("=" * 60)

# 1. Wczytanie danych
print("\n1. WCZYTANIE DANYCH")
print("-" * 40)

# Wczytaj główny plik
with open('tagi_BC.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    projekty = list(reader)

# Wczytaj legendę
with open('legenda.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    legenda = {row['Tag']: row['Opis'] for row in reader}

print(f"Liczba projektów: {len(projekty)}")
print(f"Liczba tagów w legendzie: {len(legenda)}")

# 2. Analiza zespołów
print("\n\n2. ANALIZA ZESPOŁÓW")
print("-" * 40)

zespoly = Counter(p['Zespół zgłaszający potrzebę'] for p in projekty)
print("\nStatystyki zespołów:")
for zespol, count in zespoly.most_common():
    print(f"  {zespol}: {count} projektów ({count/len(projekty)*100:.1f}%)")

# 3. Analiza celów biznesowych
print("\n\n3. ANALIZA CELÓW BIZNESOWYCH")
print("-" * 40)

cele = Counter(p['Cel biznesowy'] for p in projekty if p['Cel biznesowy'])
print("\nTop 10 celów biznesowych:")
for i, (cel, count) in enumerate(cele.most_common(10), 1):
    print(f"  {i}. {cel}: {count} projektów")

# 4. Analiza KPI
print("\n\n4. ANALIZA KPI")
print("-" * 40)

kpi_counter = Counter(p['KPI'] for p in projekty if p['KPI'])
print("\nTop 10 KPI:")
for i, (kpi, count) in enumerate(kpi_counter.most_common(10), 1):
    print(f"  {i}. {kpi}: {count} projektów")

# 5. Analiza tagów
print("\n\n5. ANALIZA TAGÓW TECHNICZNYCH")
print("-" * 40)

# Zbierz wszystkie tagi
all_tags = []
for projekt in projekty:
    if projekt['TAI - tagi']:
        tags = [tag.strip() for tag in projekt['TAI - tagi'].split(',')]
        all_tags.extend(tags)

tag_counts = Counter(all_tags)
print(f"\nLiczba unikalnych tagów: {len(tag_counts)}")
print(f"Łączna liczba użyć tagów: {sum(tag_counts.values())}")

print("\nTop 20 najczęściej używanych tagów:")
for i, (tag, count) in enumerate(tag_counts.most_common(20), 1):
    print(f"  {i:2d}. {tag:40s}: {count:3d} wystąpień")

# 6. Kategorie tagów
print("\n\n6. KATEGORIE TAGÓW")
print("-" * 40)

kategorie = {
    'Frazy': [],
    'LLM': [],
    'Baza wektorowa': [],
    'Klasyfikacja': [],
    'Analiza': [],
    'Detekcja': []
}

for tag in tag_counts:
    if 'frazy' in tag:
        kategorie['Frazy'].append(tag)
    if 'llm' in tag:
        kategorie['LLM'].append(tag)
    if 'baza-wektorowa' in tag:
        kategorie['Baza wektorowa'].append(tag)
    if 'klasyfikacja' in tag or 'classification' in tag:
        kategorie['Klasyfikacja'].append(tag)
    if 'analiza' in tag or 'analysis' in tag:
        kategorie['Analiza'].append(tag)
    if 'detection' in tag or 'detekcja' in tag:
        kategorie['Detekcja'].append(tag)

for kat, tags in kategorie.items():
    if tags:
        total = sum(tag_counts[tag] for tag in tags)
        print(f"\n{kat} ({len(tags)} tagów, {total} użyć):")
        for tag in sorted(tags)[:5]:
            print(f"  - {tag}: {tag_counts[tag]} wystąpień")
        if len(tags) > 5:
            print(f"  ... i {len(tags) - 5} więcej")

# 7. Złożoność projektów
print("\n\n7. ZŁOŻONOŚĆ PROJEKTÓW")
print("-" * 40)

liczby_tagow = []
for projekt in projekty:
    if projekt['TAI - tagi']:
        liczba = len(projekt['TAI - tagi'].split(','))
        liczby_tagow.append(liczba)
        projekt['liczba_tagow'] = liczba
    else:
        projekt['liczba_tagow'] = 0
        liczby_tagow.append(0)

if liczby_tagow:
    srednia = sum(liczby_tagow) / len(liczby_tagow)
    liczby_tagow.sort()
    mediana = liczby_tagow[len(liczby_tagow)//2]
    
    print(f"Średnia liczba tagów na projekt: {srednia:.2f}")
    print(f"Mediana liczby tagów: {mediana}")
    print(f"Minimalna liczba tagów: {min(liczby_tagow)}")
    print(f"Maksymalna liczba tagów: {max(liczby_tagow)}")

# Najbardziej złożone projekty
projekty_sorted = sorted(projekty, key=lambda x: x['liczba_tagow'], reverse=True)
print("\nNajbardziej złożone projekty (najwięcej tagów):")
for i, projekt in enumerate(projekty_sorted[:5]):
    nazwa = projekt['Projekt'][:60] + '...' if len(projekt['Projekt']) > 60 else projekt['Projekt']
    print(f"  {i+1}. {nazwa}: {projekt['liczba_tagow']} tagów")

# 8. Współwystępowanie tagów
print("\n\n8. WSPÓŁWYSTĘPOWANIE TAGÓW")
print("-" * 40)

# Znajdź pary tagów występujące razem
pary_tagow = defaultdict(int)
for projekt in projekty:
    if projekt['TAI - tagi']:
        tags = [tag.strip() for tag in projekt['TAI - tagi'].split(',')]
        for i in range(len(tags)):
            for j in range(i+1, len(tags)):
                para = tuple(sorted([tags[i], tags[j]]))
                pary_tagow[para] += 1

# Top 10 par
top_pary = sorted(pary_tagow.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nNajczęściej współwystępujące pary tagów:")
for (tag1, tag2), count in top_pary:
    if count > 2:  # Minimum 3 wystąpienia
        print(f"  {tag1} + {tag2}: {count} projektów")

# 9. Typ zadania
print("\n\n9. TYP ZADANIA")
print("-" * 40)

typy = defaultdict(int)
for projekt in projekty:
    if projekt['Dodatkowe']:
        if 'BIZNES' in projekt['Dodatkowe']:
            typy['BIZNES'] += 1
        elif 'KONTROLA' in projekt['Dodatkowe']:
            typy['KONTROLA'] += 1
        elif 'PROCES' in projekt['Dodatkowe']:
            typy['PROCES'] += 1
        else:
            typy['NIEZNANY'] += 1
    else:
        typy['NIEZNANY'] += 1

print("\nRozkład projektów według typu:")
for typ, count in sorted(typy.items(), key=lambda x: x[1], reverse=True):
    print(f"  {typ}: {count} projektów ({count/len(projekty)*100:.1f}%)")

# 10. Podsumowanie
print("\n\n10. PODSUMOWANIE")
print("=" * 60)

print(f"\nKluczowe statystyki:")
print(f"  - Liczba projektów: {len(projekty)}")
print(f"  - Liczba unikalnych tagów: {len(tag_counts)}")
print(f"  - Średnia liczba tagów na projekt: {srednia:.2f}")
print(f"  - Dominujący zespół: {zespoly.most_common(1)[0][0]} ({zespoly.most_common(1)[0][1]} projektów)")
print(f"  - Najczęstszy tag: {tag_counts.most_common(1)[0][0]} ({tag_counts.most_common(1)[0][1]} wystąpień)")

# Rekomendacje
print("\nRekomendacje:")

# Rzadkie tagi
rzadkie = [tag for tag, count in tag_counts.items() if count == 1]
print(f"\n1. Optymalizacja tagów:")
print(f"   - Znaleziono {len(rzadkie)} tagów używanych tylko raz")
print(f"   - Stanowi to {len(rzadkie)/len(tag_counts)*100:.1f}% wszystkich tagów")

# Technologie
tech_counts = {
    'Klasyczne ML': len([t for t in all_tags if any(kw in t for kw in ['frazy-binary', 'klasyfikacja', 'clustering'])]),
    'LLM/GenAI': len([t for t in all_tags if 'llm' in t]),
    'Bazy wektorowe': len([t for t in all_tags if 'baza-wektorowa' in t or 'retrieval' in t])
}

print(f"\n2. Wykorzystanie technologii:")
for tech, count in tech_counts.items():
    print(f"   - {tech}: {count} użyć ({count/len(all_tags)*100:.1f}%)")

# Wieloetapowe
wieloetapowe = sum(1 for p in projekty if p['TAI - uwagi'] and 'wieloetapowe' in p['TAI - uwagi'].lower())
print(f"\n3. Złożoność:")
print(f"   - {wieloetapowe} projektów wieloetapowych ({wieloetapowe/len(projekty)*100:.1f}%)")

print("\n" + "=" * 60)

# Zapisz wyniki do JSON
wyniki = {
    'statystyki': {
        'liczba_projektow': len(projekty),
        'liczba_tagow': len(tag_counts),
        'srednia_tagow': srednia,
        'dominujacy_zespol': zespoly.most_common(1)[0][0],
        'najczestszy_tag': tag_counts.most_common(1)[0][0]
    },
    'top_10_tagow': tag_counts.most_common(10),
    'typy_zadan': dict(typy),
    'zespoly': dict(zespoly),
    'technologie': tech_counts
}

with open('wyniki_analizy.json', 'w', encoding='utf-8') as f:
    json.dump(wyniki, f, ensure_ascii=False, indent=2)

print("\nWyniki zapisane do pliku: wyniki_analizy.json")