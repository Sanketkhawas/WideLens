/**
 * ==========================================
 * AI Business Expansion Advisor - Controller
 * Vanilla JS App Logic & Visualization Engine
 * ==========================================
 */

document.addEventListener('DOMContentLoaded', () => {
    // Application State
    const state = {
        activePage: 'dashboard',
        sidebarOpen: false,
        revenueFilterMonths: 12,
        simulator: {
            rent: 10000,
            demographic: 80,
            competition: 3
        },
        charts: {}
    };

    // DOM Element Selectors
    const elements = {
        sidebar: document.getElementById('sidebar'),
        toggleSidebar: document.getElementById('toggleSidebar'),
        sidebarOverlay: document.getElementById('sidebarOverlay'),
        sidebarMenuItems: document.querySelectorAll('.sidebar-menu li'),
        currentDateTime: document.getElementById('currentDateTime'),
        notificationBtn: document.getElementById('notificationBtn'),
        notificationMenu: document.getElementById('notificationMenu'),
        settingsBtn: document.getElementById('settingsBtn'),
        logoutBtn: document.getElementById('logoutBtn'),
        searchInput: document.getElementById('searchInput'),
        
        // KPI elements
        kpiValues: document.querySelectorAll('.kpi-value'),
        
        // Modals
        viewDetailsBtn: document.getElementById('viewDetailsBtn'),
        simulateBtn: document.getElementById('simulateBtn'),
        locationDetailsModal: document.getElementById('locationDetailsModal'),
        closeModalBtn: document.getElementById('closeModalBtn'),
        closeModalFooterBtn: document.getElementById('closeModalFooterBtn'),
        simulatorModal: document.getElementById('simulatorModal'),
        closeSimModalBtn: document.getElementById('closeSimModalBtn'),
        resetSimBtn: document.getElementById('resetSimBtn'),
        applySimBtn: document.getElementById('applySimBtn'),
        
        // Simulator elements
        rentSlider: document.getElementById('rentSlider'),
        rentValue: document.getElementById('rentValue'),
        demographicSlider: document.getElementById('demographicSlider'),
        demographicValue: document.getElementById('demographicValue'),
        competitionSlider: document.getElementById('competitionSlider'),
        competitionValue: document.getElementById('competitionValue'),
        simResultRevenue: document.getElementById('simResultRevenue'),
        simResultScore: document.getElementById('simResultScore'),
        
        // Core buttons
        exportPdfBtn: document.getElementById('exportPdfBtn'),
        refreshActivityBtn: document.getElementById('refreshActivityBtn'),
        activityTableBody: document.getElementById('activityTableBody'),
        toastContainer: document.getElementById('toastContainer')
    };

    // Initialize Dashboard
    initApp();

    function initApp() {
        updateClock();
        setInterval(updateClock, 1000 * 60); // update every minute
        
        setupSidebar();
        setupDropdowns();
        setupSearchAnimation();
        setupModals();
        setupSimulator();
        setupExtraInteractions();
        
        // Initialize visualizations
        initCharts();
        
        // Animate count numbers
        animateKPIs();
        
        // Show welcome toast
        showToast('System loaded successfully. Welcome back, Jane!', 'info');
    }

    // Real-time Clock Function
    function updateClock() {
        const now = new Date();
        const options = { 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        };
        if (elements.currentDateTime) {
            elements.currentDateTime.textContent = now.toLocaleDateString('en-US', options);
        }
    }

    // Sidebar Toggles & Menu Selection
    function setupSidebar() {
        // Toggle Sidebar on mobile
        if (elements.toggleSidebar) {
            elements.toggleSidebar.addEventListener('click', () => {
                state.sidebarOpen = !state.sidebarOpen;
                elements.sidebar.classList.toggle('show', state.sidebarOpen);
                elements.sidebarOverlay.classList.toggle('show', state.sidebarOpen);
            });
        }

        // Overlay backdrop click to close
        if (elements.sidebarOverlay) {
            elements.sidebarOverlay.addEventListener('click', () => {
                state.sidebarOpen = false;
                elements.sidebar.classList.remove('show');
                elements.sidebarOverlay.classList.remove('show');
            });
        }

        // Menu selection triggers
        elements.sidebarMenuItems.forEach(item => {
            item.addEventListener('click', (e) => {
                elements.sidebarMenuItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                
                const pageName = item.getAttribute('data-page');
                state.activePage = pageName;
                
                // Show notification feedback
                showToast(`Switched view to ${item.querySelector('span').textContent}`, 'info');
                
                // Close sidebar on mobile after clicking
                if (window.innerWidth <= 991) {
                    state.sidebarOpen = false;
                    elements.sidebar.classList.remove('show');
                    elements.sidebarOverlay.classList.remove('show');
                }
            });
        });
    }

    // Action Dropdowns (Notification Tray)
    function setupDropdowns() {
        if (elements.notificationBtn) {
            elements.notificationBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                elements.notificationMenu.classList.toggle('show');
            });
        }

        // Click outside of dropdowns closes them
        document.addEventListener('click', () => {
            if (elements.notificationMenu) {
                elements.notificationMenu.classList.remove('show');
            }
        });

        // Prevent closing dropdown when clicking inside it
        if (elements.notificationMenu) {
            elements.notificationMenu.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        // Notification clear-all button
        const clearAllBtn = document.querySelector('.mark-all-read');
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', () => {
                const list = document.querySelector('.notification-list');
                if (list) {
                    list.innerHTML = `
                        <li style="text-align: center; color: var(--text-muted); padding: 24px;">
                            <i class="bi bi-bell-slash" style="font-size: 24px;"></i>
                            <p style="margin-top: 8px;">No new alerts</p>
                        </li>
                    `;
                }
                const dot = document.querySelector('.badge-dot');
                if (dot) dot.style.display = 'none';
                showToast('Notifications cleared', 'success');
            });
        }
    }

    // Interactive Search Filtering (Mock)
    function setupSearchAnimation() {
        if (elements.searchInput) {
            elements.searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    const query = elements.searchInput.value.trim();
                    if (query) {
                        showToast(`Searching location indices for: "${query}"`, 'info');
                        elements.searchInput.blur();
                    }
                }
            });
        }
    }

    // KPI Increment Animation (Counter)
    function animateKPIs() {
        elements.kpiValues.forEach(kpi => {
            const target = parseInt(kpi.getAttribute('data-value'), 10);
            if (isNaN(target)) return;

            let current = 0;
            const duration = 1200; // ms
            const stepTime = Math.max(Math.floor(duration / (target / 50)), 15);
            
            const timer = setInterval(() => {
                // Determine increment size (accelerate initially)
                const increment = Math.ceil((target - current) / 10);
                current += increment;
                
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                // Format with commas if large
                kpi.textContent = current.toLocaleString('en-US');
            }, stepTime);
        });
    }

    // Modal Manager Toggles
    function setupModals() {
        // Spatial intelligence modal open/close
        if (elements.viewDetailsBtn) {
            elements.viewDetailsBtn.addEventListener('click', () => {
                elements.locationDetailsModal.classList.add('show');
            });
        }

        const closeSpatialModal = () => {
            elements.locationDetailsModal.classList.remove('show');
        };

        if (elements.closeModalBtn) elements.closeModalBtn.addEventListener('click', closeSpatialModal);
        if (elements.closeModalFooterBtn) elements.closeModalFooterBtn.addEventListener('click', closeSpatialModal);

        // Simulator modal open/close
        if (elements.simulateBtn) {
            elements.simulateBtn.addEventListener('click', () => {
                elements.simulatorModal.classList.add('show');
            });
        }

        if (elements.closeSimModalBtn) {
            elements.closeSimModalBtn.addEventListener('click', () => {
                elements.simulatorModal.classList.remove('show');
            });
        }

        // Close modal when clicking dark backdrop
        window.addEventListener('click', (e) => {
            if (e.target === elements.locationDetailsModal) closeSpatialModal();
            if (e.target === elements.simulatorModal) elements.simulatorModal.classList.remove('show');
        });
    }

    // What-If Simulator Logic & Projections
    function setupSimulator() {
        function runSimulation() {
            const rent = parseInt(elements.rentSlider.value, 10);
            const demographic = parseInt(elements.demographicSlider.value, 10);
            const competition = parseInt(elements.competitionSlider.value, 10);

            // Update UI Labels
            elements.rentValue.textContent = `$${rent.toLocaleString()}`;
            elements.demographicValue.textContent = `${demographic}%`;
            elements.competitionValue.textContent = competition;

            // Simple realistic simulated calculation formulas
            // Higher demographic match and lower competition = higher revenue and higher score
            // Low rent is nice, but super high rent often implies a premium high-traffic hotspot
            // Therefore, let's create a bell curve / traffic hotspot value for rent
            const rentFactor = rent < 5000 ? 0.7 : (rent < 15000 ? 1.0 : 1.25);
            
            // Expected revenue base $100k
            const computedRevenue = Math.round(
                (100000 + (demographic * 1200) - (competition * 8500)) * rentFactor
            );
            
            // Clamp revenue
            const finalRevenue = Math.max(45000, Math.min(320000, computedRevenue));

            // Success Score (0-100)
            // Competitors decrease success chance, demographic match increases it, rent budget availability helps
            let computedScore = Math.round(
                (demographic * 0.7) + (30 - (competition * 4)) + (rent > 12000 ? 10 : 0)
            );
            computedScore = Math.max(35, Math.min(99, computedScore));

            // Update simulator display values with animation/effects
            elements.simResultRevenue.textContent = `$${finalRevenue.toLocaleString()}`;
            elements.simResultScore.textContent = `${computedScore}%`;

            // Change metric text colors based on outcome
            if (computedScore >= 80) {
                elements.simResultScore.style.color = 'var(--success)';
            } else if (computedScore >= 60) {
                elements.simResultScore.style.color = 'var(--warning)';
            } else {
                elements.simResultScore.style.color = 'var(--danger)';
            }

            // Save variables in state
            state.simulator.rent = rent;
            state.simulator.demographic = demographic;
            state.simulator.competition = competition;
        }

        // Attach listeners to range sliders
        if (elements.rentSlider) elements.rentSlider.addEventListener('input', runSimulation);
        if (elements.demographicSlider) elements.demographicSlider.addEventListener('input', runSimulation);
        if (elements.competitionSlider) elements.competitionSlider.addEventListener('input', runSimulation);

        // Reset Simulator
        if (elements.resetSimBtn) {
            elements.resetSimBtn.addEventListener('click', () => {
                elements.rentSlider.value = 10000;
                elements.demographicSlider.value = 80;
                elements.competitionSlider.value = 3;
                runSimulation();
                showToast('Simulator parameters reset', 'info');
            });
        }

        // Apply Simulator parameters to live dashboard
        if (elements.applySimBtn) {
            elements.applySimBtn.addEventListener('click', () => {
                // Retrieve computed variables
                const projectedRevenueText = elements.simResultRevenue.textContent;
                const projectedScoreText = elements.simResultScore.textContent;

                // Update the AI recommendation card details in dashboard
                document.getElementById('recExpectedRevenue').textContent = projectedRevenueText;
                document.getElementById('recConfidence').textContent = projectedScoreText;

                const scoreInt = parseInt(projectedScoreText);
                document.querySelector('.score-number').textContent = scoreInt;

                // Animate circle progress
                const circle = document.querySelector('.score-progress');
                if (circle) {
                    // formula: stroke-dashoffset = 264 - (264 * scoreInt / 100)
                    const offset = 264 - (264 * scoreInt / 100);
                    circle.style.strokeDashoffset = offset;
                }

                // Close modal
                elements.simulatorModal.classList.remove('show');
                showToast('Simulation variables successfully applied to spatial model!', 'success');

                // Prepend an entry to our activity timeline
                const now = new Date();
                const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
                const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                
                prependActivity(
                    'Simulated Spatial Forecast Run',
                    'Completed',
                    'Jane Doe',
                    `${dateStr} ${timeStr}`,
                    `Rev: ${projectedRevenueText}, Conf: ${projectedScoreText}`
                );
            });
        }
    }

    // Add entries to the Recent Activity Log
    function prependActivity(name, status, user, dateTime, action) {
        if (!elements.activityTableBody) return;
        
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>
                <div class="activity-title-cell">
                    <i class="bi bi-sliders text-success"></i>
                    <span>${name}</span>
                </div>
            </td>
            <td><span class="badge badge-success">${status}</span></td>
            <td>${user}</td>
            <td>${dateTime}</td>
            <td>${action}</td>
        `;
        
        // Add item to top of list
        elements.activityTableBody.insertBefore(newRow, elements.activityTableBody.firstChild);
        
        // Animate row highlight
        newRow.style.backgroundColor = 'rgba(16, 185, 129, 0.08)';
        setTimeout(() => {
            newRow.style.transition = 'background-color 1s ease';
            newRow.style.backgroundColor = 'transparent';
        }, 1200);
    }

    // Additional general event interactions
    function setupExtraInteractions() {
        // Export report button mock
        if (elements.exportPdfBtn) {
            elements.exportPdfBtn.addEventListener('click', () => {
                showToast('Generating high-fidelity spatial PDF... please wait.', 'info');
                setTimeout(() => {
                    showToast('PDF Export complete! Spatial_Intelligence_Report.pdf downloaded.', 'success');
                }, 2000);
            });
        }

        // Settings warning alert trigger
        if (elements.settingsBtn) {
            elements.settingsBtn.addEventListener('click', () => {
                showToast('Preferences & spatial ML hyperparameters are currently locked by administrator.', 'warning');
            });
        }

        // Logout button trigger
        if (elements.logoutBtn) {
            elements.logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                showToast('Session logout sequence initiated...', 'error');
                setTimeout(() => {
                    showToast('You are currently running in Offline Portfolio mode.', 'info');
                }, 1500);
            });
        }

        // Refresh activity log mock
        if (elements.refreshActivityBtn) {
            elements.refreshActivityBtn.addEventListener('click', () => {
                showToast('Syncing real-time sensor & demographic indexes...', 'info');
                elements.refreshActivityBtn.disabled = true;
                elements.refreshActivityBtn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Syncing...';
                
                setTimeout(() => {
                    elements.refreshActivityBtn.disabled = false;
                    elements.refreshActivityBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh Log';
                    showToast('Activity log database synchronized with Manhattan Q2 retail registry.', 'success');
                }, 1200);
            });
        }
    }

    // Chart.js Visualizations Init
    function initCharts() {
        // Set globally styled Chart.js options
        Chart.defaults.font.family = 'Poppins, sans-serif';
        Chart.defaults.color = '#6B7280';
        Chart.defaults.scale.grid.color = '#E5E7EB';
        
        // 1. Line Chart: Monthly Revenue
        const revCtx = document.getElementById('monthlyRevenueChart');
        if (revCtx) {
            state.charts.revenue = new Chart(revCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    datasets: [
                        {
                            label: 'Actual Revenue ($)',
                            data: [82000, 91000, 105000, 98000, 114000, 125000, 142500, 138000, 151000, 168000, 172000, 185000],
                            borderColor: '#2563EB',
                            borderWidth: 3,
                            backgroundColor: 'rgba(37, 99, 235, 0.05)',
                            fill: true,
                            tension: 0.35,
                            pointBackgroundColor: '#2563EB',
                            pointHoverRadius: 8,
                            pointHoverBackgroundColor: '#FFFFFF',
                            pointHoverBorderColor: '#2563EB',
                            pointHoverBorderWidth: 3
                        },
                        {
                            label: 'AI Forecasted Trend ($)',
                            data: [80000, 90000, 100000, 110000, 120000, 130000, 140000, 150000, 160000, 170000, 180000, 195000],
                            borderColor: '#A78BFA',
                            borderWidth: 2,
                            borderDash: [6, 4],
                            backgroundColor: 'transparent',
                            fill: false,
                            tension: 0.1,
                            pointRadius: 0
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                boxWidth: 15,
                                font: { size: 12, weight: 500 }
                            }
                        },
                        tooltip: {
                            backgroundColor: '#1E293B',
                            titleColor: '#FFFFFF',
                            bodyColor: '#FFFFFF',
                            padding: 12,
                            cornerRadius: 8,
                            displayColors: true,
                            callbacks: {
                                label: function(context) {
                                    return ` ${context.dataset.label.split(' ')[0]}: $${context.parsed.y.toLocaleString()}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return '$' + (value / 1000) + 'k';
                                }
                            }
                        }
                    }
                }
            });

            // Handle Filter Selection change
            const filterSelect = document.getElementById('revenueFilter');
            if (filterSelect) {
                filterSelect.addEventListener('change', (e) => {
                    const months = parseInt(e.target.value, 10);
                    let labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    let actualData = [82000, 91000, 105000, 98000, 114000, 125000, 142500, 138000, 151000, 168000, 172000, 185000];
                    let forecastData = [80000, 90000, 100000, 110000, 120000, 130000, 140000, 150000, 160000, 170000, 180000, 195000];

                    if (months === 6) {
                        labels = labels.slice(6);
                        actualData = actualData.slice(6);
                        forecastData = forecastData.slice(6);
                    }

                    state.charts.revenue.data.labels = labels;
                    state.charts.revenue.data.datasets[0].data = actualData;
                    state.charts.revenue.data.datasets[1].data = forecastData;
                    state.charts.revenue.update();
                    showToast(`Updated Revenue View: Last ${months} Months`, 'success');
                });
            }
        }

        // 2. Pie Chart: Customer Segments
        const custCtx = document.getElementById('customerDistributionChart');
        if (custCtx) {
            state.charts.customers = new Chart(custCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Young Professionals', 'Students & Gen Z', 'Families', 'Corporate Executives'],
                    datasets: [{
                        data: [42, 28, 18, 12],
                        backgroundColor: [
                            '#2563EB', // Primary
                            '#10B981', // Success
                            '#F59E0B', // Warning
                            '#8B5CF6'  // Purple
                        ],
                        hoverOffset: 8,
                        borderWidth: 2,
                        borderColor: '#FFFFFF'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 12,
                                font: { size: 11, weight: 500 }
                            }
                        },
                        tooltip: {
                            backgroundColor: '#1E293B',
                            padding: 10,
                            callbacks: {
                                label: function(context) {
                                    return ` ${context.label}: ${context.parsed}%`;
                                }
                            }
                        }
                    },
                    cutout: '70%'
                }
            });
        }

        // 3. Bar Chart: Regional Sales Performance
        const salesCtx = document.getElementById('areaSalesChart');
        if (salesCtx) {
            state.charts.sales = new Chart(salesCtx, {
                type: 'bar',
                data: {
                    labels: ['Brooklyn', 'Queens', 'Manhattan', 'Bronx', 'Staten Isl.'],
                    datasets: [{
                        label: 'Gross Sales ($k)',
                        data: [124, 98, 248, 72, 45],
                        backgroundColor: [
                            'rgba(37, 99, 235, 0.85)',
                            'rgba(79, 70, 229, 0.85)',
                            'rgba(16, 185, 129, 0.85)',
                            'rgba(245, 158, 11, 0.85)',
                            'rgba(139, 92, 246, 0.85)'
                        ],
                        borderRadius: 6,
                        borderWidth: 0,
                        barThickness: 24
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) { return '$' + value + 'k'; }
                            }
                        }
                    }
                }
            });
        }
    }

    // Toast Notification System
    function showToast(message, type = 'info') {
        if (!elements.toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'bi-info-circle-fill';
        if (type === 'success') icon = 'bi-check-circle-fill';
        if (type === 'error') icon = 'bi-exclamation-octagon-fill';
        if (type === 'warning') icon = 'bi-exclamation-triangle-fill';

        toast.innerHTML = `
            <i class="bi ${icon}"></i>
            <span>${message}</span>
        `;

        elements.toastContainer.appendChild(toast);
        
        // Trigger reflow & show transition
        setTimeout(() => toast.classList.add('show'), 50);

        // Slide out and remove toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }
});
