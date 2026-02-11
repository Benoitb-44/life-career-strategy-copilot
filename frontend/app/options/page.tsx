"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { frontendApi, type OptionCard } from "@/lib/api";
import { useFlowStore } from "@/lib/flow-store";

export default function OptionsPage() {
  const router = useRouter();
  const { state, selectOption, setChecklist } = useFlowStore();
  const [selectedId, setSelectedId] = useState(state.selectedOption?.id ?? "");
  const [error, setError] = useState("");
  const [isSubmitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!state.entryAnswer) {
      router.replace("/entry");
      return;
    }

    if (!state.goal.northStar || state.options.length === 0) {
      router.replace("/goal-framing");
    }
  }, [router, state.entryAnswer, state.goal.northStar, state.options.length]);

  async function onContinue() {
    if (!selectedId) {
      setError("Sélectionne une option pour continuer.");
      return;
    }

    setError("");
    setSubmitting(true);

    try {
      const selected = state.options.find((option) => option.id === selectedId) as OptionCard;
      const checklist = await frontendApi.fetchChecklist(selected);
      selectOption(selected);
      setChecklist(checklist.items);
      router.push("/checklist");
    } catch {
      setError("Impossible de générer la checklist.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="panel">
      <h1>Options</h1>
      <p>Choisis une option stratégique (max 3 proposées).</p>
      <div className="cards">
        {state.options.slice(0, 3).map((option) => (
          <button
            key={option.id}
            type="button"
            className={`card ${selectedId === option.id ? "selected" : ""}`}
            onClick={() => setSelectedId(option.id)}
          >
            <strong>{option.title}</strong>
            <p>{option.description}</p>
          </button>
        ))}
      </div>
      {error && <p className="error">{error}</p>}
      <button type="button" onClick={onContinue} disabled={isSubmitting}>
        {isSubmitting ? "Chargement..." : "Continuer vers checklist"}
      </button>
    </section>
  );
}
