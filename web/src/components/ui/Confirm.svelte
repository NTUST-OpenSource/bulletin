<script lang="ts">
  import { ui } from "../../state.svelte";

  let dialog: HTMLDialogElement;

  $effect(() => {
    if (ui.question && !dialog.open) dialog.showModal();
  });

  function answer(yes: boolean): void {
    const question = ui.question;
    ui.question = null;
    dialog.close();
    question?.answer(yes);
  }
</script>

<dialog
  class="confirm"
  bind:this={dialog}
  aria-labelledby="confirm-title"
  oncancel={(event) => {
    event.preventDefault();
    answer(false);
  }}
>
  <div>
    <h2 id="confirm-title">{ui.question?.title}</h2>
    <p>{ui.question?.text}</p>
    <div class="row-btns">
      <button type="button" class="btn ghost" onclick={() => answer(false)}>{ui.question?.no}</button>
      <button type="button" class="btn primary" onclick={() => answer(true)}>{ui.question?.yes}</button>
    </div>
  </div>
</dialog>

<style>
  .confirm {
    width: min(380px, calc(100vw - 32px));
    border-radius: 14px;
  }
  .confirm > div {
    padding: 22px 22px 18px;
    display: grid;
    gap: 10px;
  }
  h2 {
    margin: 0;
    font-size: var(--text-md);
  }
  p {
    margin: 0;
    font-size: var(--text-sm);
    color: var(--ink-2);
  }
  .row-btns {
    justify-content: flex-end;
    margin-top: 8px;
  }
</style>
