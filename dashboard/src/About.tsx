import {
  ArrowRight,
  Database,
  MailSearch,
  Network,
  UserCheck,
} from "lucide-react";
import { ErrorBox, useQuery } from "./ui";

export function About() {
  const catalog = useQuery<{ live_ai_enabled: boolean }>(
    "/api/demo/catalog",
    0,
  );
  return (
    <div className="about-page">
      <section className="purpose-hero">
        <div>
          <span className="eyebrow">DAS PROJEKT IN EINEM SATZ</span>
          <h1>
            Von „Die Lieferung kommt später“ zu einer konkreten Entscheidung.
          </h1>
          <p>
            Normalerweise muss jemand die Meldung lesen, Aufträge durchsuchen,
            Folgen abschätzen und die nächsten Schritte abstimmen. Dieses
            Projekt verbindet diese Arbeitsschritte in einem nachvollziehbaren
            Ablauf.
          </p>
        </div>
      </section>
      <div className="about-steps">
        {[
          {
            icon: MailSearch,
            title: "Gemini liest die Mail",
            text: "Die KI erkennt gemeldetes Material, Mengen und Termine in einem frei formulierten Text. Übernommene Angaben müssen zur Mail und zu den vorhandenen Betriebsdaten passen. Unklare Angaben gehen zur Prüfung.",
          },
          {
            icon: Database,
            title: "Das System prüft die Folgen",
            text: "Bestände, Liefertermine, Maschinenzeiten und Aufträge werden miteinander verglichen. Daraus entstehen die betroffenen Aufträge und Fehlmengen. Diese Berechnung ist regelbasiert.",
          },
          {
            icon: Network,
            title: "n8n verbindet die Schritte",
            text: "Die Workflows nehmen die Meldung entgegen, starten Auswertung und Berechnung, bereiten Aktionen vor und warten auf die nötige Freigabe.",
          },
          {
            icon: UserCheck,
            title: "Ein Mensch entscheidet",
            text: "Einkauf, Produktionsleitung oder Qualitätsmanagement prüfen die vorgeschlagene Reaktion. Freigegebene Änderungen und ihre Ergebnisse werden nachvollziehbar gespeichert.",
          },
        ].map(({ icon: Icon, title, text }, i) => (
          <article key={title}>
            <span className="case-icon">
              <Icon size={25} />
            </span>
            <small>0{i + 1}</small>
            <h2>{title}</h2>
            <p>{text}</p>
          </article>
        ))}
      </div>
      <section className="plain-panel">
        <h2>Was läuft hier tatsächlich?</h2>
        {catalog.error && <ErrorBox error={catalog.error} />}
        <p>
          <b>Die drei Beispielfälle</b> zeigen gespeicherte Analysen mit
          erfundenen Aufträgen. Durchblättern löst weder eine KI-Auswertung noch
          eine Freigabe aus.
        </p>
        <p>
          <b>Eigene Mail mit Gemini:</b>{" "}
          {catalog.data
            ? catalog.data.live_ai_enabled
              ? "Für angemeldete Team-Mitglieder aktiviert. Eine neu eingereichte Beispiel-Mail wird tatsächlich an Gemini zur Auswertung übergeben."
              : "In dieser Umgebung zurzeit nicht aktiviert. Die Online-Beispielfälle belegen deshalb keinen Live-KI-Aufruf."
            : "Der aktuelle Betriebsstatus wird geladen."}
        </p>
        <p>
          <b>Maschinen- und Qualitätsmeldungen</b> liegen bereits als
          strukturierte Daten vor. Dafür ist keine KI-Texterkennung nötig.
        </p>
        <a className="button primary" href="#/mail">
          Zur Mail-Auswertung <ArrowRight size={16} />
        </a>
      </section>
      <section className="plain-panel">
        <h2>Welche Aufgabe haben die anderen Dienste?</h2>
        <p>
          <b>Supabase</b> speichert Betriebsdaten, Meldungen, Entscheidungen und
          Ergebnisse in PostgreSQL. <b>Vercel</b> stellt die Weboberfläche und
          API bereit. Die angebundenen ERP-Daten sind für dieses Portfolio
          erfunden.
        </p>
        <a className="text-link" href="#/reliability">
          Verarbeitung und technische Nachweise ansehen <ArrowRight size={16} />
        </a>
      </section>
    </div>
  );
}
