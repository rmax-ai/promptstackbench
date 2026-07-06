export const VERSION = "v0.1.0";
export const REPO = "https://github.com/rmax-ai/promptstackbench";

export const TAXONOMY_LAYERS = [
  {
    id: "persona",
    label: "Persona",
    description: "Role and interaction style. Easy to write, good UX — but hidden assumptions, weak reproducibility, role drift.",
    bestFor: "Low-risk tasks where voice matters",
    borderClass: "border-l-slate-700",
    complexity: 1,
  },
  {
    id: "lens",
    label: "Lens",
    description: "Constrained viewpoint. Sharper than persona, less theatrical — but still no defined procedure.",
    bestFor: "Tasks needing a stable perspective",
    borderClass: "border-l-slate-600",
    complexity: 2,
  },
  {
    id: "skill",
    label: "Skill",
    description: "Procedure + output schema. Interpretable, testable, reusable. The default unit of reliable work.",
    bestFor: "Repeatable, reviewable tasks with known output shape",
    borderClass: "border-l-slate-500",
    complexity: 3,
  },
  {
    id: "agent",
    label: "Agent",
    description: "Tools + state + multi-step reasoning. Useful when tasks require search, branching, or external action.",
    bestFor: "Tasks requiring tools, state, or multi-step search",
    borderClass: "border-l-indigo-600",
    complexity: 4,
  },
  {
    id: "harness",
    label: "Harness",
    description: "Guards + retry + audit trail. The evaluation and control layer. Highest implementation complexity.",
    bestFor: "Compliance, safety, production actions, audit requirements",
    borderClass: "border-l-indigo-400",
    complexity: 5,
  },
];

export const METRICS = [
  { code: "COR", label: "Correctness", desc: "Does the output solve the task?", category: "Final-answer" },
  { code: "CMP", label: "Completeness", desc: "Does it cover all necessary aspects?", category: "Final-answer" },
  { code: "CLR", label: "Clarity", desc: "Is the response well-structured and readable?", category: "Final-answer" },
  { code: "REL", label: "Relevance", desc: "Is every part relevant to the task?", category: "Final-answer" },
  { code: "SCH", label: "Schema Validity", desc: "Does output match expected structure?", category: "Final-answer" },
  { code: "HAL", label: "Hallucination", desc: "Are claims grounded or fabricated?", category: "Final-answer" },
  { code: "STB", label: "Stability", desc: "Does it hold under paraphrase perturbations?", category: "Robustness" },
  { code: "VAR", label: "Run Variance", desc: "How consistent across repeated runs?", category: "Robustness" },
];

export const QUICKSTART_COMMANDS = [
  { cmd: "uv sync --extra dev", comment: "# Install dependencies" },
  { cmd: "uv run promptstackbench init", comment: "# Initialize workspace" },
  { cmd: "uv run promptstackbench run --suite architecture_review --treatments persona,lens,skill --mock", comment: "# Run benchmark" },
  { cmd: "uv run promptstackbench report --run-id <id> --format html", comment: "# Generate report" },
];

export const STACK = ["Python 3.12+", "Typer CLI", "Pydantic v2", "SQLite", "Jinja2", "SvelteKit"];
