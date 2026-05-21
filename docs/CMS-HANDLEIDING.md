# Handleiding: Content beheren via het CMS

## Inloggen

1. Ga naar **https://ducroq.github.io/sanderveen.art/admin/**
2. Klik op **"Sign in with Token"**
3. Plak je token (begint met `github_pat_...`) en bevestig
4. Je komt nu in het dashboard

### Token verlopen? Nieuw token aanmaken

1. Ga naar **https://github.com/settings/tokens?type=beta** (log in met je GitHub account)
2. Klik op **"Generate new token"**
3. Vul in:
   - **Token name:** `sanderveen-cms`
   - **Expiration:** 90 days
   - **Repository access:** "Only select repositories" → kies `ducroq/sanderveen.art`
   - **Permissions → Repository permissions → Contents:** Read and write
4. Klik op **"Generate token"**
5. **Kopieer het token** — je ziet het maar 1x! Sla het verder **nergens** op (niet in een notitie, niet in een mail). Plak het direct in het CMS.
6. Ga terug naar het CMS en log in met dit token
7. **Verwijder het oude token:** ga terug naar https://github.com/settings/tokens?type=beta, klik op het vorige `sanderveen-cms` token en klik **Delete**. Anders blijft dat token actief tot zijn vervaldatum.

## Een nieuw schilderij toevoegen

Een schilderij toevoegen doe je **twee keer**: één keer in het Nederlands en daarna één keer in het Engels. Beide versies moeten dezelfde **vertaalsleutel** krijgen, anders werkt de taalwissel op de site niet.

### Stap 1 — Nederlandse versie

1. Klik links op **Schilderijen (NL)**
2. Klik rechtsboven op **New Schilderijen**
3. Vul de velden in (in deze volgorde, zoals ze in het formulier staan):
   - **Titel** — naam van het schilderij
   - **Datum** — laat staan op vandaag
   - **Draft** — laat uit (anders verschijnt het schilderij niet op de site)
   - **Vertaalsleutel** — een korte unieke naam, alleen kleine letters en streepjes, bijv. `bosbrand` of `horizon-in-de-lente`. **Onthoud deze sleutel** — je hebt 'm zo nodig bij de Engelse versie.
   - **Techniek** — bijv. "Olieverf op doek", "Acryl op paneel"
   - **Afmetingen** — bijv. "80 x 60 cm"
   - **Jaar** — wanneer het gemaakt is (mag leeg)
   - **Status** — available (te koop), sold (verkocht), of not-for-sale
   - **Uitgelicht** — aan als het op de homepage moet staan
   - **Afbeelding** — upload de foto van het schilderij (zie regels hieronder), of kies een al geüploade foto uit de mediabibliotheek
   - **Categorie** — Abstract of Surrealistisch
   - **Beschrijving** — optionele extra tekst onder het schilderij (mag leeg)
4. Klik op **Publish**

### Stap 2 — Engelse versie (verplicht!)

1. Klik links op **Paintings (EN)**
2. Klik rechtsboven op **New Paintings**
3. Vul dezelfde gegevens in, maar dan in het Engels:
   - **Title** — Engelse naam van het schilderij
   - **Date** — laat staan op vandaag (zelfde als de NL versie)
   - **Draft** — laat uit
   - **Translation key** — **exact dezelfde** vertaalsleutel als de Nederlandse versie. Tik 'm letter voor letter over.
   - **Medium** — bijv. "Oil on canvas"
   - **Dimensions** — bijv. "80 x 60 cm"
   - **Year** — zelfde jaartal als de NL versie (mag leeg)
   - **Status / Featured / Image** — moeten gelijk zijn aan de NL versie (dezelfde foto)
   - **Category** — kies volgens deze regel: koos je NL **Abstract** → kies EN **Abstract**. Koos je NL **Surrealistisch** → kies EN **Surrealist**. Iets anders breekt de bouwcheck en het schilderij verschijnt niet.
4. Klik op **Publish**

> **Vergeet je de Engelse versie?** Dan slaat het schilderij op, maar verschijnt het niet correct op de site en de bouwcheck (CI) zal klagen. Pak altijd beide talen in één sessie.

### Regels voor afbeeldingsbestanden

Het CMS controleert nu automatisch dat foto's een schone bestandsnaam hebben. Zorg er dus voor dat het bestand vóór upload de volgende format heeft:

- **Alleen kleine letters, cijfers en streepjes** in de naam
- **Geen spaties, geen hoofdletters, geen leestekens** (geen komma's, geen punten in de naam)
- **Eindigt op `.jpg`, `.jpeg`, `.png` of `.webp`**

Voorbeelden:
- **Goed:** `bosbrand.jpg`
- **Goed:** `horizon-in-de-lente.jpg`
- **Goed:** `stijl-in-compositie-3.jpg`
- **Niet goed:** `Bosbrand, 60x60cm.jpg` (spaties, hoofdletter, komma)
- **Niet goed:** `Stijl in compositie 3, 113x68cm. 1.jpg` (idem)

Als de bestandsnaam niet klopt, krijg je een rode foutmelding bij het opslaan en kan je het niet publiceren tot je de foto opnieuw uploadt met een geldige naam.

**Tip:** Upload de foto bij voorkeur direct binnen het schilderij-formulier (klik op het **Afbeelding**-veld) in plaats van vooraf via de Media Library — dan komt het bestand meteen op de juiste plek terecht.

## Een bestaand schilderij bewerken

1. Klik links op **Schilderijen (NL)**
2. Klik op het schilderij dat je wilt aanpassen
3. Pas de velden aan
4. Klik op **Publish**

## Een schilderij als "verkocht" markeren

1. Open het schilderij
2. Verander **Status** naar **sold**
3. Klik op **Publish**

## Een workshop toevoegen of bewerken

1. Klik links op **Workshops (NL)**
2. Klik op een bestaande workshop om te bewerken, of maak een nieuwe aan
3. Vul titel, beschrijving, datum/tijd, locatie en prijs in. Onthoud de **Vertaalsleutel** — die heb je zo nodig.
4. De inhoud (tekst) kun je opmaken met vet, cursief en opsommingen
5. Klik op **Publish**
6. **Maak ook de Engelse versie aan:** klik links op **Workshops (EN)** → **New Workshops**, vul dezelfde gegevens in het Engels in, en gebruik **exact dezelfde** vertaalsleutel. Zonder Engelse versie werkt de taalwissel op de site niet.

## Een expositie toevoegen

1. Klik links op **Exposities (NL)**
2. Klik op **New Exposities**
3. Vul de gegevens in. Onthoud de **Vertaalsleutel** — die heb je zo nodig.
4. Upload een hoofdafbeelding
5. Bij **Galerijtje** kun je extra foto's toevoegen door op "Add" te klikken
6. Klik op **Publish**
7. **Maak ook de Engelse versie aan:** klik links op **Exhibitions (EN)** → **New Exhibitions**, vul dezelfde gegevens in het Engels in, en gebruik **exact dezelfde** vertaalsleutel. Zonder Engelse versie werkt de taalwissel op de site niet.

## De "Over mij" tekst aanpassen

1. Klik links op **Over mij (NL)**
2. Klik op **Over mij**
3. Pas de tekst aan
4. Klik op **Publish**

## Belangrijk om te weten

- **Na Publish:** het CMS slaat de wijziging op en de bouwserver begint automatisch. Na 1-2 minuten staat het op de site. Controleer op **https://ducroq.github.io/sanderveen.art/** of je schilderij/workshop/expositie er staat. Zie je 'm na 5 minuten nog niet? Vaakste oorzaak: de Engelse versie is nog niet gepubliceerd.
- Maak voor elk schilderij/workshop/expositie altijd ook een **Engelse versie** aan met dezelfde **vertaalsleutel**.
- Foto's worden het best geüpload als `.jpg` bestanden. Zorg dat de foto scherp en goed belicht is.
- Als je iets fout doet is dat geen probleem — alle wijzigingen worden bijgehouden. Stuur Jeroen een berichtje, hij kan het terugdraaien.
