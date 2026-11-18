import axios from 'axios';
import { fail } from '@sveltejs/kit';
import * as publicEnv from '$app/env/public';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => ({
  uid: url.searchParams.get('uid') ?? '',
  token: url.searchParams.get('token') ?? ''
});

export const actions: Actions = {
  default: async ({ request }) => {
    const form = await request.formData();
    const uid = String(form.get('uid') ?? '');
    const token = String(form.get('token') ?? '');
    const password = String(form.get('password') ?? '');
    const confirmPassword = String(form.get('confirmPassword') ?? '');

    if (!uid || !token) {
      return fail(400, { error: 'This password setup link is incomplete or invalid.' });
    }
    if (password.length < 12) {
      return fail(400, { error: 'Use at least 12 characters for your password.' });
    }
    if (password !== confirmPassword) {
      return fail(400, { error: 'The passwords do not match.' });
    }

    try {
      await axios.post(
        `${publicEnv.PUBLIC_DJANGO_API_URL}/api/auth/social/set-password/`,
        { uid, token, password },
        { headers: { 'Content-Type': 'application/json' }, timeout: 10000 }
      );
      return { success: true };
    } catch (error) {
      const response = (error as { response?: { data?: { error?: unknown } } }).response;
      const message = response?.data?.error;
      return fail(400, {
        error: Array.isArray(message) ? message.join(' ') : String(message || 'Unable to set your password. Request a new sign-in link and try again.')
      });
    }
  }
};
