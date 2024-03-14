# HCP (Hulpmiddel ControleProtocol)
[![Status checks](https://github.com/kiesraad/HCP/actions/workflows/checks.yml/badge.svg?branch=master)](https://github.com/kiesraad/HCP/actions/workflows/checks.yml?query=branch%3Amaster)

Deze repository bevat de scripts die het controleprotocol voor uitslagen op Gemeentelijk StemBureau (GSB) niveau uitvoeren. De scripts worden door Wonderbit op het DOB platform uitgevoerd, waarbij een geüploadde `.zip` met tellingsbestanden en eventuele proces verbalen in `.odt` formaat de trigger zijn. Natuurlijk kunnen de scripts ook handmatig uitgevoerd worden om controles uit te voeren.

## Hoe voer ik het controleprotocol uit?
De functie `create_csv_files` in `main.py` is het ingangspunt voor de code. Parameters voor het aanroepen van deze functie zijn:

- `path_to_xml`: het pad naar het `.eml.xml` bestand waarover je de controle uit wilt voeren. Dit is dus een EML tellingsbestand (`id=510[a-dqrs]`)
- `dest_a`, `dest_b`, `dest_c`: paden waar respectievelijk controlebestanden `a`, `b` en `c` weggeschreven moeten worden. De precieze inhoud van deze bestanden wordt hieronder beschreven
- `path_to_odt`: optionele parameter, pad naar een proces verbaal in `.odt` formaat. Geldige bestanden zijn `Model_Na31-1.odt` voor een decentrale- en `Model_Na31-2.odt` voor een centrale stemopneming.
- `path_to_neighbourhood_data`: optionele parameter, pad naar wijkdata in `.parquet` of `.csv` formaat. In `data/` staat het het meest recente beschikbare bestand. (CBS update deze eens in de zoveel tijd, dus deze zal niet altijd 100% up-to-date zijn).

## Lijst met controles
Hieronder een korte beschrijving van de controles die onderdeel zijn van HCP. Deze zijn geïmplementeerd in `protocol_checks.py` en worden aangeroepen in `EML::run_protocol` in `eml.py`.

| Naam controle | Beschrijving | Output |
|---------------|--------------|--------|
| `check_zero_votes` | Controleert of het totaal aantal stemmen (getelde + ongeldige + blanco stemmen) gelijk is aan 0 | In `b.csv` een "ja" in de kolom "Stembureau met nul stemmen" bij stembureaus waar dit het geval is |
| `check_inexplicable_difference` | Geeft de waarde terug die ingevuld is onder 'geen verklaring' in de EML | In `a.csv` een waarde in de kolom "Aantal geen verklaring voor verschil" bij stembureaus *mits deze ongelijk is aan 0* |
| `check_explanation_sum_difference` | Geeft het verschil tussen (het totaal aantal stemmen en het aantal toegelaten kiezers) en de som van de ingevulde verklaringen. Dus bij 6 stemmen, 5 toegelaten kiezers en een som van verklaringen van 0 is deze waarde 1 (`(6-5) - 0`) | In `a.csv` het aantal dat uit deze verschilberekening komt in de kolom "Aantal ontbrekende verklaringen voor verschil" *mits deze ongelijk is aan 0*
| `check_too_many_rejected_votes` | Controleert of het *percentage* blanco of ongeldige stemmen ten opzichte van het totaal aantal *uitgebrachte* stemmen groter of gelijk is aan een in te stellen percentage. | In `b.csv` een "ja (`{percentage}`%)" in de bijbehorende kolom bij stembureaus waar dit het geval is
| `check_too_many_differences` | Controleert of het absolute verschil tussen toegelaten kiezers ten het totaal aantal uitgebrachte stemmen groter of gelijk is aan een in te stellen percentage *of* absoluuut aantal. | In `b.csv` een "ja (`{percentage}`%)" of "ja (`{aantal}`)" in de bijbehorende kolom bij stembureaus waar dit het geval is
| `check_parties_with_large_percentage_difference` | Controleert of er partijen zijn die bij een stembureau een percentage stemmen heeft behaald dat ten minste een in te stellen aantal percentagepunten verschilt van het gemiddelde in die *gemeente*. Voor de berekening van het gemiddelde in die gemeente wordt het betreffende stembureau niet meegenomen | In `b.csv` de namen van de partijen waarvoor dit het geval is, gescheiden door een komma bij de stembureaus waar dit het geval is
| `check_potentially_switched_candidates` | Controleert of voorkeursstemmen tussen twee kandidaten op dezelfde lijst mogelijk verwisseld zijn. Dat wil zeggen dat een van de kandidaten veel meer (in te stellen hoeveel) stemmen heeft gekregen dan verwacht terwijl een ander veel minder gekregen heeft dan verwacht. | In `b.csv` de paren kandidaten waarvoor dit het geval is, gescheiden door een nieuwe regel (`\n`) in het formaat: *"Mogelijke verwisseling op lijst `i` (`lijstnaam`). Kandidaat `j` had `v_j` stemmen maar verwachting was `e_j`. Kandidaat `k` had `v_k` stemmen maar verwachting was `e_k`"*

## .odt verwerking
Naast de checks die hierboven beschreven zijn, kan ook het proces-verbaal dat bij een telbestand meegeleverd wordt geparsed worden. Het doel hiervan is om stembureau's te identificeren die al een hertelling uitgevoerd hebben. Als dit het geval is, dan wordt in `a.csv` de waarde "x of ja" toegevoegd aan de kolom "Al hergeteld". In alle gevallen moet zowel het nummer als de naam van het stembureau genoteerd staan om zeker te weten dat we deze koppelen aan het juiste stembureau in de EML. Is deze koppeling om welke reden dan ook niet mogelijk, dan gaan we er van uit dat er **niet** herteld is.

De informatie is afkomstig uit:
#### [Model_Na31-1.odt](https://www.rijksoverheid.nl/onderwerpen/verkiezingen/documenten/publicaties/2022/11/18/model-na-31-1)
Stembureaus die onder **3b.** of **3c.** genoteerd staan.

#### [Model_Na31-2.odt](https://www.rijksoverheid.nl/onderwerpen/verkiezingen/documenten/publicaties/2022/11/18/model-na-31-2)
Stembureaus die onder **7.** genoteerd staan.

