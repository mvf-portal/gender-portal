#!/usr/bin/env python3
"""Alles Themenspezifische der taeglichen Studienauswahl — und sonst nichts.

Diese Datei ist die EINZIGE unter scripts/, die sich von Portal zu Portal
inhaltlich unterscheidet. `update_studies.py` bleibt in allen Portalen
wortgleich und importiert von hier. Wer die Auswahl aendern will, aendert
Text in dieser Datei — keinen Code.

Erzeugt von neues-portal.py aus dem Themenprofil `themen/gender.json`.
Weiterentwickelt wird danach hier, nicht im Profil.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------- Kennungen
# NCBI bittet bei automatisierten Zugriffen um eine Tool-Kennung.
NCBI_TOOL = "gender-portal"

# ----------------------------------------------------------- Die Suchabfrage
# Zwei Bloecke, die BEIDE zutreffen muessen. Ohne den zweiten spuelt die Abfrage
# Arbeiten herein, die das Thema nur streifen; ohne den ersten kommt beliebige
# Versorgungsliteratur.
#
# Zur Feldwahl: [MeSH Terms] fasst breit, [Majr] verlangt das Haupt-Schlagwort,
# [Title/Abstract] fasst am breitesten, [Title] am engsten. Faustregel aus den
# Schwesterportalen: Steht ein Begriff in fremden Abstracts als blosses Werkzeug
# oder Beiwerk, ist [Title/Abstract] untauglich — dann [Majr]/[Title]. Im
# KI-Portal sank die Trefferzahl dadurch von 605.000 auf 321.000, und erst die
# kleinere Menge handelte tatsaechlich vom Thema.
#
# Vor dem Livegang die Trefferzahl in PubMed nachsehen und hier notieren, damit
# spaetere Aenderungen messbar bleiben.
_THEMA = (
        "((((\"Sex Factors\"[Majr] OR \"Sex Characteristics\"[Majr] "
        "OR \"Gender Equity\"[Majr] OR \"Sexism\"[Majr] OR \"Gender Identity\"[Majr] "
        "OR \"Health Status Disparities\"[Majr]) "
        "OR (\"sex difference*\"[Title] OR \"gender difference*\"[Title] "
        "OR \"sex-specific\"[Title] OR \"gender-specific\"[Title] "
        "OR \"sex and gender\"[Title] OR \"gender medicine\"[Title] "
        "OR \"gender-sensitive\"[Title] OR \"gender sensitive\"[Title] "
        "OR \"sex-sensitive\"[Title] OR \"gender bias\"[Title] "
        "OR \"sex disparit*\"[Title] OR \"gender disparit*\"[Title] "
        "OR \"sex-based\"[Title] OR \"gender gap\"[Title] "
        "OR \"sex-stratified\"[Title])) "
        "OR (\"Women's Health\"[Majr] OR \"Men's Health\"[Majr] "
        "OR \"Women's Health Services\"[Majr] "
        "OR \"Sexual and Gender Minorities\"[Majr] OR \"Transgender Persons\"[Majr] "
        "OR \"Health Services for Transgender Persons\"[Majr]) "
        "OR (\"women's health\"[Title] OR \"men's health\"[Title] "
        "OR transgender[Title] OR \"gender-affirming\"[Title] "
        "OR \"gender affirming\"[Title] OR LGBTQ*[Title] "
        "OR \"sexual and gender minorit*\"[Title])) "
        "NOT (\"Aging\"[Majr] OR \"Longevity\"[Majr] OR \"Frailty\"[Majr] "
        "OR \"Geriatrics\"[Majr] "
        "OR \"Artificial Intelligence\"[Majr] OR \"Machine Learning\"[Majr] "
        "OR \"Telemedicine\"[Majr] "
        "OR \"Nursing\"[Majr] OR \"Nursing Care\"[Majr] OR \"Long-Term Care\"[Majr] "
        "OR \"Caregivers\"[Majr] "
        "OR \"Noncommunicable Diseases\"[Majr] OR \"Chronic Disease\"[Majr] "
        "OR \"Multimorbidity\"[Majr] "
        "OR \"Health Literacy\"[Majr] OR \"Climate Change\"[Majr] "
        "OR \"Vaccination\"[Majr] OR \"Vaccines\"[Majr]))"
)
_KONTEXT = (
        "(\"Delivery of Health Care\"[MeSH Terms] OR \"Health Services\"[MeSH Terms] "
        "OR \"Quality of Health Care\"[MeSH Terms] OR \"Patient Care\"[MeSH Terms] "
        "OR \"Health Policy\"[MeSH Terms] OR \"Public Health\"[MeSH Terms] "
        "OR \"health care\"[Title/Abstract] OR \"health services\"[Title/Abstract] "
        "OR \"patient outcome*\"[Title/Abstract] "
        "OR \"clinical practice\"[Title/Abstract] "
        "OR implementation[Title/Abstract] OR patients[Title/Abstract])"
)
# "Humans"[MeSH] haelt Tier-, Labor- und reine Modellarbeiten heraus.
TERM = os.environ.get(
    "SEARCH_TERM",
    f'(({_THEMA} AND {_KONTEXT}) AND "Humans"[MeSH Terms])',
)
# Zweite Abfrage, damit Arbeiten mit Deutschland- und Europabezug den
# Kandidatenpool sicher erreichen. Ueber MeSH und Autorenadresse, nicht ueber
# Journalnamen - deutschsprachige Journale liefern kaum Treffer.
TERM_DE = os.environ.get(
    "SEARCH_TERM_DE",
    f"{TERM} AND (Germany[MeSH Terms] OR Germany[Affiliation] "
    "OR Europe[MeSH Terms] OR Europe[Affiliation])",
)

# Groesse des Kandidatenpools. Europa steht vorn und stellt die Mehrheit -
# ein Sprachmodell gewichtet, was es zuerst liest. Wer das umdreht, bekommt
# eine Auswahl ohne Bezug zu hiesigen Verhaeltnissen; im Klima-Portal ist
# genau das passiert.
POOL_EUROPA = 30
POOL_ALLGEMEIN = 25
# Welche Abfrage vorn steht. True ist der Regelfall und die Lehre aus dem
# Klima-Portal: Steht die allgemeine Abfrage vorn, kommt eine Auswahl ohne
# Bezug zu hiesigen Verhaeltnissen heraus. Das Versorgungsforschungs-Portal
# arbeitet historisch andersherum (40 allgemein + 15 deutsch) - dort steht
# hier False, damit der Anschluss an die Vorlage nichts an seiner taeglichen
# Auswahl geaendert hat. Umstellen ist eine redaktionelle Entscheidung.
EUROPA_ZUERST = True

# Wie viele Studien taeglich erscheinen. SOLL wird im Prompt verlangt und beim
# Kappen verwendet; ueber MAX wird gekappt, unter MIN bricht der Lauf ab.
# **Nicht ins JSON-Schema schreiben** - die Anthropic-API lehnt minItems > 1
# und maxItems ab (am 17.08.2026 zweimal mit HTTP 400 belegt).
ANZAHL_SOLL = 6
ANZAHL_MAX = 7
ANZAHL_MIN = 5
# True: zu viele Studien werden auf ANZAHL_SOLL gekuerzt (die Auswahl ist nach
# Relevanz geordnet, die vorderen sind brauchbar). False: zu viele lassen den
# Lauf scheitern - so hielt es das Versorgungsforschungs-Portal von Anfang an.
KAPPEN = True

# ------------------------------------------------------------------- Prompts
SYSTEM = (
        "Du bist Fachredakteur fuer geschlechtersensible Medizin im "
        "Gesundheitswesen. Aus einer Liste von PubMed-Abstracts waehlst du "
        "die relevantesten aktuellen Studien aus und fasst sie praezise auf "
        "Deutsch zusammen. Deine Leserschaft arbeitet im deutschen "
        "Gesundheitswesen: Praxen, Kliniken, Kostentraeger, Selbstverwaltung "
        "und Gesundheitspolitik. Sie will wissen, wo Geschlecht das "
        "Behandlungsergebnis veraendert und woran das liegt - an der "
        "Biologie, am Zugang zur Versorgung oder daran, wie behandelt wird. "
        "Sie will NICHT eine weitere Arbeit ueber Geschlechterverhaeltnisse "
        "in der Wissenschaft, solange daraus nichts fuer die Versorgung folgt."
)

USER_TEMPLATE = """Unten stehen aktuelle PubMed-Abstracts (nach Datum sortiert).

Waehle GENAU 6 Studien aus, die (a) Geschlecht als Einflussgroesse in der Versorgung untersuchen - in Diagnostik, Therapie, Zugang, Arzneimittelwirkung oder Ergebnisqualitaet UND (b) im
Abstract ein BENENNBARES ERGEBNIS berichten. Bei quantitativen Arbeiten heisst
das: konkrete Zahlen (Prozentwerte, Effektstaerken, Odds/Hazard Ratios, Zeit-
oder Kostenwirkungen, Fallzahlen, p-Werte) - und die gehoeren dann auch in die
Zusammenfassung. Qualitative Studien (Interviews, Fokusgruppen) und
Expertenpapiere sind ausdruecklich zugelassen; bei ihnen tritt an die Stelle
der Zahl die klar benannte Kernaussage - welche Faktoren, welche Bedingungen,
welche Empfehlung. Was NICHT genuegt, ist ein Abstract, der nur ankuendigt,
was untersucht wurde, ohne zu sagen, was dabei herauskam.
Ueberspringe Studien ohne Abstract oder ohne benennbares Ergebnis. Achte auf
thematische Vielfalt und mische quantitative und qualitative Arbeiten.

THEMATISCHE RANGFOLGE - in dieser Reihenfolge bevorzugen:
      1. Arbeiten, die einen Geschlechterunterschied im Versorgungsergebnis
         zeigen UND eine Erklaerung dafuer pruefen (Zugangsweg, Diagnostik,
         Dosierung, Zuschreibung durch Behandelnde).
      2. Arbeiten, die eine Massnahme gegen einen bekannten Unterschied
         testen - geaenderte Leitlinie, angepasste Dosierung, eigene
         Sprechstunde, Schulung von Personal.
      3. Arbeiten mit belastbaren geschlechtergetrennten Routinedaten aus
         einem europaeischen Gesundheitssystem.
      4. Methodenarbeiten, die zeigen, wie Geschlecht ausgewertet gehoert -
         aber nur, wenn sie an einem konkreten Versorgungsbeispiel haengen.

NICHT in die Auswahl gehoeren:
reine Grundlagenarbeiten zu Hormonwirkung oder Genexpression ohne
Versorgungsbezug, Uebersichten, die nichts Eigenes berichten, Arbeiten, die
Geschlecht lediglich als Kontrollvariable mitfuehren, ohne es auszuwerten,
sowie Studien zur Gleichstellung in Wissenschaft und Karriere, solange sie
keine Folge fuer die Patientenversorgung benennen.

HARTE REGELN ZUR ZUSAMMENSETZUNG (sie gehen der thematischen Rangfolge vor):
      1. MINDESTENS DREI der sechs Studien muessen aus Europa stammen oder ein
         europaeisches Gesundheitssystem betreffen. Liegen weniger als drei
         solche Arbeiten vor, nimm die verbleibenden Plaetze aus dem Rest -
         aber schoepfe die europaeischen zuerst aus.
      2. HOECHSTENS ZWEI der sechs duerfen ausschliesslich Frauengesundheit im
         engeren Sinn betreffen - Schwangerschaft, Geburtshilfe, Gynaekologie.
         Dieses Material stellt den groessten Teil des Kandidatenpools; ohne
         Grenze waere der Hub binnen weniger Wochen ein Frauengesundheits-
         portal und nicht das, was er sein soll: ein Hub darueber, dass
         Geschlecht in JEDEM Fach eine Rolle spielt.
      3. HOECHSTENS EINE darf sich ausschliesslich mit Alter, Gebrechlichkeit
         oder Lebenserwartung befassen. Solche Arbeiten deckt das
         Schwesterportal longevity.m-vf.de ab; es ist der groesste Nachbar
         dieses Hubs.
      4. HOECHSTENS EINE darf eine digitale Anwendung oder ein Modell im
         Mittelpunkt haben (App, Algorithmus, Risikoscore, Sprachmodell).
         Dafuer gibt es ki.m-vf.de; zugelassen ist die Arbeit nur, wenn die
         Geschlechterfrage im Vordergrund steht, nicht die Technik.
      5. HOECHSTENS EINE darf einen Unterschied nur beschreiben, ohne eine
         Ursache, eine Massnahme oder eine Folge zu untersuchen. Dass es
         Unterschiede gibt, ist der Ausgangspunkt dieses Hubs, nicht sein
         Ergebnis.

ZWEITES AUSWAHLKRITERIUM - Übertragbarkeit auf Deutschland:
Bei sonst gleicher Qualität hat die übertragbare Studie IMMER Vorrang vor der
aktuelleren.

  Hoch:    Deutschland und deutschsprachiger Raum, vergleichbare Sozial-
           versicherungssysteme.
  Mittel:  Übriges Europa, Kanada, Australien - andere Ausgangslage,
           ähnlicher Versorgungsauftrag.
  Gering:  USA und Länder mit grundlegend anderer Finanzierung oder
           Ressourcenlage. Nur nehmen, wenn die Fragestellung davon
           unabhängig ist.

Besonderheit dieses Themenfeldes: Ein Geschlechterunterschied kann drei sehr verschiedene Ursachen haben - Biologie, Zugang zur Versorgung oder die Art, wie Beschwerden gedeutet werden. Sage im Feld transfer ausdruecklich, welche der drei die Arbeit tatsaechlich zeigt und welche sie nur vermutet; das ist die haeufigste Ueberdehnung in diesem Feld. Fuer die Uebertragbarkeit auf Deutschland zaehlen ausserdem der Zugangsweg (Facharztdirektzugang statt Gatekeeping), die Frage, ob Geschlecht in der einschlaegigen AWMF-Leitlinie ueberhaupt vorkommt, und die Datenlage: Deutschland hat keine Register mit der Qualitaet der skandinavischen, geschlechtergetrennte Routinedaten sind hier entsprechend schwerer zu bekommen. Ordne die Systeme nach Vergleichbarkeit: hoch bei DACH, Niederlanden, Belgien und Frankreich, mittel bei Skandinavien, Grossbritannien, Kanada und Australien, gering bei den USA, deren Zugangshuerden geschlechtsbezogene Unterschiede ueberlagern.

Fuer jede Studie:
- journal: Journalname genau so, wie er in der Kopfzeile des Abstracts steht -
  Abkuerzung nicht aufloesen, nichts ergaenzen. (Wird ohnehin durch die Angabe
  aus PubMed ersetzt; rate hier nichts.)
- year: Erscheinungsjahr, z. B. "2026"
- pmid: die PubMed-ID
- title: praegnanter deutscher Titel.
      **Er MUSS mit der Versorgungsfrage beginnen, nicht mit dem Geschlecht.**
      Faengt jede Zeile mit "Frauen" oder "Maenner" an, liest sich der Hub
      wie eine Aufzaehlung von Benachteiligungen statt wie eine
      Versorgungsanalyse - und der Unterschied, um den es geht, verschwindet
      hinter der Gruppe.
      Gut:      "Herzkatheter kam bei Frauen im Schnitt 47 Minuten spaeter"
      Schlecht: "Frauen mit Herzinfarkt: Neue Studie zeigt Unterschiede"
- sum: 1 Satz auf Deutsch, was die Studie untersucht hat. Wenn der genannte
  Anlassfall nur das Material ist, an dem gerechnet wurde, sage das
  ausdruecklich - sonst haelt die Leserschaft ihn fuer den Gegenstand.
- result: Deutsch, die konkreten Zahlen/Befunde + ein kurzer Einordnungssatz.
  Deutsches Zahlenformat mit Komma (z. B. 0,63). **Der Einordnungssatz darf
  nicht behaupten, was die Autoren selbst ablehnen.** Wo ein Abstract eine
  Deutung ausdruecklich zurueckweist, diese Einschraenkung uebernehmen statt
  sie zu ueberschreiben. Ein Rechercheportal referiert, es wertet nicht auf.
- transfer: EIN Halbsatz (höchstens 12 Wörter), warum das Ergebnis für Deutschland
  taugt - oder wo die Grenze liegt. Nenne Land bzw. System und Datengrundlage.
  Keine ganzen Sätze, keine Wiederholung des Titels.
  Gut:      "Deutsche Klinikdaten, vergleichbare Dokumentationspflichten"
            "Niederlande, vergleichbares Versicherungssystem"
            "USA - nur der Sicherheitsbefund ist übertragbar"
  Schlecht: "Diese Studie ist gut übertragbar." (sagt nichts)

WICHTIG - Fachterminologie: Etablierte englische Fachbegriffe NICHT eindeutschen.
Sie sind auch im deutschen Fachdeutsch stehende Begriffe; eine woertliche
Uebersetzung wirkt unprofessionell und erschwert das Wiederfinden.
Beispiele fuer Begriffe, die englisch bleiben: Gender Data Gap, Sex as a Biological Variable, Outcome, Screening, Baseline, Hazard Ratio, Public Health. Uebersetze dagegen, was im Deutschen eine gaengige Entsprechung hat: aus "sex differences" werden Geschlechterunterschiede, aus "sex-disaggregated data" geschlechtergetrennte Daten, aus "health care disparities" Versorgungsungleichheit, aus "gender-affirming care" geschlechtsangleichende Behandlung. Verwende "Geschlecht" fuer sex und "soziales Geschlecht" nur dort, wo die Arbeit die Unterscheidung selbst trifft - ein deutscher Text, der ueberall "Gender" schreibt, verliert genau die Genauigkeit, um die es diesem Hub geht.
Faustregel: Wuerde eine deutsche Fachzeitschrift wie Monitor Versorgungsforschung
den Begriff englisch stehen lassen, dann tue es auch. Im Zweifel englisch
belassen und bei Bedarf eine kurze deutsche Erlaeuterung in Klammern ergaenzen.

Gib ausschliesslich das geforderte JSON zurueck.

=== ABSTRACTS ===
{abstracts}
"""
