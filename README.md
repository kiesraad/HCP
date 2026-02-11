# HCP (Hulpmiddel ControleProtocol)
[![Status checks](https://github.com/kiesraad/HCP/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/kiesraad/HCP/actions/workflows/test.yml?query=branch%3Amain)

Deze repository bevat scripts die als hulpmiddel dienen voor het uitvoeren van Onderdeel A van het [Controleprotocol Centraal Stembureau](https://www.kiesraad.nl/binaries/kiesraad/documenten/publicaties/2025/12/16/gr26-controleprotocol-centraal-stembureau/Kiesraad+GR26+Controleprotocol+CSB.pdf). De scripts worden door Wonderbit op het platform teluitslagen uitgevoerd, waarbij een geüploadde `.zip` met daarin het tellingsbestand (`.eml`) de trigger zijn.

## Hoe voer ik het controleprotocol uit?
De gemakkelijkste manier is met behulp van [`uv`](https://docs.astral.sh/uv/getting-started/installation/). Als `uv` geinstalleerd is, is `hcp` te draaien vanuit de root directory. Hiermee wordt automatisch het `.eml.xml` bestand uit het zip bestand gehaald dat door OSV2020-U of Abacus geproduceerd wordt om `hcp` over te draaien. Bijvoorbeeld:
```
uv run hcp definitieve-documenten_tk2060_gemeente_juinen-20600607-152117.zip
```
De output wordt weggeschreven in de directory van waaruit `hcp` aangeroepen is als `a.csv`, `b.csv` en `c.csv`.

Het is ook mogelijk om `hcp` direct op een uitgepakt EML bestand te draaien. Bijvoorbeeld:

```
uv run hcp Telling_GR2026_Juinen_DSO.eml.xml
```

---
De code is ook direct vanuit Python aan te roepen. De functie `create_csv_files` in `main.py` is het ingangspunt voor de code. Parameters voor het aanroepen van deze functie zijn:

- `path_to_xml`: het pad naar het `.eml.xml` bestand waarover je de controle uit wilt voeren. Dit is dus een EML tellingsbestand (`id=510[a-dqrs]`)
- `dest_a`, `dest_b`, `dest_c`: paden waar respectievelijk controlebestanden `a`, `b` en `c` weggeschreven moeten worden. De precieze inhoud van deze bestanden wordt hieronder beschreven
- `path_to_neighbourhood_data`: optionele parameter, pad naar wijkdata in `.parquet` of `.csv` formaat. In `data/` staat het meest recente beschikbare bestand. (CBS update deze eens in de zoveel tijd, dus deze zal niet altijd 100% up-to-date zijn).

## Lijst met controles
Hieronder een korte beschrijving van de controles die onderdeel zijn van HCP. Deze zijn geïmplementeerd in `protocol_checks.py` en worden aangeroepen in `EML::run_protocol` in `eml.py`.

| Naam controle | Beschrijving | Output |
|---------------|--------------|--------|
| `check_zero_votes` | Controleert of het totaal aantal stemmen (getelde + ongeldige + blanco stemmen) gelijk is aan 0 | In `b.csv` een "ja" in de kolom "Stembureau met nul stemmen" bij stembureaus waar dit het geval is |
| `check_vote_difference` | Berekent het verschil tussen het aantal toegelaten kiezers en het aantal uitgebrachte stemmen in de EML en geeft deze waarde terug | In `a.csv` het resultaat van deze berekening in de kolom `Niet onderzocht telverschil` *mits het GSB niet heeft aangevinkt dat dat stembureau is onderzocht vanwege een onverklaard verschil (DSO) of dat de toegelaten kiezers opnieuw zijn vastgesteld (CSO)* |
| `check_too_many_rejected_votes` | Controleert of het *percentage* blanco of ongeldige stemmen ten opzichte van het totaal aantal *uitgebrachte* stemmen groter of gelijk is aan een in te stellen percentage. | In `b.csv` een "ja (`{percentage}`%)" in de bijbehorende kolom bij stembureaus waar dit het geval is
| `check_too_many_differences` | Controleert of het absolute verschil tussen toegelaten kiezers ten het totaal aantal uitgebrachte stemmen groter of gelijk is aan een in te stellen percentage *of* absoluuut aantal. | In `b.csv` een "ja (`{percentage}`%)" of "ja (`{aantal}`)" in de bijbehorende kolom bij stembureaus waar dit het geval is
| `check_parties_with_large_percentage_difference` | Controleert of er partijen zijn die bij een stembureau een percentage stemmen heeft behaald dat ten minste een in te stellen aantal percentagepunten verschilt van het gemiddelde in die *gemeente*. Voor de berekening van het gemiddelde in die gemeente wordt het betreffende stembureau niet meegenomen | In `b.csv` de namen van de partijen waarvoor dit het geval is, gescheiden door een komma bij de stembureaus waar dit het geval is
| `check_potentially_switched_candidates` | Controleert of voorkeursstemmen tussen twee kandidaten op dezelfde lijst mogelijk verwisseld zijn. Dat wil zeggen dat een van de kandidaten veel meer (in te stellen hoeveel) stemmen heeft gekregen dan verwacht terwijl een ander veel minder gekregen heeft dan verwacht. Hierbij kunnen stembureaus welke in de voorspelling te veel ruis hebben om een goede controle te doen uitgesloten worden (in te stellen in `eml_types::SwitchedCandidateConfig`) | In `b.csv` de paren kandidaten waarvoor dit het geval is, gescheiden door een `, ` in het formaat: *"Mogelijke verwisseling op lijst `i` (`lijstnaam`). Kandidaat `j` had `v_j` stemmen maar verwachting was `e_j`. Kandidaat `k` had `v_k` stemmen maar verwachting was `e_k`"*