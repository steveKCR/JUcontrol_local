# JUcontrol local

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-yellow.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/itsh-neumeier/JUcontrol_local)](https://github.com/itsh-neumeier/JUcontrol_local/releases)

Eine **rein lokale** Home Assistant Integration für JUDO Wasseraufbereitungsgeräte. Kommuniziert direkt mit dem Gerät in Ihrem lokalen Netzwerk — keine Cloud-Abhängigkeit.

---

## Funktionen

- **100% Lokal** — Kommuniziert direkt über die REST-API des Geräts im LAN
- **Automatische Erkennung** — Erkennt automatisch das angeschlossene JUDO Gerätemodell
- **Vollständige Sensorunterstützung** — Wasserhärte, Salzvorrat, Wassermengen, Betriebsstunden und mehr
- **Gerätesteuerung** — Regeneration starten, Leckageschutz umschalten, Urlaubsmodus, Einstellungen anpassen
- **Konfigurierbares Polling** — Wählen Sie Ihr Abfrageintervall: 30 s, 1 min, 2 min, 5 min oder 10 min
- **Mehrsprachig** — Englische und deutsche Übersetzungen enthalten
- **Diagnose** — Integrierte Diagnoseunterstützung zur Fehlerbehebung

---

## Unterstützte Geräte

| Gerät | Typ | Funktionen |
|---|---|---|
| **i-soft SAFE+** / **i-soft K SAFE+** | Enthärter | Enthärtung, Leckageschutz, Salzüberwachung |
| **i-soft PRO** / **i-soft PRO L** | Enthärter | Enthärtung, Leckageschutz, Szenen |
| **i-soft** / **i-soft K** | Enthärter | Enthärtung, Leckagealarm |
| **SOFTwell P / S / K / KP / KS** | Enthärter | Basis-Enthärtung, Statistiken |
| **ZEWA i-SAFE** / **PROM-i-SAFE** / **ZEWA i-SAFE FILT** | Leckageschutz | Eigenständiger Leckageschutz, Abwesenheitsverwaltung |
| **i-dos eco** | Dosierpumpe | Chemische Dosierung, Pumpensteuerung |
| **i-fill 60** | Heizungsbefüllung | Heizkreisbefüllung, Ventilsteuerung |

---

## Installation

### HACS (Empfohlen)

1. Öffnen Sie **HACS** in Ihrer Home Assistant Instanz.
2. Klicken Sie auf die drei Punkte oben rechts und wählen Sie **Benutzerdefinierte Repositories**.
3. Fügen Sie `https://github.com/itsh-neumeier/JUcontrol_local` als **Integration** hinzu.
4. Suchen Sie nach **JUcontrol local** und klicken Sie **Herunterladen**.
5. Starten Sie Home Assistant neu.

### Manuelle Installation

1. Laden Sie das neueste Release von [GitHub Releases](https://github.com/itsh-neumeier/JUcontrol_local/releases) herunter.
2. Kopieren Sie den Ordner `custom_components/jucontrol_local` in Ihr Home Assistant `config/custom_components/` Verzeichnis.
3. Starten Sie Home Assistant neu.

---

## Konfiguration

1. Gehen Sie zu **Einstellungen** > **Geräte & Dienste** > **Integration hinzufügen**.
2. Suchen Sie nach **JUcontrol local**.
3. Geben Sie Ihre Gerätedaten ein:

| Parameter | Beschreibung | Standard |
|---|---|---|
| **Host** | IP-Adresse Ihres JUDO Geräts | *(erforderlich)* |
| **Benutzername** | API-Benutzername | `admin` |
| **Passwort** | API-Passwort | `Connectivity` |
| **Abfrageintervall** | Wie oft das Gerät abgefragt wird | `1 Minute` |

4. Die Integration erkennt automatisch Ihr Gerätemodell und erstellt die entsprechenden Entitäten.

### Abfrageintervall ändern

Nach der Einrichtung können Sie das Abfrageintervall jederzeit ändern:

1. Gehen Sie zu **Einstellungen** > **Geräte & Dienste**.
2. Finden Sie Ihr JUDO Gerät und klicken Sie auf **Konfigurieren**.
3. Wählen Sie ein neues Abfrageintervall und speichern Sie.

---

## Verfügbare Entitäten

Entitäten werden automatisch basierend auf dem erkannten Gerätetyp und seinen Fähigkeiten erstellt. Nicht alle Entitäten sind für jedes Gerätemodell verfügbar.

### Sensoren

| Entität | Beschreibung | Gerätetypen |
|---|---|---|
| Wasserhärte | Aktuelle Wunschwasserhärte (°dH) | i-soft Varianten |
| Salzvorrat | Aktuelles Salzgewicht (kg) | i-soft Varianten |
| Salzreichweite | Geschätzte Salzreichweite (Tage) | i-soft Varianten |
| Salzmangelwarnung | Warnschwelle (Tage) | i-soft Varianten |
| Gesamtwassermenge | Gesamter Wasserverbrauch (m³) | Die meisten Geräte |
| Weichwassermenge | Produziertes Weichwasser (m³) | Enthärter |
| Betriebstage | Gesamte Betriebstage | Alle Geräte |
| Aktueller Durchfluss | Aktueller Wasserdurchfluss (L/h) | i-dos eco |
| Restmenge im Behälter | Verbleibende Dosiermittelmenge (L) | i-dos eco |
| Max. Fülldruck | Maximaler Fülldruck (bar) | i-fill 60 |
| Patronentyp | Installierter Patronentyp | i-fill 60 |

### Buttons

| Entität | Beschreibung | Gerätetypen |
|---|---|---|
| Regeneration starten | Löst einen manuellen Regenerationszyklus aus | i-soft Varianten |
| Meldung zurücksetzen | Setzt aktive Meldungen zurück | ZEWA i-SAFE |
| Mikroleckageprüfung starten | Führt eine Mikroleckage-Erkennung durch | ZEWA i-SAFE |
| Lernmodus starten | Startet den Lernmodus | ZEWA i-SAFE |

### Switches

| Entität | Beschreibung | Gerätetypen |
|---|---|---|
| Leckageschutz | Schließt/öffnet das Leckageschutzventil | i-soft SAFE+, ZEWA |
| Sleepmodus | Aktiviert/deaktiviert den Sleepmodus | ZEWA i-SAFE |

### Selects

| Entität | Optionen | Gerätetypen |
|---|---|---|
| Urlaubsmodus | Aus, U1, U2, U3 | i-soft Varianten, ZEWA |
| Härteeinheit | °dH, °eH, °fH, gpg, ppm, mmol, mval | i-soft Varianten |
| Pumpenbetriebsart | Aus, Automatik, Manuell, Einzel | i-dos eco |
| Füllventilmodus | Automatik, Manuell öffnen, Manuell schließen | i-fill 60 |
| Mikroleckage-Modus | Deaktiviert, Nur Melden, Melden und Schließen | ZEWA i-SAFE |

### Numbers

| Entität | Bereich | Gerätetypen |
|---|---|---|
| Wunschwasserhärte | 1–30 °dH | i-soft Varianten |
| Salzvorrat (setzen) | 0–50.000 g | i-soft Varianten |
| Salzmangelwarnung (setzen) | 1–90 Tage | i-soft Varianten |
| Max. Entnahmedauer | 0–255 min | i-soft Varianten |
| Max. Entnahmemenge | 0–65.535 L | i-soft Varianten |
| Max. Volumenstrom | 0–65.535 L/h | i-soft Varianten |
| Sleepmodusdauer | 1–10 h | ZEWA i-SAFE |

### Binärsensoren

| Entität | Beschreibung | Gerätetypen |
|---|---|---|
| Lernmodus aktiv | Ob der Lernmodus gerade aktiv ist | ZEWA i-SAFE |

---

## Netzwerkanforderungen

- Das JUDO Gerät muss sich im **gleichen lokalen Netzwerk** wie Ihre Home Assistant Instanz befinden.
- Die Kommunikation verwendet **HTTP** (Port 80) mit **Basic Authentication**.
- Es ist keine Internetverbindung erforderlich — die gesamte Kommunikation ist lokal.

---

## Integrations-Branding (HA 2026.3+)

Diese Integration liefert die Branding-Dateien jetzt direkt lokal mit:

`custom_components/jucontrol_local/brand/`

Enthaltene Dateien:

- `icon.png`
- `icon@2x.png`
- `logo.png`
- `logo@2x.png`

Home Assistant ordnet die Bilder ueber die Domain (`jucontrol_local`) zu und laedt diese Dateien automatisch.
Ein eigenes Logo pro einzelnes Geraet wird nicht ueber `device_info` gesetzt; sichtbare Bilder kommen aus dem Integrations-Branding.

Schneller Test in Home Assistant:

- `/api/brands/integration/jucontrol_local/icon.png`
- `/api/brands/integration/jucontrol_local/logo.png`

Wenn Datei, Pfad oder Domain nicht passen, liefert Home Assistant ein Standard-Platzhalterbild zurueck.

---

## Automatisierungsbeispiel: Salzvorrat

Die folgende Automation sendet sofort eine Benachrichtigung, wenn die `Salzreichweite` auf oder unter die in `Salzmangelwarnung` gesetzte Anzahl Tage faellt.
Zusätzlich erinnert sie taeglich um `09:00` erneut, bis der Salzvorrat wieder ueber dem gesetzten Grenzwert liegt.

Passe vor dem Einfuegen bitte die Entity-IDs und den Benachrichtigungsdienst an dein System an:

```yaml
alias: JUcontrol Salzvorrat Erinnerung
description: Meldet niedrigen Salzvorrat sofort und danach taeglich, solange der Grenzwert unterschritten ist.
mode: single
trigger:
  - platform: state
    entity_id:
      - sensor.jucontrol_local_salzreichweite
      - sensor.jucontrol_local_salzmangelwarnung
  - platform: time
    at: "09:00:00"
condition:
  - condition: template
    value_template: >
      {{ states('sensor.jucontrol_local_salzreichweite') | float(999) <=
         states('sensor.jucontrol_local_salzmangelwarnung') | float(0) }}
action:
  - service: notify.notify
    data:
      title: JUcontrol Salzvorrat
      message: >
        Salz nachfuellen. Verbleibende Salzreichweite:
        {{ states('sensor.jucontrol_local_salzreichweite') }} Tage.
        Grenzwert Salzmangelwarnung:
        {{ states('sensor.jucontrol_local_salzmangelwarnung') }} Tage.
```

Wenn du den Grenzwert direkt in Home Assistant anpassen moechtest, nutze die Number-Entitaet
`Salzmangelwarnung (setzen)`. Sobald die `Salzreichweite` wieder groesser als die aktuelle
`Salzmangelwarnung` ist, stoppt die taegliche Erinnerung automatisch.

---

## Fehlerbehebung

| Problem | Lösung |
|---|---|
| **Verbindung nicht möglich** | Überprüfen Sie die IP-Adresse und stellen Sie sicher, dass das Gerät eingeschaltet ist. Stellen Sie sicher, dass Home Assistant das Gerät erreichen kann (gleiches VLAN/Subnetz). |
| **Ungültige Authentifizierung** | Überprüfen Sie Benutzername und Passwort. Standard-Anmeldedaten sind `admin` / `Connectivity`. |
| **Unbekanntes Gerät** | Der Gerätetyp wird noch nicht unterstützt. Bitte öffnen Sie ein Issue auf GitHub mit Ihrem Gerätemodell. |
| **Entitäten aktualisieren nicht** | Überprüfen Sie das Abfrageintervall in den Integrationsoptionen. Überprüfen Sie die Netzwerkverbindung zum Gerät. |
| **Entitäten zeigen "nicht verfügbar"** | Das Gerät ist möglicherweise vorübergehend nicht erreichbar. Überprüfen Sie Ihr Netzwerk und den Gerätestatus. |

---

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md) für eine vollständige Versionshistorie.

---

## Mitwirken

Beiträge sind willkommen! Bitte:

1. Forken Sie das Repository.
2. Erstellen Sie einen Feature-Branch (`git checkout -b feature/mein-feature`).
3. Committen Sie Ihre Änderungen nach [Conventional Commits](https://www.conventionalcommits.org/).
4. Pushen Sie Ihren Branch und öffnen Sie einen Pull Request.

Wenn Sie ein JUDO Gerätemodell haben, das noch nicht unterstützt wird, öffnen Sie bitte ein Issue mit dem Gerätetyp-Code (über die Diagnose der Integration ablesbar).

---

## Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert — siehe die [LICENSE](LICENSE) Datei für Details.

---

## Haftungsausschluss

Diese Integration ist **nicht mit JUDO Wasseraufbereitung GmbH verbunden, wird nicht von ihr unterstützt oder ist mit ihr assoziiert**. JUDO, i-soft, SOFTwell, ZEWA, i-dos und i-fill sind Marken der JUDO Wasseraufbereitung GmbH. Die Nutzung dieser Integration erfolgt auf eigene Gefahr.
