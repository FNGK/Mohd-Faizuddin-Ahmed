(function () {
  const form = document.getElementById('contactForm');
  if (!form) return;

  const statusEl = document.getElementById('contactFormStatus');
  const submitBtn = form.querySelector('button[type="submit"]');
  const apiCfg = window.CONTACT_API_CONFIG || {};
  const NOTIFY_EMAIL = apiCfg.notifyEmail || 'md.faiz.ahmed62@gmail.com';
  const WHATSAPP = apiCfg.whatsapp || '+916281367104';

  // Never use FormSubmit or native POST to third-party handlers.
  form.removeAttribute('action');
  form.setAttribute('method', 'post');

  function apiUrl() {
    const base = (apiCfg.apiBase || '').replace(/\/$/, '');
    return (base || window.location.origin) + '/api/v1/contact';
  }

  function thankYouUrl() {
    return new URL('../thank-you.html', window.location.href).href;
  }

  function mailtoUrl(payload) {
    const subject = encodeURIComponent(`SEO inquiry — ${payload.name} (${payload.region})`);
    const body = encodeURIComponent(
      [
        'New inquiry from seowithfaiz.com',
        '',
        `Name: ${payload.name}`,
        `Email: ${payload.email}`,
        `Website: ${payload.website}`,
        `Market: ${payload.region}`,
        '',
        payload.goal,
      ].join('\n')
    );
    return `mailto:${NOTIFY_EMAIL}?subject=${subject}&body=${body}`;
  }

  function setStatus(message, type, options) {
    if (!statusEl) return;
    statusEl.innerHTML = '';
    statusEl.textContent = message;
    statusEl.hidden = !message;
    statusEl.classList.remove('form-status--error', 'form-status--success');
    if (type) statusEl.classList.add('form-status--' + type);
    if (options && options.mailtoHref) {
      statusEl.textContent = '';
      statusEl.appendChild(document.createTextNode(message + ' '));
      const link = document.createElement('a');
      link.href = options.mailtoHref;
      link.textContent = 'Send via Gmail instead';
      link.className = 'form-status__mailto';
      statusEl.appendChild(link);
    }
  }

  function setBusy(busy) {
    if (!submitBtn) return;
    submitBtn.disabled = busy;
    submitBtn.setAttribute('aria-busy', busy ? 'true' : 'false');
    submitBtn.textContent = busy ? 'Sending…' : 'Send inquiry';
  }

  function payloadFromForm() {
    return {
      name: form.elements.name?.value?.trim() || '',
      email: form.elements.email?.value?.trim() || '',
      website: form.elements.website?.value?.trim() || '',
      region: form.elements.region?.value?.trim() || '',
      goal: form.elements.goal?.value?.trim() || '',
      honeypot: form.elements.honeypot?.value?.trim() || '',
    };
  }

  function parseApiError(data) {
    if (data?.errors && Array.isArray(data.errors)) return data.errors.join(' ');
    if (data?.detail?.errors && Array.isArray(data.detail.errors)) return data.detail.errors.join(' ');
    if (typeof data?.detail === 'string') return data.detail;
    if (Array.isArray(data?.detail)) {
      return data.detail
        .map(function (item) {
          return item.msg || item.message || '';
        })
        .filter(Boolean)
        .join(' ');
    }
    return data?.message || '';
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    setStatus('', '');

    if (!form.reportValidity()) return;

    const payload = payloadFromForm();
    setBusy(true);
    setStatus('Sending your inquiry…', 'success');

    fetch(apiUrl(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        return res
          .json()
          .catch(function () {
            return {};
          })
          .then(function (data) {
            return { ok: res.ok, status: res.status, data: data };
          });
      })
      .then(function (result) {
        if (result.ok && result.data && result.data.success) {
          window.location.href = thankYouUrl() + '?sent=1';
          return;
        }
        const message =
          parseApiError(result.data) ||
          'Could not send your inquiry. Use the email link below or WhatsApp.';
        throw new Error(message);
      })
      .catch(function (err) {
        setBusy(false);
        const isNetwork =
          err instanceof TypeError ||
          /failed to fetch|network|unavailable/i.test(String(err.message));
        const hint = isNetwork
          ? 'The form API is not available on this host yet (GitHub Pages is static). '
          : '';
        setStatus(
          hint +
            (err.message ||
              'Could not send your inquiry.') +
            ' You can also email or WhatsApp using the links above.',
          'error',
          { mailtoHref: mailtoUrl(payload) }
        );
      });
  });
})();
