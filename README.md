# JUDO Wasseraufbereitung

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/steveKCR/ha-judo-wasseraufbereitung)](https://github.com/steveKCR/ha-judo-wasseraufbereitung/releases)

Eine schlanke, **lokale** Home-Assistant-Integration für den **JUDO i-soft K SAFE+** Wasserenthärter. Kommuniziert direkt mit dem Gerät im LAN — keine Cloud, kein Server, keine Abhängigkeiten.

> Diese Integration ist gezielt nur für den i-soft K SAFE+ entwickelt und bewusst minimal gehalten.

---

## Features

- **100 % lokal** über die JUDO REST-API
- **Wunschwasserhärte als Dropdown** (1–30 °dH)
- **Wasser an/aus** (Schalter, Ein = fließt, Aus = abgesperrt)
- **Live-Durchfluss** (abgeleitet aus Polling-Delta)
- **Beide Wassermengen-Sensoren** in m³ und Litern
- **30-Sekunden-Polling** standardmäßig
- **Energy-Dashboard-kompatibel** (Wassermengen mit `WATER` device class)

## Entitäten

| Typ | Name | Bemerkung |
|---|---|---|
| Sensor | Aktueller Durchfluss | L/h, abgeleitet aus Polling-Delta |
| Sensor | Gesamtwassermenge | m³ |
| Sensor | Gesamtwassermenge (Liter) | L |
| Sensor | Enthärtetes Wasser | m³ |
| Sensor | Enthärtetes Wasser (Liter) | L |
| Sensor | Salzreichweite | Tage |
| Sensor | Salzvorrat | kg |
| Sensor | Aktuelle Wasserhärte | °dH |
| Select | Wunschwasserhärte | Dropdown 1–30 °dH |
| Switch | Wasser an/aus | Ein = Wasser fließt, Aus = Leckageventil zu |

## Voraussetzungen

- JUDO i-soft K SAFE+ mit JUDO Connectivity-Modul (Software-Version ≥ 3.20, Hardware-Version ≥ 4.0)
- Connectivity-Modul über LAN/WLAN im Heimnetzwerk
- Home Assistant ≥ 2024.4

## Installation

### Über HACS (empfohlen)

1. HACS öffnen → Integrationen → Menü oben rechts → **Benutzerdefinierte Repositories**
2. Repository: `https://github.com/steveKCR/ha-judo-wasseraufbereitung`
3. Kategorie: **Integration** → Hinzufügen
4. Anschließend „**JUDO Wasseraufbereitung**" suchen und installieren
5. Home Assistant neu starten

### Manuell

1. Den Ordner `custom_components/judo_wasseraufbereitung` aus dem Repository herunterladen
2. In den HA-Konfigurationsordner kopieren: `/config/custom_components/judo_wasseraufbereitung/`
3. Home Assistant neu starten

## Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. „JUDO Wasseraufbereitung" auswählen
3. Eingaben:
   - **IP-Adresse** des Connectivity-Moduls (z. B. `192.168.1.50`)
   - **Benutzername** (Standard: `admin`)
   - **Passwort** (Standard: `Connectivity`)
   - **Abfrageintervall** (Standard: 30 Sekunden)

## REST-API-Befehle

Die Integration verwendet ausschließlich diese 10 dokumentierten REST-Befehle:

| Cmd | Funktion |
|---|---|
| `0xFF` | Gerätetyp |
| `0x06` | Seriennummer |
| `0x01` | Software-Version |
| `0x51` | Wunschwasserhärte lesen |
| `0x30` | Wunschwasserhärte setzen |
| `0x56` | Salzvorrat (Gewicht + Reichweite) |
| `0x28` | Gesamtwassermenge |
| `0x29` | Enthärtetes Wasser |
| `0x3D` | Leckageschutz öffnen |
| `0x3C` | Leckageschutz schließen |

HTTP 429 (Gerät beschäftigt) wird mit einem 2-Sekunden-Retry abgefangen.

## Lizenz

MIT — siehe [LICENSE](LICENSE)
