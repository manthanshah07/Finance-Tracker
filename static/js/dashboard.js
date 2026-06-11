document.addEventListener("DOMContentLoaded", function () {
    // Check elements
    const ctxCategory = document.getElementById("expenseCategoryChart");
    const ctxMonthly = document.getElementById("expenseMonthlyChart");
    const ctxGrowth = document.getElementById("investmentGrowthChart");

    if (!ctxCategory && !ctxMonthly && !ctxGrowth) return;

    // Load data injected in the templates
    let chartData = {
        categories: [],
        category_totals: [],
        monthly_labels: [],
        monthly_values: [],
        growth_labels: [],
        growth_invested: [],
        growth_current: []
    };

    const dataEl = document.getElementById("chart-data-raw");
    if (dataEl) {
        try {
            chartData = JSON.parse(dataEl.textContent);
        } catch (e) {
            console.error("Error parsing chart data: ", e);
        }
    }

    // Colors
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const textColor = isDark ? "#9ca3af" : "#64748b";
    const gridColor = isDark ? "#1f2937" : "#e2e8f0";

    const baseChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 },
                    color: textColor
                }
            }
        }
    };

    // 1. Expense Category Pie Chart
    let categoryChart = null;
    if (ctxCategory && chartData.categories.length > 0) {
        categoryChart = new Chart(ctxCategory, {
            type: "doughnut",
            data: {
                labels: chartData.categories,
                datasets: [{
                    data: chartData.category_totals,
                    backgroundColor: [
                        "#f87171", // Food
                        "#60a5fa", // Travel
                        "#34d399", // Shopping
                        "#fbbf24", // Entertainment
                        "#a78bfa", // Education
                        "#22d3ee", // Bills
                        "#94a3b8"  // Other
                    ],
                    borderWidth: isDark ? 2 : 1,
                    borderColor: isDark ? "#111827" : "#ffffff"
                }]
            },
            options: {
                ...baseChartOptions,
                plugins: {
                    legend: {
                        position: "right",
                        labels: {
                            color: textColor,
                            font: { family: "'Plus Jakarta Sans', sans-serif" }
                        }
                    }
                },
                cutout: "70%"
            }
        });
    }

    // 2. Monthly Expenses Bar Chart
    let monthlyChart = null;
    if (ctxMonthly && chartData.monthly_labels.length > 0) {
        monthlyChart = new Chart(ctxMonthly, {
            type: "bar",
            data: {
                labels: chartData.monthly_labels,
                datasets: [{
                    label: "Monthly Expenses",
                    data: chartData.monthly_values,
                    backgroundColor: "rgba(59, 130, 246, 0.85)",
                    borderRadius: 6,
                    borderWidth: 0
                }]
            },
            options: {
                ...baseChartOptions,
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: textColor, font: { family: "'Plus Jakarta Sans'" } }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor, font: { family: "'Plus Jakarta Sans'" } }
                    }
                }
            }
        });
    }

    // 3. Investment Growth Line Chart
    let growthChart = null;
    if (ctxGrowth && chartData.growth_labels.length > 0) {
        growthChart = new Chart(ctxGrowth, {
            type: "line",
            data: {
                labels: chartData.growth_labels,
                datasets: [
                    {
                        label: "Total Invested Amount",
                        data: chartData.growth_invested,
                        borderColor: "#64748b",
                        borderWidth: 2,
                        borderDash: [5, 5],
                        backgroundColor: "transparent",
                        tension: 0.3,
                        pointRadius: 3
                    },
                    {
                        label: "Current Market Value",
                        data: chartData.growth_current,
                        borderColor: "#10b981",
                        borderWidth: 3,
                        backgroundColor: "rgba(16, 185, 129, 0.1)",
                        fill: true,
                        tension: 0.3,
                        pointRadius: 4,
                        pointBackgroundColor: "#10b981"
                    }
                ]
            },
            options: {
                ...baseChartOptions,
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: textColor, font: { family: "'Plus Jakarta Sans'" } }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor, font: { family: "'Plus Jakarta Sans'" } }
                    }
                }
            }
        });
    }

    // Update Chart themes when theme toggles
    window.addEventListener("themeChanged", function (e) {
        const dark = e.detail.theme === "dark";
        const newTextColor = dark ? "#9ca3af" : "#64748b";
        const newGridColor = dark ? "#1f2937" : "#e2e8f0";

        const updateChartColors = (chart) => {
            if (!chart) return;
            // Legends
            if (chart.options.plugins && chart.options.plugins.legend) {
                chart.options.plugins.legend.labels.color = newTextColor;
            }
            // Scales
            if (chart.options.scales) {
                if (chart.options.scales.x) {
                    chart.options.scales.x.ticks.color = newTextColor;
                    chart.options.scales.x.grid.color = newGridColor;
                }
                if (chart.options.scales.y) {
                    chart.options.scales.y.ticks.color = newTextColor;
                    chart.options.scales.y.grid.color = newGridColor;
                }
            }
            chart.update();
        };

        updateChartColors(categoryChart);
        updateChartColors(monthlyChart);
        updateChartColors(growthChart);
    });
});
