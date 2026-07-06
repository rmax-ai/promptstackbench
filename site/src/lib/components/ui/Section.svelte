<script lang="ts">
  let { id = "", class: klass = "", children }: { id?: string; class?: string; children?: import("svelte").Snippet } = $props();
</script>

<section {id} class="py-24 px-4 sm:px-6 {klass}">
  <div class="max-w-5xl mx-auto">
    {@render children?.()}
  </div>
</section>
