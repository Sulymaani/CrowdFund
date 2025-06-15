// Dashboard Charts for CrowdFund Organization Portal
let donationTrendsChart; // Global reference for updating chart periods
let weeklyData, monthlyData, yearlyData; // Data for different periods

document.addEventListener('DOMContentLoaded', function() {
    // Monthly Donations Chart
    const donationsCtx = document.getElementById('monthlyDonationsChart');
    if (donationsCtx) {
        const donationData = JSON.parse(donationsCtx.dataset.donations || '{}');
        new Chart(donationsCtx, {
            type: 'bar',
            data: {
                labels: donationData.labels || [],
                datasets: [{
                    label: 'Monthly Donations',
                    data: donationData.values || [],
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '$' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    // Campaign Performance Chart
    const campaignPerformanceCtx = document.getElementById('campaignPerformanceChart');
    if (campaignPerformanceCtx) {
        const campaignData = JSON.parse(campaignPerformanceCtx.dataset.campaigns);
        new Chart(campaignPerformanceCtx, {
            type: 'horizontalBar',
            data: {
                labels: campaignData.labels,
                datasets: [{
                    label: 'Raised',
                    data: campaignData.raised,
                    backgroundColor: 'rgba(16, 185, 129, 0.5)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Goal',
                    data: campaignData.goals,
                    backgroundColor: 'rgba(209, 213, 219, 0.5)',
                    borderColor: 'rgba(209, 213, 219, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed.x;
                                return label + ': $' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    // Donation Sources Pie Chart
    const donationSourcesCtx = document.getElementById('donationSourcesChart');
    if (donationSourcesCtx) {
        console.log('Found donation sources chart element, data-sources:', donationSourcesCtx.dataset.sources);
        let sourcesData;
        let labels = [];
        let values = [];
        
        try {
            const parsedData = JSON.parse(donationSourcesCtx.dataset.sources || '{}');
            console.log('Parsed source data format:', parsedData);
            
            if (Array.isArray(parsedData)) {
                // If array format with source/amount objects
                sourcesData = parsedData;
                labels = sourcesData.map(item => item.source);
                values = sourcesData.map(item => item.amount);
            } else {
                // If labels/values format
                sourcesData = parsedData;
                labels = parsedData.labels || ['Direct', 'Social Media', 'Email', 'Referral', 'Other'];
                values = parsedData.values || [40, 25, 20, 10, 5];
            }
        } catch (e) {
            console.error('Error parsing donation sources data:', e);
            // Default data
            labels = ['Direct', 'Social Media', 'Website', 'Other'];
            values = [2450, 1280, 1865, 587];
        }

        new Chart(donationSourcesCtx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',  // Blue
                        'rgba(16, 185, 129, 0.8)', // Green
                        'rgba(245, 158, 11, 0.8)', // Yellow
                        'rgba(139, 92, 246, 0.8)'  // Purple
                    ],
                    borderColor: [
                        'rgba(59, 130, 246, 1)',
                        'rgba(16, 185, 129, 1)',
                        'rgba(245, 158, 11, 1)',
                        'rgba(139, 92, 246, 1)'
                    ],
                    borderWidth: 1,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                                const value = context.parsed;
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${context.label}: $${value.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    }
    
    // Donation Trends Chart with period switching
    const donationTrendsCtx = document.getElementById('donationChart');
    if (donationTrendsCtx) {
        console.log('Found donation chart element, data-trends:', donationTrendsCtx.dataset.trends);
        let trendsData;
        try {
            // If empty, use defaults
            if (!donationTrendsCtx.dataset.trends || donationTrendsCtx.dataset.trends === '{}' || donationTrendsCtx.dataset.trends === '') {
                console.log('No trends data found, using defaults');
                trendsData = {};
            } else {
                trendsData = JSON.parse(donationTrendsCtx.dataset.trends);
                console.log('Parsed trends data:', trendsData);
            }
        } catch (e) {
            console.error('Error parsing donation trends data:', e);
            trendsData = {};
        }
        
        // Initialize data for different periods (or use sample data if not available)
        weeklyData = trendsData.weekly || {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            values: [125, 232, 187, 290, 346, 402, 501]
        };
        
        monthlyData = trendsData.monthly || {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            values: [1250, 1432, 1687, 1890]
        };
        
        yearlyData = trendsData.yearly || {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            values: [5250, 4890, 6540, 5780, 6432, 7230, 6890, 7654, 8320, 7890, 8765, 9230]
        };
        
        // Create the initial chart with weekly data
        donationTrendsChart = new Chart(donationTrendsCtx, {
            type: 'line',
            data: {
                labels: weeklyData.labels,
                datasets: [{
                    label: 'Donations',
                    data: weeklyData.values,
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                    pointRadius: 4,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '$' + context.parsed.y.toLocaleString();
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Sparkline for KPI cards
    const donationsTrendSparkline = document.getElementById('donationsTrendSparkline');
    if (donationsTrendSparkline) {
        const trendData = JSON.parse(donationsTrendSparkline.dataset.trend || '[0,0,0,0,0,0,0]');
        new Chart(donationsTrendSparkline, {
            type: 'line',
            data: {
                labels: new Array(trendData.length).fill(''),
                datasets: [{
                    data: trendData,
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                elements: {
                    line: {
                        borderColor: '#10b981'
                    }
                }
            }
        });
    }
});

// Chart period switching function
function switchChartPeriod(period) {
    if (!donationTrendsChart) return;
    
    let chartData, chartTitle;
    
    // Update button styles
    const buttons = document.querySelectorAll('[onclick^="switchChartPeriod"]');
    buttons.forEach(btn => {
        btn.classList.remove('bg-blue-100', 'text-blue-600');
        btn.classList.add('bg-gray-100', 'text-gray-600');
    });
    
    // Set active button
    const activeButton = document.querySelector(`[onclick*="'${period}'"]`);
    if (activeButton) {
        activeButton.classList.remove('bg-gray-100', 'text-gray-600');
        activeButton.classList.add('bg-blue-100', 'text-blue-600');
    }
    
    // Set chart data based on selected period
    switch(period) {
        case 'week':
            chartData = weeklyData;
            chartTitle = 'Weekly Donations';
            break;
        case 'month':
            chartData = monthlyData;
            chartTitle = 'Monthly Donations';
            break;
        case 'year':
            chartData = yearlyData;
            chartTitle = 'Yearly Donations';
            break;
        default:
            chartData = weeklyData;
            chartTitle = 'Weekly Donations';
    }
    
    // Update chart data
    donationTrendsChart.data.labels = chartData.labels;
    donationTrendsChart.data.datasets[0].data = chartData.values;
    donationTrendsChart.options.plugins.title = {
        display: true,
        text: chartTitle
    };
    donationTrendsChart.update();
}

document.addEventListener('DOMContentLoaded', function() {
    // KPI sparklines
    const sparklineOptions = {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            },
            elements: {
                point: {
                    radius: 0
                },
                line: {
                    tension: 0.4
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: false
                }
            }
        }
    };

    // Donations Trend Sparkline
    const donationsTrendCtx = document.getElementById('donationsTrendSparkline');
    if (donationsTrendCtx) {
        const trendData = JSON.parse(donationsTrendCtx.dataset.trend);
        new Chart(donationsTrendCtx, {
            ...sparklineOptions,
            data: {
                labels: Array.from({length: trendData.length}, (_, i) => i + 1),
                datasets: [{
                    data: trendData,
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    fill: true,
                    borderWidth: 2
                }]
            }
        });
    }

    // Campaigns Trend Sparkline
    const campaignsTrendCtx = document.getElementById('campaignsTrendSparkline');
    if (campaignsTrendCtx) {
        const trendData = JSON.parse(campaignsTrendCtx.dataset.trend);
        new Chart(campaignsTrendCtx, {
            ...sparklineOptions,
            data: {
                labels: Array.from({length: trendData.length}, (_, i) => i + 1),
                datasets: [{
                    data: trendData,
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    fill: true,
                    borderWidth: 2
                }]
            }
        });
    }

    // Donors Trend Sparkline
    const donorsTrendCtx = document.getElementById('donorsTrendSparkline');
    if (donorsTrendCtx) {
        const trendData = JSON.parse(donorsTrendCtx.dataset.trend);
        new Chart(donorsTrendCtx, {
            ...sparklineOptions,
            data: {
                labels: Array.from({length: trendData.length}, (_, i) => i + 1),
                datasets: [{
                    data: trendData,
                    backgroundColor: 'rgba(139, 92, 246, 0.2)',
                    borderColor: 'rgba(139, 92, 246, 1)',
                    fill: true,
                    borderWidth: 2
                }]
            }
        });
    }
});
