"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useFlowStore } from "@/lib/flow-store";

export default function ChecklistPage() {
  const router = useRouter();
  const { state } = useFlowStore();

  useEffect(() => {
    if (!state.entryAnswer) {
      router.replace("/entry");
      return;
    }

    if (!state.selectedOption) {
      router.replace("/options");
    }
  }, [router, state.entryAnswer, state.selectedOption]);

  return (
    <section className="panel">
      <h1>Checklist</h1>
      <p>Plan d'action pour: {state.selectedOption?.title}</p>
      <ul>
        {state.checklist.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <button type="button" onClick={() => router.push("/export")}>
        Continuer vers export
      </button>
    </section>
  );
}
