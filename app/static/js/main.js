/**
 * CampusFind — Main JavaScript
 * Theme toggle, cascade dropdowns, flash messages, modals, form helpers
 */

// ─────────────────────────────────────────────
//  THEME
// ─────────────────────────────────────────────
(function () {
  const stored = localStorage.getItem('cf_theme') || 'light';
  document.documentElement.setAttribute('data-theme', stored);
})();

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('cf_theme', next);
  const svg = document.getElementById('theme-icon-svg');
  if (svg) {
    if (next === 'dark') {
      svg.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
    } else {
      svg.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
    }
  }
}

// ─────────────────────────────────────────────
//  FLASH MESSAGES — auto dismiss
// ─────────────────────────────────────────────
function dismissFlash(el) {
  el.style.animation = 'fadeOut 0.4s ease forwards';
  setTimeout(() => el.remove(), 400);
}

document.addEventListener('DOMContentLoaded', function () {
  // Set initial theme icon
  const theme = document.documentElement.getAttribute('data-theme');
  const svg = document.getElementById('theme-icon-svg');
  if (svg && theme === 'dark') {
    svg.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
  }

  // Auto-dismiss flash messages
  document.querySelectorAll('.flash-msg').forEach(function (msg) {
    setTimeout(function () {
      if (msg.isConnected) dismissFlash(msg);
    }, 5000);
  });

  // ─────────────────────────────────────────────
  //  DROPDOWNS
  // ─────────────────────────────────────────────
  document.querySelectorAll('.dropdown').forEach(function (dd) {
    const trigger = dd.querySelector('[data-dropdown-trigger]');
    if (!trigger) return;
    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      dd.classList.toggle('open');
    });
  });

  document.addEventListener('click', function () {
    document.querySelectorAll('.dropdown.open').forEach(function (d) { d.classList.remove('open'); });
  });

  // ─────────────────────────────────────────────
  //  MOBILE NAV
  // ─────────────────────────────────────────────
  const hamburger = document.getElementById('hamburger');
  const mobileNav = document.getElementById('mobile-nav');
  const mobileClose = document.getElementById('mobile-nav-close');

  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', function () { mobileNav.classList.add('open'); });
    mobileClose && mobileClose.addEventListener('click', function () { mobileNav.classList.remove('open'); });
    mobileNav.addEventListener('click', function (e) {
      if (e.target === mobileNav) mobileNav.classList.remove('open');
    });
  }

  // ─────────────────────────────────────────────
  //  CASCADING LOCATION DROPDOWNS & AUTOCOMPLETE
  // ─────────────────────────────────────────────
  const countrySelect = document.getElementById('country_id');
  const regionSelect = document.getElementById('region_id');
  const citySelect = document.getElementById('city_id');
  const areaSelect = document.getElementById('area_id');
  const locationTextInput = document.getElementById('location_text');

  function clearSelect(sel, placeholder) {
    if (!sel) return;
    sel.innerHTML = '<option value="0">' + placeholder + '</option>';
    sel.disabled = false;
  }

  function populateSelect(sel, items, placeholder) {
    if (!sel) return;
    sel.innerHTML = '<option value="0">' + placeholder + '</option>';
    items.forEach(function (item) {
      var opt = document.createElement('option');
      opt.value = item.id;
      opt.textContent = item.name;
      sel.appendChild(opt);
    });
    sel.disabled = false;
  }

  // Load countries if select has only placeholder
  if (countrySelect && countrySelect.options.length <= 1) {
    fetch('/api/countries')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        populateSelect(countrySelect, data, '-- Select Country --');
        var preC = countrySelect.getAttribute('data-selected');
        if (preC && preC !== '0') {
          countrySelect.value = preC;
          countrySelect.dispatchEvent(new Event('change'));
        }
      })
      .catch(function () {});
  }

  if (countrySelect) {
    countrySelect.addEventListener('change', function () {
      var id = this.value;
      clearSelect(regionSelect, '-- Select Region / Province --');
      clearSelect(citySelect, '-- Select City / District --');
      clearSelect(areaSelect, '-- Select Area / Campus --');
      if (id && id !== '0') {
        fetch('/api/regions/' + id)
          .then(function (r) { return r.json(); })
          .then(function (data) {
            populateSelect(regionSelect, data, '-- Select Region / Province --');
            var preR = regionSelect ? regionSelect.getAttribute('data-selected') : null;
            if (preR && preR !== '0') {
              regionSelect.value = preR;
              regionSelect.removeAttribute('data-selected');
              regionSelect.dispatchEvent(new Event('change'));
            }
          });
      }
    });
  }

  if (regionSelect) {
    regionSelect.addEventListener('change', function () {
      var id = this.value;
      clearSelect(citySelect, '-- Select City / District --');
      clearSelect(areaSelect, '-- Select Area / Campus --');
      if (id && id !== '0') {
        fetch('/api/cities/' + id)
          .then(function (r) { return r.json(); })
          .then(function (data) {
            populateSelect(citySelect, data, '-- Select City / District --');
            var preCt = citySelect ? citySelect.getAttribute('data-selected') : null;
            if (preCt && preCt !== '0') {
              citySelect.value = preCt;
              citySelect.removeAttribute('data-selected');
              citySelect.dispatchEvent(new Event('change'));
            }
          });
      }
    });
  }

  if (citySelect) {
    citySelect.addEventListener('change', function () {
      var id = this.value;
      clearSelect(areaSelect, '-- Select Area / Campus --');
      if (id && id !== '0') {
        fetch('/api/areas/' + id)
          .then(function (r) { return r.json(); })
          .then(function (data) {
            populateSelect(areaSelect, data, '-- Select Area / Campus --');
            var preA = areaSelect ? areaSelect.getAttribute('data-selected') : null;
            if (preA && preA !== '0') {
              areaSelect.value = preA;
              areaSelect.removeAttribute('data-selected');
            }
          });
      }
    });
  }

  // Pre-load cascade if country already selected (e.g., in edit form or pre-filled form)
  if (countrySelect && countrySelect.value && countrySelect.value !== '0') {
    countrySelect.dispatchEvent(new Event('change'));
  }

  // ─────────────────────────────────────────────
  //  IMAGE PREVIEW
  // ─────────────────────────────────────────────
  const imageInput = document.getElementById('image');
  const imagePreview = document.getElementById('image-preview');

  if (imageInput && imagePreview) {
    imageInput.addEventListener('change', function () {
      var file = this.files[0];
      if (!file) return;
      if (!file.type.startsWith('image/')) {
        showToast('Please select an image file.', 'error');
        this.value = '';
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        showToast('Image must be under 5 MB.', 'error');
        this.value = '';
        return;
      }
      var reader = new FileReader();
      reader.onload = function (e) {
        imagePreview.src = e.target.result;
        imagePreview.style.display = 'block';
      };
      reader.readAsDataURL(file);
    });
  }

  // Upload area drag-and-drop
  const uploadArea = document.querySelector('.upload-area');
  if (uploadArea && imageInput) {
    uploadArea.addEventListener('click', function () { imageInput.click(); });
    uploadArea.addEventListener('dragover', function (e) { e.preventDefault(); this.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', function () { this.classList.remove('dragover'); });
    uploadArea.addEventListener('drop', function (e) {
      e.preventDefault();
      this.classList.remove('dragover');
      var files = e.dataTransfer.files;
      if (files.length) { imageInput.files = files; imageInput.dispatchEvent(new Event('change')); }
    });
  }

  // ─────────────────────────────────────────────
  //  CONFIRMATION MODAL
  // ─────────────────────────────────────────────
  const confirmModal = document.getElementById('confirm-modal');
  const confirmBtn = document.getElementById('confirm-action-btn');
  let confirmForm = null;

  window.showConfirm = function (message, formEl) {
    if (!confirmModal) {
      // fallback
      if (confirm(message)) formEl && formEl.submit();
      return;
    }
    const msgEl = document.getElementById('confirm-message');
    if (msgEl) msgEl.textContent = message;
    confirmForm = formEl || null;
    confirmModal.classList.add('open');
  };

  if (confirmBtn) {
    confirmBtn.addEventListener('click', function () {
      if (confirmForm) confirmForm.submit();
      if (confirmModal) confirmModal.classList.remove('open');
    });
  }

  const cancelModalBtns = document.querySelectorAll('[data-modal-close]');
  cancelModalBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (confirmModal) confirmModal.classList.remove('open');
    });
  });

  // Trigger confirm on delete/dangerous buttons
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      var msg = this.getAttribute('data-confirm');
      var form = this.closest('form') || document.querySelector(this.getAttribute('data-form'));
      showConfirm(msg, form);
    });
  });

  // ─────────────────────────────────────────────
  //  ADMIN SIDEBAR MOBILE TOGGLE
  // ─────────────────────────────────────────────
  const adminToggle = document.getElementById('admin-sidebar-toggle');
  const adminSidebar = document.querySelector('.admin-sidebar');
  if (adminToggle && adminSidebar) {
    adminToggle.addEventListener('click', function () {
      adminSidebar.classList.toggle('mobile-open');
    });
    document.addEventListener('click', function (e) {
      if (!adminSidebar.contains(e.target) && e.target !== adminToggle) {
        adminSidebar.classList.remove('mobile-open');
      }
    });
  }

  // ─────────────────────────────────────────────
  //  ACTIVE NAV LINK
  // ─────────────────────────────────────────────
  var path = window.location.pathname;
  document.querySelectorAll('.navbar-nav a, .admin-nav-link').forEach(function (a) {
    if (a.getAttribute('href') && path.startsWith(a.getAttribute('href')) && a.getAttribute('href') !== '/') {
      a.classList.add('active');
    } else if (a.getAttribute('href') === '/' && path === '/') {
      a.classList.add('active');
    }
  });

  // ─────────────────────────────────────────────
  //  HOME PAGE STATS — animated counter
  // ─────────────────────────────────────────────
  function animateCounter(el) {
    var target = parseInt(el.getAttribute('data-target'), 10);
    if (isNaN(target)) return;
    var duration = 1200;
    var step = Math.ceil(target / (duration / 16));
    var current = 0;
    var timer = setInterval(function () {
      current = Math.min(current + step, target);
      el.textContent = current.toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 16);
  }

  // Intersection observer for stat counters
  var counters = document.querySelectorAll('[data-target]');
  if (counters.length) {
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(function (c) { obs.observe(c); });
  }

  // ─────────────────────────────────────────────
  //  CHARACTER COUNTER for textareas
  // ─────────────────────────────────────────────
  document.querySelectorAll('textarea[maxlength]').forEach(function (ta) {
    var max = parseInt(ta.getAttribute('maxlength'), 10);
    var counter = document.createElement('small');
    counter.className = 'text-muted';
    counter.style.display = 'block';
    counter.style.textAlign = 'right';
    ta.parentNode.appendChild(counter);
    function update() { counter.textContent = ta.value.length + ' / ' + max; }
    ta.addEventListener('input', update);
    update();
  });

  // ─────────────────────────────────────────────
  //  HERO SECTION — 60 FPS 3D PARTICLE NETWORK & 3D TILT
  // ─────────────────────────────────────────────
  var heroCanvas = document.getElementById('hero-3d-canvas');
  var heroSection = document.getElementById('hero-premium');
  
  if (heroCanvas && heroSection) {
    var ctx = heroCanvas.getContext('2d');
    var particles = [];
    var particleCount = window.innerWidth < 768 ? 22 : 42; // Responsive density for zero lag
    var width, height;
    var mouse = { x: -1000, y: -1000, radius: 140 };
    var animFrameId = null;

    function resizeCanvas() {
      width = heroCanvas.width = heroSection.offsetWidth;
      height = heroCanvas.height = heroSection.offsetHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas, { passive: true });

    // 3D Particle Object
    function Particle() {
      this.reset(true);
    }

    Particle.prototype.reset = function (initial) {
      this.x = Math.random() * width;
      this.y = initial ? Math.random() * height : height + 10;
      this.z = Math.random() * 1.5 + 0.5; // Depth factor (3D parallax)
      this.radius = (Math.random() * 2 + 1.2) * this.z;
      this.vx = (Math.random() - 0.5) * 0.45 * this.z;
      this.vy = -(Math.random() * 0.45 + 0.2) * this.z;
      this.baseAlpha = Math.random() * 0.4 + 0.25;
    };

    Particle.prototype.update = function () {
      this.x += this.vx;
      this.y += this.vy;

      // Mouse interactive push
      var dx = mouse.x - this.x;
      var dy = mouse.y - this.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < mouse.radius) {
        var force = (mouse.radius - dist) / mouse.radius;
        var angle = Math.atan2(dy, dx);
        this.x -= Math.cos(angle) * force * 2.5;
        this.y -= Math.sin(angle) * force * 2.5;
      }

      // Loop boundaries
      if (this.y < -10 || this.x < -20 || this.x > width + 20) {
        this.reset(false);
      }
    };

    Particle.prototype.draw = function () {
      var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      var color = isDark ? '147, 197, 253' : '79, 70, 229'; // Indigo / Sky
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(' + color + ', ' + this.baseAlpha + ')';
      ctx.shadowBlur = this.z > 1.2 ? 8 : 0;
      ctx.shadowColor = 'rgba(' + color + ', 0.5)';
      ctx.fill();
    };

    // Initialize particles
    for (var i = 0; i < particleCount; i++) {
      particles.push(new Particle());
    }

    // Connect particles with 3D depth lines
    function drawLines() {
      var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      var lineColor = isDark ? '99, 102, 241' : '99, 102, 241';
      var maxDist = 115;

      for (var a = 0; a < particles.length; a++) {
        for (var b = a + 1; b < particles.length; b++) {
          var p1 = particles[a];
          var p2 = particles[b];
          var dx = p1.x - p2.x;
          var dy = p1.y - p2.y;
          var dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < maxDist) {
            var alpha = (1 - dist / maxDist) * 0.18 * ((p1.z + p2.z) / 2);
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = 'rgba(' + lineColor + ', ' + alpha + ')';
            ctx.lineWidth = 0.8 * ((p1.z + p2.z) / 2);
            ctx.stroke();
          }
        }
      }
    }

    // Animation Loop (High Performance 60FPS)
    var isHeroVisible = true;
    var heroObserver = new IntersectionObserver(function (entries) {
      isHeroVisible = entries[0].isIntersecting;
      if (isHeroVisible && !animFrameId) {
        animate();
      }
    }, { threshold: 0.1 });
    heroObserver.observe(heroSection);

    function animate() {
      if (!isHeroVisible) {
        animFrameId = null;
        return;
      }
      ctx.clearRect(0, 0, width, height);

      for (var i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].draw();
      }
      drawLines();

      animFrameId = requestAnimationFrame(animate);
    }
    animate();

    // Mouse coordinates tracker
    heroSection.addEventListener('mousemove', function (e) {
      var rect = heroCanvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    }, { passive: true });

    heroSection.addEventListener('mouseleave', function () {
      mouse.x = -1000;
      mouse.y = -1000;
    }, { passive: true });

    // Smooth 3D Card Tilt effect
    var card = heroSection.querySelector('.smart-match-preview-card');
    if (card && window.innerWidth > 992) {
      heroSection.addEventListener('mousemove', function (e) {
        var rect = heroSection.getBoundingClientRect();
        var x = e.clientX - rect.left - rect.width / 2;
        var y = e.clientY - rect.top - rect.height / 2;

        var rotX = -(y / rect.height) * 14;
        var rotY = (x / rect.width) * 18;

        card.style.transform = 'perspective(1000px) rotateX(' + rotX.toFixed(2) + 'deg) rotateY(' + rotY.toFixed(2) + 'deg) translateZ(10px)';
      }, { passive: true });

      heroSection.addEventListener('mouseleave', function () {
        card.style.transform = 'perspective(1000px) rotateX(2deg) rotateY(-3deg) translateZ(0)';
      }, { passive: true });
    }
  }
});

// ─────────────────────────────────────────────
//  TOAST HELPER (programmatic)
// ─────────────────────────────────────────────
function showToast(message, type) {
  type = type || 'info';
  var symbols = { success: '•', error: '!', warning: '!', info: 'i' };
  var container = document.querySelector('.flash-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'flash-container';
    document.body.appendChild(container);
  }
  var msg = document.createElement('div');
  msg.className = 'flash-msg flash-' + type;
  msg.innerHTML =
    '<span class="flash-icon" style="font-weight: 800;">' + (symbols[type] || 'i') + '</span>' +
    '<span class="flash-text">' + message + '</span>' +
    '<button class="flash-close" onclick="dismissFlash(this.parentElement)">✕</button>';
  container.appendChild(msg);
  setTimeout(function () { if (msg.isConnected) dismissFlash(msg); }, 5000);
}
