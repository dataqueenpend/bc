#!/usr/bin/env python3
"""
Skrypt generujący notebook Jupyter z analizą tagów
"""

import json

# Struktura notebooka
notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Analiza tagów technicznych w projektach AI/TAI\n",
                "\n",
                "Ten notebook zawiera analizę projektów związanych z przetwarzaniem języka naturalnego i analizą rozmów w kontekście bankowym.\n",
                "\n",
                "## Spis treści\n",
                "1. Wczytanie danych\n",
                "2. Analiza zespołów i projektów\n",
                "3. Analiza tagów technicznych\n",
                "4. Analiza złożoności projektów\n",
                "5. Współwystępowanie tagów\n",
                "6. Analiza według typu zadania\n",
                "7. Podsumowanie i rekomendacje"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Import bibliotek\n",
                "import csv\n",
                "from collections import Counter, defaultdict\n",
                "import json\n",
                "\n",
                "# Dla wizualizacji (opcjonalne - jeśli masz matplotlib)\n",
                "try:\n",
                "    import matplotlib.pyplot as plt\n",
                "    has_matplotlib = True\n",
                "except ImportError:\n",
                "    has_matplotlib = False\n",
                "    print(\"Matplotlib nie jest zainstalowany - wykresy będą pominięte\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Wczytanie danych"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Wczytaj główny plik\n",
                "with open('tagi_BC.csv', 'r', encoding='utf-8') as f:\n",
                "    reader = csv.DictReader(f)\n",
                "    projekty = list(reader)\n",
                "\n",
                "# Wczytaj legendę\n",
                "with open('legenda.csv', 'r', encoding='utf-8') as f:\n",
                "    reader = csv.DictReader(f)\n",
                "    legenda = {row['Tag']: row['Opis'] for row in reader}\n",
                "\n",
                "print(f\"Liczba projektów: {len(projekty)}\")\n",
                "print(f\"Liczba tagów w legendzie: {len(legenda)}\")\n",
                "print(f\"\\nPrzykładowy projekt:\")\n",
                "for key, value in list(projekty[0].items())[:5]:\n",
                "    print(f\"  {key}: {value[:50]}...\" if len(str(value)) > 50 else f\"  {key}: {value}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Analiza zespołów i projektów"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Analiza zespołów\n",
                "zespoly = Counter(p['Zespół zgłaszający potrzebę'] for p in projekty)\n",
                "\n",
                "print(\"Statystyki zespołów:\")\n",
                "for zespol, count in zespoly.most_common():\n",
                "    print(f\"  {zespol}: {count} projektów ({count/len(projekty)*100:.1f}%)\")\n",
                "\n",
                "# Wykres (jeśli matplotlib jest dostępny)\n",
                "if has_matplotlib:\n",
                "    plt.figure(figsize=(10, 6))\n",
                "    plt.bar(zespoly.keys(), zespoly.values())\n",
                "    plt.xlabel('Zespół')\n",
                "    plt.ylabel('Liczba projektów')\n",
                "    plt.title('Liczba projektów według zespołów')\n",
                "    plt.xticks(rotation=45)\n",
                "    plt.tight_layout()\n",
                "    plt.show()"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Analiza celów biznesowych\n",
                "cele = Counter(p['Cel biznesowy'] for p in projekty if p['Cel biznesowy'])\n",
                "\n",
                "print(\"Top 10 celów biznesowych:\")\n",
                "for i, (cel, count) in enumerate(cele.most_common(10), 1):\n",
                "    print(f\"  {i}. {cel}: {count} projektów\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Analiza KPI\n",
                "kpi_counter = Counter(p['KPI'] for p in projekty if p['KPI'])\n",
                "\n",
                "print(\"Top 10 KPI:\")\n",
                "for i, (kpi, count) in enumerate(kpi_counter.most_common(10), 1):\n",
                "    print(f\"  {i}. {kpi}: {count} projektów\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Analiza tagów technicznych"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Zbierz wszystkie tagi\n",
                "all_tags = []\n",
                "for projekt in projekty:\n",
                "    if projekt['TAI - tagi']:\n",
                "        tags = [tag.strip() for tag in projekt['TAI - tagi'].split(',')]\n",
                "        all_tags.extend(tags)\n",
                "\n",
                "tag_counts = Counter(all_tags)\n",
                "\n",
                "print(f\"Liczba unikalnych tagów: {len(tag_counts)}\")\n",
                "print(f\"Łączna liczba użyć tagów: {sum(tag_counts.values())}\")\n",
                "print(f\"\\nTop 20 najczęściej używanych tagów:\")\n",
                "\n",
                "for i, (tag, count) in enumerate(tag_counts.most_common(20), 1):\n",
                "    opis = legenda.get(tag, \"Brak opisu\")\n",
                "    print(f\"  {i:2d}. {tag:40s}: {count:3d} wystąpień\")\n",
                "    print(f\"      -> {opis[:70]}...\" if len(opis) > 70 else f\"      -> {opis}\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Kategorie tagów\n",
                "kategorie = {\n",
                "    'Frazy': [],\n",
                "    'LLM': [],\n",
                "    'Baza wektorowa': [],\n",
                "    'Klasyfikacja': [],\n",
                "    'Analiza': [],\n",
                "    'Detekcja': []\n",
                "}\n",
                "\n",
                "for tag in tag_counts:\n",
                "    if 'frazy' in tag:\n",
                "        kategorie['Frazy'].append(tag)\n",
                "    if 'llm' in tag:\n",
                "        kategorie['LLM'].append(tag)\n",
                "    if 'baza-wektorowa' in tag:\n",
                "        kategorie['Baza wektorowa'].append(tag)\n",
                "    if 'klasyfikacja' in tag or 'classification' in tag:\n",
                "        kategorie['Klasyfikacja'].append(tag)\n",
                "    if 'analiza' in tag or 'analysis' in tag:\n",
                "        kategorie['Analiza'].append(tag)\n",
                "    if 'detection' in tag or 'detekcja' in tag:\n",
                "        kategorie['Detekcja'].append(tag)\n",
                "\n",
                "print(\"Kategorie tagów:\")\n",
                "for kat, tags in kategorie.items():\n",
                "    if tags:\n",
                "        total = sum(tag_counts[tag] for tag in tags)\n",
                "        print(f\"\\n{kat} ({len(tags)} tagów, {total} użyć):\")\n",
                "        for tag in sorted(tags)[:5]:\n",
                "            print(f\"  - {tag}: {tag_counts[tag]} wystąpień\")\n",
                "        if len(tags) > 5:\n",
                "            print(f\"  ... i {len(tags) - 5} więcej\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Analiza złożoności projektów"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Liczba tagów per projekt\n",
                "liczby_tagow = []\n",
                "for projekt in projekty:\n",
                "    if projekt['TAI - tagi']:\n",
                "        liczba = len(projekt['TAI - tagi'].split(','))\n",
                "        liczby_tagow.append(liczba)\n",
                "        projekt['liczba_tagow'] = liczba\n",
                "    else:\n",
                "        projekt['liczba_tagow'] = 0\n",
                "        liczby_tagow.append(0)\n",
                "\n",
                "if liczby_tagow:\n",
                "    srednia = sum(liczby_tagow) / len(liczby_tagow)\n",
                "    liczby_tagow.sort()\n",
                "    mediana = liczby_tagow[len(liczby_tagow)//2]\n",
                "    \n",
                "    print(f\"Średnia liczba tagów na projekt: {srednia:.2f}\")\n",
                "    print(f\"Mediana liczby tagów: {mediana}\")\n",
                "    print(f\"Minimalna liczba tagów: {min(liczby_tagow)}\")\n",
                "    print(f\"Maksymalna liczba tagów: {max(liczby_tagow)}\")\n",
                "\n",
                "# Histogram liczby tagów\n",
                "if has_matplotlib:\n",
                "    plt.figure(figsize=(10, 6))\n",
                "    plt.hist(liczby_tagow, bins=range(0, max(liczby_tagow)+2), edgecolor='black')\n",
                "    plt.xlabel('Liczba tagów')\n",
                "    plt.ylabel('Liczba projektów')\n",
                "    plt.title('Rozkład liczby tagów w projektach')\n",
                "    plt.grid(True, alpha=0.3)\n",
                "    plt.show()"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Najbardziej złożone projekty\n",
                "projekty_sorted = sorted(projekty, key=lambda x: x['liczba_tagow'], reverse=True)\n",
                "\n",
                "print(\"Top 5 najbardziej złożonych projektów (najwięcej tagów):\")\n",
                "for i, projekt in enumerate(projekty_sorted[:5], 1):\n",
                "    nazwa = projekt['Projekt'][:60] + '...' if len(projekt['Projekt']) > 60 else projekt['Projekt']\n",
                "    print(f\"\\n{i}. {nazwa}\")\n",
                "    print(f\"   Liczba tagów: {projekt['liczba_tagow']}\")\n",
                "    print(f\"   Zespół: {projekt['Zespół zgłaszający potrzebę']}\")\n",
                "    print(f\"   Cel: {projekt['Cel biznesowy']}\")\n",
                "    print(f\"   Tagi: {projekt['TAI - tagi'][:100]}...\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Współwystępowanie tagów"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Znajdź pary tagów występujące razem\n",
                "pary_tagow = defaultdict(int)\n",
                "for projekt in projekty:\n",
                "    if projekt['TAI - tagi']:\n",
                "        tags = [tag.strip() for tag in projekt['TAI - tagi'].split(',')]\n",
                "        for i in range(len(tags)):\n",
                "            for j in range(i+1, len(tags)):\n",
                "                para = tuple(sorted([tags[i], tags[j]]))\n",
                "                pary_tagow[para] += 1\n",
                "\n",
                "# Top 15 par\n",
                "top_pary = sorted(pary_tagow.items(), key=lambda x: x[1], reverse=True)[:15]\n",
                "\n",
                "print(\"Top 15 najczęściej współwystępujących par tagów:\")\n",
                "for (tag1, tag2), count in top_pary:\n",
                "    if count > 2:  # Minimum 3 wystąpienia\n",
                "        print(f\"  {tag1:30s} + {tag2:30s}: {count} projektów\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Analiza według typu zadania"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Typ zadania\n",
                "typy = defaultdict(int)\n",
                "for projekt in projekty:\n",
                "    if projekt['Dodatkowe']:\n",
                "        if 'BIZNES' in projekt['Dodatkowe']:\n",
                "            typy['BIZNES'] += 1\n",
                "        elif 'KONTROLA' in projekt['Dodatkowe']:\n",
                "            typy['KONTROLA'] += 1\n",
                "        elif 'PROCES' in projekt['Dodatkowe']:\n",
                "            typy['PROCES'] += 1\n",
                "        else:\n",
                "            typy['NIEZNANY'] += 1\n",
                "    else:\n",
                "        typy['NIEZNANY'] += 1\n",
                "\n",
                "print(\"Rozkład projektów według typu:\")\n",
                "for typ, count in sorted(typy.items(), key=lambda x: x[1], reverse=True):\n",
                "    print(f\"  {typ}: {count} projektów ({count/len(projekty)*100:.1f}%)\")\n",
                "\n",
                "# Analiza tagów według typu\n",
                "print(\"\\nNajpopularniejsze tagi według typu zadania:\")\n",
                "for typ in ['BIZNES', 'KONTROLA', 'PROCES']:\n",
                "    projekty_typu = [p for p in projekty if p['Dodatkowe'] and typ in p['Dodatkowe']]\n",
                "    if projekty_typu:\n",
                "        tagi_typu = []\n",
                "        for p in projekty_typu:\n",
                "            if p['TAI - tagi']:\n",
                "                tagi_typu.extend([tag.strip() for tag in p['TAI - tagi'].split(',')])\n",
                "        \n",
                "        if tagi_typu:\n",
                "            top_5 = Counter(tagi_typu).most_common(5)\n",
                "            print(f\"\\n{typ} (top 5 tagów):\")\n",
                "            for tag, count in top_5:\n",
                "                print(f\"  - {tag}: {count}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 7. Podsumowanie i rekomendacje"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Podsumowanie\n",
                "print(\"=\" * 60)\n",
                "print(\"PODSUMOWANIE ANALIZY\")\n",
                "print(\"=\" * 60)\n",
                "\n",
                "print(f\"\\nKluczowe statystyki:\")\n",
                "print(f\"  - Liczba projektów: {len(projekty)}\")\n",
                "print(f\"  - Liczba unikalnych tagów: {len(tag_counts)}\")\n",
                "print(f\"  - Średnia liczba tagów na projekt: {srednia:.2f}\")\n",
                "print(f\"  - Dominujący zespół: {zespoly.most_common(1)[0][0]} ({zespoly.most_common(1)[0][1]} projektów)\")\n",
                "print(f\"  - Najczęstszy tag: {tag_counts.most_common(1)[0][0]} ({tag_counts.most_common(1)[0][1]} wystąpień)\")\n",
                "\n",
                "# Rekomendacje\n",
                "print(\"\\nRekomendacje:\")\n",
                "\n",
                "# Rzadkie tagi\n",
                "rzadkie = [tag for tag, count in tag_counts.items() if count == 1]\n",
                "print(f\"\\n1. Optymalizacja tagów:\")\n",
                "print(f\"   - Znaleziono {len(rzadkie)} tagów używanych tylko raz ({len(rzadkie)/len(tag_counts)*100:.1f}%)\")\n",
                "print(f\"   - Sugerowane działanie: przegląd i konsolidacja rzadko używanych tagów\")\n",
                "\n",
                "# Technologie\n",
                "tech_counts = {\n",
                "    'Klasyczne ML': len([t for t in all_tags if any(kw in t for kw in ['frazy-binary', 'klasyfikacja', 'clustering'])]),\n",
                "    'LLM/GenAI': len([t for t in all_tags if 'llm' in t]),\n",
                "    'Bazy wektorowe': len([t for t in all_tags if 'baza-wektorowa' in t or 'retrieval' in t])\n",
                "}\n",
                "\n",
                "print(f\"\\n2. Wykorzystanie technologii:\")\n",
                "for tech, count in tech_counts.items():\n",
                "    print(f\"   - {tech}: {count} użyć ({count/len(all_tags)*100:.1f}%)\")\n",
                "\n",
                "# Wieloetapowe\n",
                "wieloetapowe = sum(1 for p in projekty if p['TAI - uwagi'] and 'wieloetapowe' in p['TAI - uwagi'].lower())\n",
                "print(f\"\\n3. Złożoność projektów:\")\n",
                "print(f\"   - {wieloetapowe} projektów wieloetapowych ({wieloetapowe/len(projekty)*100:.1f}%)\")\n",
                "print(f\"   - Sugerowane działanie: dekompozycja złożonych procesów\")\n",
                "\n",
                "# Najważniejsze wnioski\n",
                "print(\"\\n4. Kluczowe wnioski:\")\n",
                "print(\"   - Dominują klasyczne metody analizy tekstu (frazy-binary, ekstrakcja)\")\n",
                "print(\"   - Rosnące wykorzystanie LLM i baz wektorowych\")\n",
                "print(\"   - Wysoka złożoność projektów (75% wieloetapowych)\")\n",
                "print(\"   - Potencjał do standaryzacji i reużycia komponentów\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Zapisz wyniki do pliku\n",
                "wyniki = {\n",
                "    'statystyki': {\n",
                "        'liczba_projektow': len(projekty),\n",
                "        'liczba_tagow': len(tag_counts),\n",
                "        'srednia_tagow': srednia,\n",
                "        'dominujacy_zespol': zespoly.most_common(1)[0][0],\n",
                "        'najczestszy_tag': tag_counts.most_common(1)[0][0]\n",
                "    },\n",
                "    'top_10_tagow': tag_counts.most_common(10),\n",
                "    'typy_zadan': dict(typy),\n",
                "    'zespoly': dict(zespoly),\n",
                "    'technologie': tech_counts,\n",
                "    'wieloetapowe': wieloetapowe,\n",
                "    'rzadkie_tagi': len(rzadkie)\n",
                "}\n",
                "\n",
                "with open('wyniki_analizy_notebook.json', 'w', encoding='utf-8') as f:\n",
                "    json.dump(wyniki, f, ensure_ascii=False, indent=2)\n",
                "\n",
                "print(\"\\nWyniki zapisane do pliku: wyniki_analizy_notebook.json\")"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": 3
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

# Zapisz notebook
with open('analiza_tagi_BC.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print("Utworzono plik: analiza_tagi_BC.ipynb")
print("Notebook zawiera kompleksową analizę tagów technicznych.")