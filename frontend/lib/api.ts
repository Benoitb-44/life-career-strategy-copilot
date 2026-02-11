export type GoalFormData = {
  northStar: string;
  constraints: string;
};

export type OptionCard = {
  id: string;
  title: string;
  description: string;
};

type ChecklistResponse = {
  items: string[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const useMock = (process.env.NEXT_PUBLIC_USE_MOCK ?? "true") === "true";

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new Error(`API error ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function mockDelay<T>(value: T): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(value), 250);
  });
}

export const frontendApi = {
  submitEntry(questionAnswer: string): Promise<{ sessionId: string }> {
    if (useMock) {
      return mockDelay({ sessionId: `mock-${questionAnswer.length || 1}` });
    }

    return request("/context", {
      method: "POST",
      body: JSON.stringify({ answer: questionAnswer }),
    });
  },

  frameGoal(payload: GoalFormData): Promise<{ framingId: string }> {
    if (useMock) {
      return mockDelay({ framingId: `frame-${payload.northStar.length || 1}` });
    }

    return request("/decision", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  fetchOptions(payload: GoalFormData & { entryAnswer: string }): Promise<OptionCard[]> {
    if (useMock) {
      return mockDelay([
        {
          id: "option-1",
          title: "Deepen current role",
          description: "Double down on scope expansion in your existing company.",
        },
        {
          id: "option-2",
          title: "External pivot",
          description: "Target a role switch aligned with your north star and constraints.",
        },
        {
          id: "option-3",
          title: "Portfolio approach",
          description: "Combine your current position with a strategic side project.",
        },
      ]);
    }

    return request("/bets", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  fetchChecklist(option: OptionCard): Promise<ChecklistResponse> {
    if (useMock) {
      return mockDelay({
        items: [
          `Clarify success criteria for \"${option.title}\"`,
          "Schedule 3 stakeholder conversations in week 1",
          "Block a 90-day execution cadence on your calendar",
        ],
      });
    }

    return request("/plan-generator", {
      method: "POST",
      body: JSON.stringify({ selected_option: option }),
    });
  },

  exportPlan(payload: {
    entryAnswer: string;
    goal: GoalFormData;
    option: OptionCard;
    checklist: string[];
  }): Promise<Blob> {
    if (useMock) {
      const content = [
        "Life/Career Strategy Plan",
        "",
        `Entry: ${payload.entryAnswer}`,
        `North star: ${payload.goal.northStar}`,
        `Constraints: ${payload.goal.constraints}`,
        `Selected option: ${payload.option.title}`,
        "",
        "Checklist:",
        ...payload.checklist.map((item, index) => `${index + 1}. ${item}`),
      ].join("\n");
      return mockDelay(new Blob([content], { type: "text/plain" }));
    }

    return fetch(`${apiBaseUrl}/plan-export-pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then(async (response) => {
      if (!response.ok) {
        throw new Error(`API error ${response.status}`);
      }
      return response.blob();
    });
  },
};
