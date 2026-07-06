document.addEventListener('DOMContentLoaded', function () {
    // -------------------------------------------------------------
    // 00. Dynamic Animation Delays (Resolves HTML/CSS linter warning)
    // -------------------------------------------------------------
    document.querySelectorAll('[data-delay]').forEach(el => {
        const delay = el.getAttribute('data-delay');
        if (delay) {
            el.style.animationDelay = delay + 'ms';
        }
    });

    // -------------------------------------------------------------
    // 0. Library Live Clock Widget
    // -------------------------------------------------------------
    const clockEl = document.getElementById('library-clock');
    const dateEl = document.getElementById('library-date');
    
    if (clockEl && dateEl) {
        const updateClock = () => {
            const now = new Date();
            // Format: 10:24:37 AM
            clockEl.textContent = now.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit', 
                hour12: true 
            });
            // Format: Friday, 03 July 2026
            const options = { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' };
            dateEl.textContent = now.toLocaleDateString('en-US', options);
        };
        setInterval(updateClock, 1000);
        updateClock();
    }

    // -------------------------------------------------------------
    // 1. Dark Mode Toggle
    // -------------------------------------------------------------
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-toggle-icon');
    
    const currentTheme = localStorage.getItem('theme') || 
                         (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    
    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeIcon) {
            themeIcon.classList.remove('bi-moon-fill');
            themeIcon.classList.add('bi-sun-fill');
        }
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        if (themeIcon) {
            themeIcon.classList.remove('bi-sun-fill');
            themeIcon.classList.add('bi-moon-fill');
        }
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            let theme = document.documentElement.getAttribute('data-theme');
            if (theme === 'dark') {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                if (themeIcon) {
                    themeIcon.classList.remove('bi-sun-fill');
                    themeIcon.classList.add('bi-moon-fill');
                }
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                if (themeIcon) {
                    themeIcon.classList.remove('bi-moon-fill');
                    themeIcon.classList.add('bi-sun-fill');
                }
            }
        });
    }

    // -------------------------------------------------------------
    // 2. Live Search & Genre/Availability Filter (AJAX)
    // -------------------------------------------------------------
    const searchInput = document.getElementById('search-input');
    const genreSelect = document.getElementById('genre-select');
    const availabilitySelect = document.getElementById('availability-select');
    const catalogContainer = document.getElementById('book-catalog-container');
    const spinner = document.getElementById('catalog-spinner');

    if (catalogContainer && (searchInput || genreSelect || availabilitySelect)) {
        let debounceTimer;

        const performSearch = () => {
            const searchVal = searchInput ? searchInput.value : '';
            const genreVal = genreSelect ? genreSelect.value : '';
            const availVal = availabilitySelect ? availabilitySelect.value : '';
            
            if (spinner) spinner.classList.remove('d-none');

            // Build URL
            let url = `/catalog/?search=${encodeURIComponent(searchVal)}&genre=${encodeURIComponent(genreVal)}&availability=${encodeURIComponent(availVal)}`;

            fetch(url, {
                headers: {
                    'x-requested-with': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.text();
            })
            .then(html => {
                catalogContainer.innerHTML = html;
                if (spinner) spinner.classList.add('d-none');
                initializeTimersAndBadges();
            })
            .catch(error => {
                console.error('Error during live catalog search:', error);
                if (spinner) spinner.classList.add('d-none');
            });
        };

        if (searchInput) {
            searchInput.addEventListener('input', () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(performSearch, 300);
            });
        }

        if (genreSelect) {
            genreSelect.addEventListener('change', performSearch);
        }

        if (availabilitySelect) {
            availabilitySelect.addEventListener('change', performSearch);
        }
    }

    // -------------------------------------------------------------
    // 3. Due Date Calculator (for Issue Form)
    // -------------------------------------------------------------
    const issueDateInput = document.getElementById('id_issue_date');
    const dueDatePreview = document.getElementById('due-date-preview');

    if (issueDateInput && dueDatePreview) {
        const calculateDueDate = () => {
            const issueDateVal = issueDateInput.value;
            if (issueDateVal) {
                const dateParts = issueDateVal.split('-');
                if (dateParts.length === 3) {
                    const issueDateObj = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
                    issueDateObj.setDate(issueDateObj.getDate() + 14);
                    
                    const options = { day: '2-digit', month: 'short', year: 'numeric' };
                    dueDatePreview.textContent = issueDateObj.toLocaleDateString('en-IN', options);
                }
            } else {
                dueDatePreview.textContent = '--';
            }
        };

        issueDateInput.addEventListener('change', calculateDueDate);
        calculateDueDate();
    }

    // -------------------------------------------------------------
    // 4. Overdue Alerts, Countdown Timers, and Late Fine Previewer
    // -------------------------------------------------------------
    function initializeTimersAndBadges() {
        const timerElements = document.querySelectorAll('.countdown-timer');
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        timerElements.forEach(el => {
            const dueStr = el.getAttribute('data-due-date');
            if (dueStr) {
                const parts = dueStr.split('-');
                const dueDate = new Date(parts[0], parts[1] - 1, parts[2]);
                dueDate.setHours(0, 0, 0, 0);

                const timeDiff = dueDate.getTime() - today.getTime();
                const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));

                if (daysDiff < 0) {
                    const absoluteOverdue = Math.abs(daysDiff);
                    const fine = absoluteOverdue * 50;
                    el.innerHTML = `<span class="text-danger fw-bold"><i class="bi bi-exclamation-triangle-fill"></i> Overdue by ${absoluteOverdue} day(s) (Fine: ₹${fine})</span>`;
                    
                    const parentCard = el.closest('.glass-card') || el.closest('.book-card-custom');
                    if (parentCard) {
                        parentCard.style.borderColor = 'rgba(239, 68, 68, 0.5)';
                    }
                    const parentRow = el.closest('tr');
                    if (parentRow) {
                        parentRow.classList.add('table-danger');
                    }
                } else if (daysDiff === 0) {
                    el.innerHTML = `<span class="text-warning fw-bold"><i class="bi bi-clock-fill"></i> Due Today!</span>`;
                } else {
                    el.innerHTML = `<span class="text-success"><i class="bi bi-calendar-check"></i> ${daysDiff} days remaining</span>`;
                }
            }
        });
    }
    initializeTimersAndBadges();

    // -------------------------------------------------------------
    // 5. Back to Top Button
    // -------------------------------------------------------------
    const backToTopBtn = document.getElementById('backToTopBtn');
    if (backToTopBtn) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });

        backToTopBtn.addEventListener('click', function () {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // -------------------------------------------------------------
    // 6. Loading Spinner for forms
    // -------------------------------------------------------------
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function () {
            if (form.checkValidity()) {
                const submitBtn = form.querySelector('[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...`;
                }
            }
        });
    });

    // -------------------------------------------------------------
    // 7. Toast Notifications (Bootstrap 5)
    // -------------------------------------------------------------
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
    });
});
