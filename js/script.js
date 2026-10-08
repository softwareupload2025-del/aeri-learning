"use strict";

document.documentElement.classList.add('js');

// Analytics are intentionally not loaded until you add IDs and your consent setup.
// A lead_form_submit event is pushed to dataLayer / Meta Pixel if those are installed.
function trackLead() {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event: 'lead_form_submit', form_name: 'free_activity_pack' });
  if (typeof window.fbq === 'function') window.fbq('track', 'Lead', { content_name: 'Aeri Learning Free Activity Pack' });
}

const form = document.getElementById('lead-form');
const requestTokenField = document.getElementById('request-token');
const responseFrame = document.getElementById('form-response-frame');
const formStatus = document.getElementById('form-status');
const submitButton = document.getElementById('submit-button');
const submitLabel = submitButton.querySelector('.submit-label');
const submitArrow = submitButton.querySelector('.submit-arrow');
const originalSubmitLabel = submitLabel.textContent;
// Destination used after the Apps Script POST response completes.
const successRedirectUrl = 'https://softwareupload2025-del.github.io/aeri-learning-thanks/';
const responseTimeoutMs = 30000;
let pendingRequestToken = '';
let submissionTimeout = null;
let responseFallbackTimeout = null;
let formResponseReceived = false;
let redirectStarted = false;
let responseFrameLoaded = false;
try {
  responseFrameLoaded = responseFrame.contentDocument.readyState === 'complete';
} catch (_error) {
  // The frame may already be cross-origin; its load event is used below instead.
}

// Keep the visitor on this page while Apps Script processes the POST in a hidden iframe.
// Current deployments use postMessage; the load fallback also supports older text responses.
form.target = responseFrame.name;

function createRequestToken() {
  if (window.crypto && typeof window.crypto.randomUUID === 'function') {
    return window.crypto.randomUUID();
  }
  if (window.crypto && typeof window.crypto.getRandomValues === 'function') {
    const bytes = new Uint8Array(16);
    window.crypto.getRandomValues(bytes);
    return Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
  }
  return `${Date.now().toString(16)}-${Math.random().toString(16).slice(2)}`;
}

function setFormStatus(message, state = '') {
  formStatus.textContent = message;
  if (state) formStatus.dataset.state = state;
  else delete formStatus.dataset.state;
}

function resetSubmitButton() {
  delete form.dataset.submitting;
  submitButton.disabled = false;
  submitButton.removeAttribute('aria-busy');
  submitLabel.textContent = originalSubmitLabel;
  submitArrow.hidden = false;
}

function clearSubmissionTimers() {
  if (submissionTimeout !== null) {
    window.clearTimeout(submissionTimeout);
    submissionTimeout = null;
  }
  if (responseFallbackTimeout !== null) {
    window.clearTimeout(responseFallbackTimeout);
    responseFallbackTimeout = null;
  }
}

function redirectAfterSave() {
  if (redirectStarted) return;
  redirectStarted = true;
  clearSubmissionTimers();
  pendingRequestToken = '';
  trackLead();
  window.location.assign(successRedirectUrl);
}

function handleAppsScriptResponse(event) {
  const response = event.data;
  // Validate the random per-submission token. Apps Script can send this from a
  // nested Google frame, so do not require event.source to equal the outer iframe.
  if (!response || response.type !== 'aeri-form-result' || response.token !== pendingRequestToken) return;

  formResponseReceived = true;
  clearSubmissionTimers();

  if (response.status === 'success') {
    redirectAfterSave();
    return;
  }

  pendingRequestToken = '';
  resetSubmitButton();
  setFormStatus(response.message || 'We could not save your request. Please try again.', 'error');
}

function handleResponseFrameLoad() {
  if (!responseFrameLoaded) {
    responseFrameLoaded = true;
    return;
  }
  if (form.dataset.submitting !== 'true' || formResponseReceived) return;

  // A legacy Apps Script deployment may return plain text (for example, "Success")
  // instead of postMessage. The hidden-frame load means the POST has completed.
  responseFallbackTimeout = window.setTimeout(() => {
    responseFallbackTimeout = null;
    if (form.dataset.submitting === 'true' && !formResponseReceived) redirectAfterSave();
  }, 500);
}

responseFrame.addEventListener('load', handleResponseFrameLoad);
window.addEventListener('message', handleAppsScriptResponse);

form.addEventListener('submit', (event) => {
  if (!form.checkValidity()) {
    event.preventDefault();
    form.reportValidity();
    return;
  }
  if (form.dataset.submitting === 'true') {
    event.preventDefault();
    return;
  }

  clearSubmissionTimers();
  formResponseReceived = false;
  redirectStarted = false;
  pendingRequestToken = createRequestToken();
  requestTokenField.value = pendingRequestToken;
  form.dataset.submitting = 'true';
  submitButton.disabled = true;
  submitButton.setAttribute('aria-busy', 'true');
  submitLabel.textContent = 'Sending...';
  submitArrow.hidden = true;
  setFormStatus('Sending your request…');

  submissionTimeout = window.setTimeout(() => {
    if (form.dataset.submitting !== 'true') return;
    clearSubmissionTimers();
    formResponseReceived = true;
    pendingRequestToken = '';
    resetSubmitButton();
    setFormStatus('We could not confirm the submission. It may have been saved; wait a moment before trying again to avoid a duplicate.', 'error');
  }, responseTimeoutMs);
});

// Gentle reveal on scroll; content remains visible if JavaScript or IntersectionObserver is unavailable.
const revealItems = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -24px 0px' });
  revealItems.forEach((item) => revealObserver.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add('is-visible'));
}

// Mobile-only sticky CTA after the visitor has scrolled halfway down the page.
const stickyCta = document.getElementById('sticky-cta');
const signupSection = document.getElementById('get-the-pack');
const footer = document.querySelector('.site-footer');
let signupInView = false;
let footerInView = false;
if ('IntersectionObserver' in window) {
  const stopStickyObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.target === signupSection) signupInView = entry.isIntersecting;
      if (entry.target === footer) footerInView = entry.isIntersecting;
      updateStickyCta();
    });
  }, { threshold: 0.12 });
  stopStickyObserver.observe(signupSection);
  stopStickyObserver.observe(footer);
}
function updateStickyCta() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? window.scrollY / scrollable : 0;
  const isMobile = window.matchMedia('(max-width: 760px)').matches;
  stickyCta.classList.toggle('is-visible', isMobile && progress >= 0.5 && !signupInView && !footerInView);
}
window.addEventListener('scroll', updateStickyCta, { passive: true });
window.addEventListener('resize', updateStickyCta);
updateStickyCta();

// Accessible policy dialogs.
document.querySelectorAll('[data-dialog]').forEach((link) => {
  link.addEventListener('click', (event) => {
    event.preventDefault();
    const dialog = document.getElementById(link.dataset.dialog);
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });
});
document.querySelectorAll('.dialog-close').forEach((button) => {
  button.addEventListener('click', () => button.closest('dialog').close());
});
document.querySelectorAll('dialog').forEach((dialog) => {
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });
});
document.getElementById('year').textContent = new Date().getFullYear();
