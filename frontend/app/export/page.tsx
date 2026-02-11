"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { frontendApi } from "@/lib/api";
import { useFlowStore } from "@/lib/flow-store";

export default function ExportPage() {
  const router = useRouter();
  const { state, reset } = useFlowStore();
  const [downloadUrl, setDownloadUrl] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setLoading] = useState(false);

  useEffect(() => {
    if (!state.entryAnswer) {
      router.replace("/entry");
      return;
    }
    if (!state.selectedOption || state.checklist.length === 0) {
      router.replace("/checklist");
    }
  }, [router, state.checklist.length, state.entryAnswer, state.selectedOption]);

  async function handleGenerateExport() {
    if (!state.selectedOption) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const blob = await frontendApi.exportPlan({
        entryAnswer: state.entryAnswer,
        goal: state.goal,
        option: state.selectedOption,
        checklist: state.checklist,
      });
      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);
    } catch {
      setError("Export indisponible pour le moment.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <h1>Export</h1>
      <p>Télécharge ton plan final.</p>
      <div className="row">
        <button type="button" onClick={handleGenerateExport} disabled={isLoading}>
          {isLoading ? "Génération..." : "Générer le fichier"}
        </button>
        <button type="button" className="secondary" onClick={() => { reset(); router.push('/entry'); }}>
          Recommencer
        </button>
      </div>
      {downloadUrl && (
        <p>
          <a href={downloadUrl} download="career-strategy-plan.txt">
            Télécharger le plan
          </a>
        </p>
      )}
      {error && <p className="error">{error}</p>}
    </section>
  );
}
