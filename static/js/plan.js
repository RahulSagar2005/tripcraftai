// TripCraft AI - Plan Form JS
let currentStep = 1;
const totalSteps = 7;
const paceLabels = ['Very relaxed', 'Mostly relaxed', 'Balanced', 'Fairly active', 'Action-packed'];
const currencySymbols = { USD: '$', EUR: '€', GBP: '£', INR: '₹', AUD: 'A$', CAD: 'C$', JPY: '¥', SGD: 'S$' };

// ── Navigation ──────────────────────────────────────────────────────────────
function updateStepUI() {
  document.querySelectorAll('.form-step').forEach((s, i) => {
    s.classList.toggle('active', i + 1 === currentStep);
  });
  document.querySelectorAll('.step-nav-item').forEach((s, i) => {
    const isActive = i + 1 === currentStep;
    const isCompleted = i + 1 < currentStep;
    s.classList.toggle('active', isActive);
    s.classList.toggle('completed', isCompleted);

    // Add checkmark icon for completed steps
    const icon = s.querySelector('.step-nav-icon');
    if (isCompleted && icon && !icon.querySelector('.checkmark')) {
      const checkmark = document.createElement('span');
      checkmark.className = 'checkmark';
      checkmark.textContent = '✓';
      icon.appendChild(checkmark);
    } else if (!isCompleted && icon && icon.querySelector('.checkmark')) {
      const checkmark = icon.querySelector('.checkmark');
      if (checkmark) checkmark.remove();
    }
  });

  document.getElementById('step-counter').textContent = `Step ${currentStep} of ${totalSteps}`;
  document.getElementById('prev-btn').disabled = currentStep === 1;

  const nextBtn = document.getElementById('next-btn');
  if (currentStep === totalSteps) {
    nextBtn.innerHTML = '✨ Create My Trip';
    nextBtn.classList.add('btn-success');
    nextBtn.onclick = submitTrip;
  } else {
    nextBtn.innerHTML = 'Next <span aria-hidden="true">→</span>';
    nextBtn.classList.remove('btn-success');
    nextBtn.onclick = nextStep;
  }

  const pct = (currentStep / totalSteps) * 100;
  document.getElementById('progress-fill').style.width = `${pct}%`;

  // Scroll to top of form smoothly
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Trigger animation on step change
  const activeStep = document.getElementById(`step-${currentStep}`);
  if (activeStep) {
    activeStep.style.animation = 'none';
    activeStep.offsetHeight; // Trigger reflow
    activeStep.style.animation = 'slideIn 0.5s ease-out';
  }
}

function nextStep() {
  if (!validateStep(currentStep)) return;
  if (currentStep < totalSteps) {
    currentStep++;
    updateStepUI();
  }
}

function prevStep() {
  if (currentStep > 1) {
    currentStep--;
    updateStepUI();
  }
}

function validateStep(step) {
  if (step === 1) {
    const dest = document.getElementById('destination').value.trim();
    const origin = document.getElementById('origin').value.trim();
    if (!dest) {
      showFieldError('destination', 'Please enter your destination');
      return false;
    }
    if (!origin) {
      showFieldError('origin', 'Please enter your starting location');
      return false;
    }
    clearFieldError('destination');
    clearFieldError('origin');
  }
  return true;
}

function showFieldError(fieldId, message) {
  const field = document.getElementById(fieldId);
  if (field) {
    field.style.borderColor = 'var(--primary)';
    field.style.boxShadow = '0 0 0 3px var(--primary-light)';

    // Show error message
    let errorEl = field.parentElement.querySelector('.field-error');
    if (!errorEl) {
      errorEl = document.createElement('span');
      errorEl.className = 'field-error';
      errorEl.style.cssText = 'color: var(--primary); font-size: 0.8rem; margin-top: 4px; display: block;';
      field.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
  }
}

function clearFieldError(fieldId) {
  const field = document.getElementById(fieldId);
  if (field) {
    field.style.borderColor = 'var(--gray-200)';
    field.style.boxShadow = 'none';

    const errorEl = field.parentElement.querySelector('.field-error');
    if (errorEl) errorEl.remove();
  }
}

// ── Date Toggle ──────────────────────────────────────────────────────────────
function toggleDateMode(mode, el) {
  document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('date-picker-mode').style.display = mode === 'picker' ? 'block' : 'none';
  document.getElementById('date-flexible-mode').classList.toggle('hidden', mode !== 'flexible');
}

// Auto-calculate duration from dates
['start_date', 'end_date'].forEach(id => {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener('change', () => {
      const s = document.getElementById('start_date').value;
      const e = document.getElementById('end_date').value;
      if (s && e) {
        const diff = Math.round((new Date(e) - new Date(s)) / (1000 * 60 * 60 * 24));
        if (diff > 0) {
          const durationInput = document.getElementById('duration_days');
          durationInput.value = diff;
          // Animate the change
          durationInput.parentElement.classList.add('highlight');
          setTimeout(() => durationInput.parentElement.classList.remove('highlight'), 1000);
        }
      }
    });
  }
});

// ── Budget ──────────────────────────────────────────────────────────────────
function updateBudget(val) {
  document.getElementById('budget_per_person').value = val;
  const sym = currencySymbols[document.getElementById('currency').value] || '$';
  const num = parseInt(val).toLocaleString();
  const display = document.getElementById('budget-display-val');
  display.textContent = `${sym}${num}`;

  // Animate the budget value change
  display.style.transform = 'scale(1.1)';
  setTimeout(() => display.style.transform = 'scale(1)', 200);
}

document.getElementById('currency')?.addEventListener('change', () => {
  updateBudget(document.getElementById('budget_range').value);
});

// ── Pace ────────────────────────────────────────────────────────────────────
function updatePace(val) {
  const label = document.getElementById('pace-label');
  label.textContent = paceLabels[parseInt(val) - 1];

  // Animate pace label
  label.style.transform = 'scale(1.15)';
  label.style.transition = 'transform 0.2s ease';
  setTimeout(() => label.style.transform = 'scale(1)', 200);
}

// ── Counter ─────────────────────────────────────────────────────────────────
function changeCount(id, delta) {
  const el = document.getElementById(id);
  const min = parseInt(el.min) || 0;
  const max = parseInt(el.max) || 99;
  const newVal = Math.min(max, Math.max(min, parseInt(el.value) + delta));
  el.value = newVal;

  // Add button press animation
  const btn = event.target;
  btn.style.transform = 'scale(0.9)';
  setTimeout(() => btn.style.transform = 'scale(1)', 100);
}

// ── Checkbox Tag Toggle ──────────────────────────────────────────────────────
document.querySelectorAll('.checkbox-tag').forEach(tag => {
  const checkbox = tag.querySelector('input[type="checkbox"]');

  // Sync active class with checkbox state on load
  if (checkbox && checkbox.checked) {
    tag.classList.add('active');
  }

  tag.addEventListener('click', (e) => {
    // Prevent double-triggering
    e.preventDefault();

    // Toggle the checkbox
    checkbox.checked = !checkbox.checked;

    // Toggle active class based on checkbox state
    if (checkbox.checked) {
      tag.classList.add('active');
    } else {
      tag.classList.remove('active');
    }

    // Add a little bounce animation
    tag.style.transform = 'scale(0.95)';
    setTimeout(() => tag.style.transform = 'scale(1)', 150);
  });
});

document.querySelectorAll('.radio-card').forEach(card => {
  card.addEventListener('click', () => {
    const group = card.closest('.radio-grid, .radio-grid-2, .radio-grid-3');
    if (group) {
      group.querySelectorAll('.radio-card').forEach(c => c.classList.remove('active'));
    }
    card.classList.add('active');

    // Add scale animation
    card.style.transform = 'scale(1.02)';
    setTimeout(() => card.style.transform = 'scale(1)', 200);
  });
});

document.querySelectorAll('.radio-card-lg').forEach(card => {
  card.addEventListener('click', () => {
    const group = card.closest('.radio-cards-2col');
    if (group) {
      group.querySelectorAll('.radio-card-lg').forEach(c => c.classList.remove('active'));
    }
    card.classList.add('active');

    card.style.transform = 'scale(1.02)';
    setTimeout(() => card.style.transform = 'scale(1)', 200);
  });
});

// ── Collect Form Data ────────────────────────────────────────────────────────
function collectFormData() {
  const getChecked = (name) =>
    [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(i => i.value);
  const getCheckedTags = (groupId) =>
    [...document.querySelectorAll(`#${groupId} .checkbox-tag.active input`)].map(i => i.value);
  const getCheckedTagsByName = (name) =>
    [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(i => i.value);

  const startDate = document.getElementById('start_date').value;
  const endDate = document.getElementById('end_date').value;
  const flexDates = document.getElementById('flexible_dates')?.value || '';
  const isFlexible = !document.getElementById('date-picker-mode').style.display ||
                     document.getElementById('date-picker-mode').style.display === 'none';

  const paceVal = parseInt(document.getElementById('pace_slider')?.value || 3);
  const pace = paceLabels[paceVal - 1];

  const dietary = getCheckedTagsByName('dietary');
  const vibes = getCheckedTags('vibes-group');
  const priorities = getCheckedTags('priorities-group');
  const ageGroups = getCheckedTags('age-groups');
  const amenities = getCheckedTagsByName('amenity');
  const accomType = getCheckedTagsByName('accom_type');
  const transport = getCheckedTagsByName('transport');

  return {
    traveler_name: document.getElementById('traveler_name').value.trim(),
    destination: document.getElementById('destination').value.trim(),
    origin: document.getElementById('origin').value.trim(),
    start_date: startDate || flexDates,
    end_date: endDate,
    flexible_dates: flexDates,
    duration_days: parseInt(document.getElementById('duration_days').value) || 5,
    group_type: (document.querySelector('input[name="group_type"]:checked') || {}).value || 'Solo',
    num_adults: parseInt(document.getElementById('num_adults').value) || 1,
    num_children: parseInt(document.getElementById('num_children').value) || 0,
    age_groups: ageGroups,
    budget_per_person: parseInt(document.getElementById('budget_per_person').value) || 1000,
    currency: document.getElementById('currency').value || 'USD',
    travel_style: (document.querySelector('input[name="travel_style"]:checked') || {}).value || 'comfort',
    budget_flexible: document.getElementById('budget_flexible')?.checked || false,
    vibes: vibes,
    priorities: priorities,
    accom_type: accomType,
    num_rooms: parseInt(document.getElementById('num_rooms').value) || 1,
    amenities: amenities,
    pace: pace,
    start_time_pref: (document.querySelector('input[name="start_time"]:checked') || {}).value || 'normal',
    transport_pref: transport,
    previous_visit: (document.querySelector('input[name="previous_visit"]:checked') || {}).value || 'no',
    specific_interests: document.getElementById('specific_interests')?.value.trim() || '',
    dietary_restrictions: dietary.join(', '),
    additional_info: document.getElementById('additional_info')?.value.trim() || '',
  };
}

// ── Submit ────────────────────────────────────────────────────────────────────
async function submitTrip() {
  const btn = document.getElementById('next-btn');
  const originalText = btn.innerHTML;

  btn.innerHTML = '🚀 Creating your trip...';
  btn.classList.add('btn-submitting');
  btn.disabled = true;

  const formData = collectFormData();

  try {
    const res = await fetch('/create-trip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    const data = await res.json();
    if (data.success) {
      btn.innerHTML = '✅ Trip Created! Redirecting...';
      btn.classList.remove('btn-submitting');
      btn.classList.add('btn-success');
      setTimeout(() => {
        window.location.href = `/processing/${data.trip_id}`;
      }, 1000);
    } else {
      alert('Error creating trip: ' + (data.message || 'Unknown error'));
      btn.innerHTML = originalText;
      btn.disabled = false;
      btn.classList.remove('btn-submitting');
    }
  } catch (e) {
    alert('Network error. Please try again.');
    btn.innerHTML = originalText;
    btn.disabled = false;
    btn.classList.remove('btn-submitting');
  }
}

// ── Add click handlers to step nav items ─────────────────────────────────────
document.querySelectorAll('.step-nav-item').forEach((item, index) => {
  item.addEventListener('click', () => {
    // Allow going back to completed steps
    if (index + 1 < currentStep) {
      currentStep = index + 1;
      updateStepUI();
    }
  });
});

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateStepUI();
  updateBudget(1000);
  updatePace(3);

  // Set default age group (26-35)
  const ageGroupsContainer = document.getElementById('age-groups');
  if (ageGroupsContainer) {
    const defaultAgeTag = ageGroupsContainer.querySelector('[value="26-35"]');
    if (defaultAgeTag) {
      defaultAgeTag.classList.add('active');
      const checkbox = defaultAgeTag.querySelector('input[type="checkbox"]');
      if (checkbox) checkbox.checked = true;
    }
  }

  // Add focus animations to inputs
  document.querySelectorAll('.form-input, .form-textarea').forEach(input => {
    input.addEventListener('focus', () => {
      input.parentElement.classList.add('focused');
    });
    input.addEventListener('blur', () => {
      input.parentElement.classList.remove('focused');
    });
  });

  // Add hover effect to step cards
  document.querySelectorAll('.step-card').forEach((card, index) => {
    card.style.transitionDelay = `${index * 0.1}s`;
  });
});
