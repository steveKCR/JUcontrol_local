# Changelog

Alle nennenswerten Änderungen werden hier dokumentiert.

Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
Versionierung nach [SemVer](https://semver.org/lang/de/).

## [1.0.1] - 2026-04-30

### Geändert

- Leckageschutz-**Ventil** durch einen **Schalter** „Wasser an/aus“ ersetzt:
  **Ein** = API „Leckageschutz öffnen“ (Wasser fließt), **Aus** = „schließen“ (abgesperrt).
- Der Aktivitätsverlauf nutzt damit die üblichen Zustände **eingeschaltet/ausgeschaltet**
  statt Ventil „geöffnet/geschlossen“ (klarere Zuordnung zur Wasserführung).
- Beim Update wird die alte Ventil-Entität aus der Entity Registry entfernt; der Zustand
  wird wie zuvor nach Neustart aus der Home-Assistant-Historie wiederhergestellt.

## [1.0.0] - 2026-04-30

### Hinzugefügt

Komplett neu gebaut: schlanke, fokussierte Integration speziell für den
**JUDO i-soft K SAFE+** Wasserenthärter.

**Sensoren** (alle aktiv standardmäßig):
- Aktueller Durchfluss (L/h, abgeleitet aus Polling-Delta, mit `VOLUME_FLOW_RATE` device class)
- Gesamtwassermenge (m³ + L) – beide Energy-Dashboard-kompatibel
- Enthärtetes Wasser (m³ + L)
- Salzreichweite (Tage)
- Salzvorrat (kg)
- Aktuelle Wasserhärte (°dH)

**Steuerelemente:**
- Wunschwasserhärte als **Dropdown** (1–30 °dH) mit Read-Back
- Leckageschutz öffnen/schließen (Ventil)

**Architektur:**
- Nur 10 REST-API-Befehle, keine ungenutzten Codepfade
- Standard-Pollingintervall 30 s (anstatt 60 s)
- HTTP 429 mit 2-s-Retry
- Saubere Konfiguration: lehnt nicht-i-soft-K-SAFE+ Geräte ab
