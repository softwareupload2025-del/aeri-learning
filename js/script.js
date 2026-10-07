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
const nextUrlField = document.getElementById('form-next');
const submitButton = document.getElementById('submit-button');
const submitLabel = submitButton.querySelector('.submit-label');
const submitArrow = submitButton.querySelector('.submit-arrow');

// FormSubmit expects an absolute redirect URL. Resolve the thank-you page on the
// same origin so this also works on the final deployed domain without a backend.
if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
  nextUrlField.value = new URL('thank-you.html', window.location.href).href;
}

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
  form.dataset.submitting = 'true';
  submitButton.disabled = true;
  submitButton.setAttribute('aria-busy', 'true');
  submitLabel.textContent = 'Sending...';
  submitArrow.hidden = true;
  trackLead();
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
