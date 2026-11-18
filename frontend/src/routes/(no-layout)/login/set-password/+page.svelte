<script lang="ts">
  import '../../../app.css';
  import '#lib/v2/styles/v2.css';
  import imgLogo from '#lib/assets/images/logo.png';
  import type { PageProps } from './$types';

  let { data, form }: PageProps = $props();
  let password = $state('');
  let confirmPassword = $state('');
  let submitting = $state(false);
</script>

<svelte:head>
  <title>Set password · Godan CRM</title>
  <meta name="description" content="Add a password to your Godan CRM account." />
  <meta name="referrer" content="same-origin" />
</svelte:head>

<div class="v2-root v2-auth">
  <div class="v2-auth-box">
    <a href="/" class="v2-auth-brand">
      <img src={imgLogo} alt="" />
      <b>Godan CRM</b>
    </a>
    <div class="v2-auth-card">
      {#if form?.success}
        <div class="v2-auth-head">
          <h1>Password added</h1>
          <p>Your password is now set. You can continue signing in with Google or use your email and password where available.</p>
        </div>
        <a href="/login" class="v2-btn v2-btn-primary v2-btn-block">Back to sign in</a>
      {:else}
        <div class="v2-auth-head">
          <h1>Set your password</h1>
          <p>Add a password as another way to access your Godan CRM account. Your Google sign-in will continue to work.</p>
        </div>
        {#if !data.uid || !data.token}
          <div class="v2-auth-note v2-auth-note-bad">This password setup link is incomplete. Request a new sign-in link and try again.</div>
        {:else}
          <form method="POST" onsubmit={() => (submitting = true)} style="display:flex;flex-direction:column;gap:12px">
            <label for="password">New password</label>
            <input id="password" name="password" type="password" class="v2-input" minlength="12" autocomplete="new-password" required bind:value={password} />
            <label for="confirmPassword">Confirm password</label>
            <input id="confirmPassword" name="confirmPassword" type="password" class="v2-input" minlength="12" autocomplete="new-password" required bind:value={confirmPassword} />
            <input type="hidden" name="uid" value={data.uid} />
            <input type="hidden" name="token" value={data.token} />
            <p class="v2-sub">Use at least 12 characters. Choose a password you do not use on another site.</p>
            {#if form?.error}
              <div class="v2-auth-note v2-auth-note-bad">{form.error}</div>
            {/if}
            <button type="submit" class="v2-btn v2-btn-primary v2-btn-block" disabled={submitting}>
              {submitting ? 'Saving…' : 'Set password'}
            </button>
          </form>
        {/if}
      {/if}
    </div>
  </div>
</div>
