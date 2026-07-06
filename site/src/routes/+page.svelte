<script lang="ts">
  import Section from "$lib/components/ui/Section.svelte";
  import { TAXONOMY_LAYERS, METRICS, QUICKSTART_COMMANDS, STACK, VERSION, REPO } from "$lib/data/meta";

  let activeLayer = $state<string | null>(null);
  let copied = $state(false);

  function copyCommands() {
    const text = QUICKSTART_COMMANDS.map((c) => c.cmd).join("\n");
    navigator.clipboard.writeText(text);
    copied = true;
    setTimeout(() => (copied = false), 2000);
  }
</script>

<svelte:head>
  <title>PromptStackBench — Taxonomy Evaluation Harness</title>
  <meta name="description" content="Evaluate when a persona should become a skill, when a skill should become an agent, and when an agent needs a harness." />
</svelte:head>

<!-- Hero -->
<Section klass="pt-32 pb-20">
  <div class="text-center">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-slate-800 bg-slate-900/50 text-xs font-mono text-slate-500 mb-8">
      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
      {VERSION}
    </div>
    <h1 class="text-4xl sm:text-5xl font-semibold tracking-tight text-slate-50 mb-6">
      PromptStack<span class="text-indigo-400">Bench</span>
    </h1>
    <p class="text-lg text-slate-400 max-w-2xl mx-auto mb-4 leading-relaxed">
      Evaluate when a persona should become a skill,
      when a skill should become an agent,
      and when an agent needs a harness.
    </p>
    <p class="text-sm text-slate-500 max-w-xl mx-auto mb-10">
      Run the same task through five control abstractions.
      Compare answer quality, groundedness, stability, cost, latency, and promotion value.
      Know when each layer pays for itself.
    </p>
    <p class="text-sm text-slate-500 max-w-xl mx-auto mb-10">
      Today the runnable benchmark focuses on persona, lens, and skill.
      Richer agent and harness execution models are planned rather than fully implemented.
    </p>
    <div class="flex items-center justify-center gap-4">
      <a href={REPO} class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors">
        View on GitHub
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.387.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.73.083-.73 1.205.085 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.418-1.305.762-1.604-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12 24 5.37 18.63 0 12 0z"/></svg>
      </a>
      <a href="#quickstart" class="inline-flex items-center gap-2 border border-slate-800 hover:bg-slate-900 text-slate-300 px-5 py-2.5 rounded-lg text-sm font-medium transition-colors">
        Quickstart
      </a>
    </div>
  </div>

  <!-- Quickstart preview -->
  <div class="mt-16 max-w-2xl mx-auto">
    <div class="rounded-lg border border-slate-800 bg-black overflow-hidden">
      <div class="flex items-center gap-2 px-4 py-3 border-b border-slate-800">
        <span class="w-3 h-3 rounded-full bg-red-500/80"></span>
        <span class="w-3 h-3 rounded-full bg-amber-500/80"></span>
        <span class="w-3 h-3 rounded-full bg-emerald-500/80"></span>
        <span class="ml-2 text-xs font-mono text-slate-600">quickstart</span>
      </div>
      <pre class="p-4 text-xs font-mono text-slate-400 leading-relaxed overflow-x-auto">{#each QUICKSTART_COMMANDS as cmd}<span class="text-slate-600">$</span> {cmd.cmd}
{/each}</pre>
    </div>
  </div>
</Section>

<!-- Taxonomy Staircase -->
<Section id="taxonomy">
  <h2 class="text-2xl font-semibold tracking-tight text-slate-50 mb-2">
    The <span class="text-indigo-400">Taxonomy</span>
  </h2>
  <p class="text-slate-500 mb-12 max-w-xl">
    Five control abstractions, from lightweight role instructions to planned agent and harness runtimes.
    Each adds structure — and cost. The benchmark measures when the trade-off pays off.
  </p>

  <div class="relative">
    {#each TAXONOMY_LAYERS as layer, i}
      <div
        class="relative pl-8 pb-12 last:pb-0 group"
        onmouseenter={() => (activeLayer = layer.id)}
        onmouseleave={() => (activeLayer = null)}
      >
        <!-- Vertical thread -->
        {#if i < TAXONOMY_LAYERS.length - 1}
          <div class="absolute left-[11px] top-10 bottom-0 w-px bg-slate-800"></div>
        {/if}

        <!-- Node dot -->
        <div
          class="absolute left-0 top-2 w-[23px] h-[23px] rounded-full border-2 transition-colors duration-200 {activeLayer === layer.id ? 'border-indigo-500 bg-indigo-500/20' : 'border-slate-700'}"
        >
          <div
            class="absolute inset-1 rounded-full transition-colors {activeLayer === layer.id ? 'bg-indigo-400' : 'bg-slate-600'}"
          ></div>
        </div>

        <div
          class="border-l-2 rounded-r-lg p-5 transition-all duration-200 {layer.borderClass} {activeLayer === layer.id ? 'bg-indigo-500/5' : 'bg-transparent'}"
        >
          <div class="flex items-baseline gap-3 mb-2">
            <span class="font-mono text-xs text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">
              L{layer.complexity}
            </span>
            <h3 class="text-lg font-semibold text-slate-200">{layer.label}</h3>
            <span class="text-xs text-slate-600 font-mono hidden sm:inline">
              {layer.id}
            </span>
          </div>
          <p class="text-sm text-slate-400 leading-relaxed mb-2">{layer.description}</p>
          <p class="text-xs text-slate-600">
            <span class="text-slate-500">Best for:</span> {layer.bestFor}
          </p>
        </div>
      </div>
    {/each}
  </div>
</Section>

<!-- Metrics Grid -->
<Section id="metrics" klass="border-t border-slate-900">
  <h2 class="text-2xl font-semibold tracking-tight text-slate-50 mb-2">
    Evaluation <span class="text-indigo-400">Metrics</span>
  </h2>
  <p class="text-slate-500 mb-12 max-w-xl">
    Current scoring combines answer-quality checks, structure checks, and robustness summaries.
    Tokens, latency, and cost are reported alongside those scores.
  </p>

  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
    {#each METRICS as metric}
      <div
        class="group border border-slate-800 bg-slate-900/30 p-4 rounded-lg hover:border-indigo-500/50 transition-colors duration-200 {activeLayer && activeLayer !== 'persona' ? 'border-indigo-500/30' : ''}"
      >
        <div class="flex items-center gap-2 mb-2">
          <span class="font-mono text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-indigo-400">
            {metric.code}
          </span>
          <h4 class="text-sm font-medium text-slate-300">{metric.label}</h4>
        </div>
        <p class="text-xs text-slate-500 leading-relaxed">{metric.desc}</p>
        <p class="text-[10px] text-slate-600 mt-2 font-mono">{metric.category}</p>
      </div>
    {/each}
  </div>
</Section>

<!-- Example Report -->
<Section klass="border-t border-slate-900">
  <h2 class="text-2xl font-semibold tracking-tight text-slate-50 mb-2">
    Example <span class="text-indigo-400">Report</span>
  </h2>
  <p class="text-slate-500 mb-8 max-w-2xl">
    This preview is based on a real generated HTML report from run
    <span class="font-mono text-slate-400">2026-07-06-202054</span>. It shows the current
    report shape more accurately than a fabricated benchmark-run terminal demo.
  </p>

  <div class="rounded-lg border border-slate-800 bg-black overflow-hidden max-w-3xl">
    <div class="flex items-center justify-between px-4 py-3 border-b border-slate-800">
      <span class="text-xs font-mono text-slate-600">report preview</span>
      <span class="text-xs font-mono text-slate-600">report_2026-07-06-202054.html</span>
    </div>
    <pre class="p-4 text-xs font-mono text-slate-300 leading-relaxed overflow-x-auto">PromptStackBench Report
Run ID: 2026-07-06-202054
Suite: architecture_review
Model: gpt-4.1

Summary

persona: senior_architect_persona
  correctness: 9.50
  completeness: 9.00
  clarity: 9.00
  relevance: 10.00
  schema_validity: 8.00
  avg tokens: 713
  avg latency: 8679ms
  avg cost: $0.0067

skill: architecture_review_skill
  correctness: 10.00
  completeness: 9.00
  clarity: 9.00
  relevance: 10.00
  schema_validity: 5.00
  avg tokens: 586
  avg latency: 8515ms
  avg cost: $0.0048

Promotion signals
  persona -> lens: quality -13.1%, cost +6.9%
  lens -> skill: quality +11.5%, cost -32.5%

Per-task scores
  arch_review_001: persona 9.14, skill 8.86, lens 7.86
  arch_review_002: persona 9.43, skill 9.14, lens 8.29</pre>
  </div>
</Section>

<!-- How It Works -->
<Section klass="border-t border-slate-900">
  <h2 class="text-2xl font-semibold tracking-tight text-slate-50 mb-12 text-center">
    How It <span class="text-indigo-400">Works</span>
  </h2>

  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div class="text-center p-6 rounded-lg border border-slate-800 bg-slate-900/30">
      <div class="w-10 h-10 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto mb-4">
        <span class="font-mono text-sm text-indigo-400">1</span>
      </div>
      <h3 class="font-medium text-slate-200 mb-2">Load</h3>
      <p class="text-sm text-slate-500">Define task suites and taxonomy specs in YAML, then initialize a fresh workspace directory for each example run.</p>
    </div>
    <div class="text-center p-6 rounded-lg border border-slate-800 bg-slate-900/30">
      <div class="w-10 h-10 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto mb-4">
        <span class="font-mono text-sm text-indigo-400">2</span>
      </div>
      <h3 class="font-medium text-slate-200 mb-2">Run</h3>
      <p class="text-sm text-slate-500">Execute each task through each treatment with configurable repetitions and paraphrases. Outputs are stored in SQLite.</p>
    </div>
    <div class="text-center p-6 rounded-lg border border-slate-800 bg-slate-900/30">
      <div class="w-10 h-10 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto mb-4">
        <span class="font-mono text-sm text-indigo-400">3</span>
      </div>
      <h3 class="font-medium text-slate-200 mb-2">Compare</h3>
      <p class="text-sm text-slate-500">Generate HTML or Markdown reports with scores, robustness summaries, and promotion signals.</p>
    </div>
  </div>
</Section>

<!-- Quickstart -->
<Section id="quickstart" klass="border-t border-slate-900">
  <h2 class="text-2xl font-semibold tracking-tight text-slate-50 mb-2">
    <span class="text-indigo-400">Quickstart</span>
  </h2>
  <p class="text-slate-500 mb-8 max-w-xl">
    Install, initialize, and run your first mock benchmark in a repo-local workspace.
  </p>

  <div class="relative max-w-2xl">
    <div class="rounded-lg border border-slate-800 bg-black overflow-hidden">
      <div class="flex items-center justify-between px-4 py-3 border-b border-slate-800">
        <span class="text-xs font-mono text-slate-600">terminal</span>
        <button
          onclick={copyCommands}
          class="text-xs font-mono text-slate-500 hover:text-slate-300 transition-colors"
        >
          {copied ? "copied!" : "copy"}
        </button>
      </div>
      <pre class="p-4 text-sm font-mono text-slate-300 leading-relaxed overflow-x-auto">
{#each QUICKSTART_COMMANDS as cmd}
<span class="text-slate-600">$</span> {cmd.cmd}  <span class="text-slate-600">{cmd.comment}</span>
{/each}</pre>
    </div>
  </div>

  <div class="flex flex-wrap gap-2 mt-6">
    {#each STACK as item}
      <span class="text-xs font-mono text-slate-600 bg-slate-900/50 border border-slate-800 px-2 py-1 rounded">{item}</span>
    {/each}
  </div>
</Section>

<!-- Footer -->
<footer class="border-t border-slate-900 mt-20 py-10">
  <div class="max-w-5xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-2 text-xs text-slate-600">
      <span class="font-mono">{VERSION}</span>
      <span class="text-slate-800">|</span>
      <span>MIT License</span>
      <span class="text-slate-800">|</span>
      <span>Built with Python + SvelteKit</span>
    </div>
    <div class="flex items-center gap-4">
      <a href={REPO} class="text-xs text-slate-500 hover:text-slate-300 transition-colors flex items-center gap-1.5">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.387.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.73.083-.73 1.205.085 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.418-1.305.762-1.604-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12 24 5.37 18.63 0 12 0z"/></svg>
        rmax-ai/promptstackbench
      </a>
    </div>
  </div>
</footer>
