"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { frontendApi } from "@/lib/api";
import { useFlowStore } from "@/lib/flow-store";

export default function EntryPage() {
  const router = useRouter();
  const { state, setEntry } = useFlowStore();
  const [answer, setAnswer] = useState(state.entryAnswer);
  const [isSubmitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!answer.trim()) {
      setError("Merci de répondre à la question.");
      return;
    }

    setError("");
    setSubmitting(true);

    try {
      const { sessionId } = await frontendApi.submitEntry(answer.trim());
      setEntry(answer.trim(), sessionId);
      router.push("/goal-framing");
    } catch {
      setError("Impossible de démarrer le flow pour le moment.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="panel">
      <h1>Entry</h1>
      <p>Quelle décision de carrière veux-tu clarifier dans les 90 prochains jours ?</p>
      <form onSubmit={onSubmit}>
        <textarea
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          placeholder="Ex: Dois-je rester dans mon poste actuel ou pivoter ?"
        />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Chargement..." : "Continuer"}
        </button>
      </form>
    </section>
  );
}
