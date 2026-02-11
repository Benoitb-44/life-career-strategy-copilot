"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { frontendApi } from "@/lib/api";
import { useFlowStore } from "@/lib/flow-store";

export default function GoalFramingPage() {
  const router = useRouter();
  const { state, setGoal, setOptions } = useFlowStore();
  const [northStar, setNorthStar] = useState(state.goal.northStar);
  const [constraints, setConstraints] = useState(state.goal.constraints);
  const [error, setError] = useState("");
  const [isSubmitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!state.entryAnswer) {
      router.replace("/entry");
    }
  }, [router, state.entryAnswer]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();

    if (!northStar.trim() || !constraints.trim()) {
      setError("Tous les champs sont obligatoires.");
      return;
    }

    setError("");
    setSubmitting(true);

    try {
      const goal = { northStar: northStar.trim(), constraints: constraints.trim() };
      const [{ framingId }, options] = await Promise.all([
        frontendApi.frameGoal(goal),
        frontendApi.fetchOptions({ ...goal, entryAnswer: state.entryAnswer }),
      ]);
      setGoal(goal, framingId);
      setOptions(options.slice(0, 3));
      router.push("/options");
    } catch {
      setError("Erreur lors de la génération des options.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="panel">
      <h1>Goal Framing</h1>
      <form onSubmit={onSubmit}>
        <label>
          North Star
          <input
            value={northStar}
            onChange={(event) => setNorthStar(event.target.value)}
            placeholder="Ex: devenir Head of Product en 12 mois"
          />
        </label>
        <label>
          Contraintes
          <textarea
            value={constraints}
            onChange={(event) => setConstraints(event.target.value)}
            placeholder="Ex: rester basé à Paris, conserver un équilibre familial"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Chargement..." : "Voir les options"}
        </button>
      </form>
    </section>
  );
}
