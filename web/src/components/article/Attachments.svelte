<script lang="ts">
  import type { Attachment } from "../../lib/api";
  import { extension, kind, size } from "../../lib/files";

  type Props = { files: Attachment[]; onpreview: (file: Attachment) => void };
  let { files, onpreview }: Props = $props();

  // A plain click previews a stored image, PDF or DOCX; other clicks keep the browser's tabs and
  // link menu, which save the school's file.
  function click(event: MouseEvent, file: Attachment): void {
    const previewed = kind(file);
    if (!previewed || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    // iOS reports a PDF viewer but draws a framed PDF as a still picture of its first page.
    const inline = navigator.pdfViewerEnabled && !matchMedia("(pointer: coarse)").matches;
    if (previewed === "pdf" && !inline) window.open(file.file!, "_blank", "noopener");
    else onpreview(file);
  }
</script>

<ul class="files">
  {#each files as file, index (index)}
    {@const type = extension(file)}
    <li>
      <a class="file" href={file.url} target="_blank" rel="noopener noreferrer" onclick={(event) => click(event, file)}>
        {#if type}<span class="ext">{type}</span>{/if}
        <span class="name">{file.name}{#if file.size !== null}<small>{size(file.size)}</small>{/if}</span>
      </a>
    </li>
  {/each}
</ul>

<style>
  .files {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(min(100%, 260px), 1fr));
    gap: 10px;
  }
  .file {
    box-sizing: border-box;
    height: 100%;
    display: flex;
    gap: 12px;
    align-items: center;
    padding: 12px 14px;
    border-radius: 10px;
    background: var(--bg);
    color: inherit;
    text-decoration: none;
  }
  .file:hover {
    background: var(--accent-soft);
  }
  .ext {
    flex: none;
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--accent);
    border: 1.5px solid currentColor;
    border-radius: 4px;
    padding: 2px 5px;
    min-width: 3.4em;
    text-align: center;
  }
  .name {
    min-width: 0;
    font-size: var(--text-sm);
    overflow-wrap: anywhere;
    line-height: 1.4;
  }
  small {
    display: block;
    color: var(--ink-3);
    font-size: var(--text-xs);
    margin-top: 2px;
  }
</style>
