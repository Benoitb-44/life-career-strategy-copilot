"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { GoalFormData, OptionCard } from "@/lib/api";

type FlowState = {
  entryAnswer: string;
  sessionId: string;
  goal: GoalFormData;
  framingId: string;
  options: OptionCard[];
  selectedOption?: OptionCard;
  checklist: string[];
};

const initialState: FlowState = {
  entryAnswer: "",
  sessionId: "",
  goal: { northStar: "", constraints: "" },
  framingId: "",
  options: [],
  selectedOption: undefined,
  checklist: [],
};

type FlowContextValue = {
  state: FlowState;
  setEntry: (entryAnswer: string, sessionId: string) => void;
  setGoal: (goal: GoalFormData, framingId: string) => void;
  setOptions: (options: OptionCard[]) => void;
  selectOption: (option: OptionCard) => void;
  setChecklist: (checklist: string[]) => void;
  reset: () => void;
};

const FlowContext = createContext<FlowContextValue | undefined>(undefined);

export function FlowProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<FlowState>(initialState);

  useEffect(() => {
    const raw = localStorage.getItem("career-flow-state");
    if (raw) {
      setState(JSON.parse(raw) as FlowState);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("career-flow-state", JSON.stringify(state));
  }, [state]);

  const value = useMemo<FlowContextValue>(
    () => ({
      state,
      setEntry: (entryAnswer, sessionId) =>
        setState((prev) => ({ ...prev, entryAnswer, sessionId })),
      setGoal: (goal, framingId) =>
        setState((prev) => ({ ...prev, goal, framingId })),
      setOptions: (options) =>
        setState((prev) => ({ ...prev, options, selectedOption: undefined, checklist: [] })),
      selectOption: (option) => setState((prev) => ({ ...prev, selectedOption: option })),
      setChecklist: (checklist) => setState((prev) => ({ ...prev, checklist })),
      reset: () => setState(initialState),
    }),
    [state],
  );

  return <FlowContext.Provider value={value}>{children}</FlowContext.Provider>;
}

export function useFlowStore() {
  const context = useContext(FlowContext);
  if (!context) {
    throw new Error("useFlowStore must be used inside FlowProvider");
  }

  return context;
}
