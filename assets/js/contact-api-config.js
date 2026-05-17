/**
 * Contact form API base URL.
 * - Leave apiBase empty when the CMS runs on the same domain (e.g. VPS: python cms/run.py).
 * - GitHub Pages alone cannot run /api/v1/contact; the form falls back to a mailto link on error.
 * - When CMS is live on seowithfaiz.com, set: apiBase: 'https://seowithfaiz.com'
 */
window.CONTACT_API_CONFIG = {
  apiBase: '',
  notifyEmail: 'md.faiz.ahmed62@gmail.com',
  whatsapp: '+916281367104',
};
