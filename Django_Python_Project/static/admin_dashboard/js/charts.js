/**
 * ElectroShop Admin Dashboard Charts
 * Sử dụng Chart.js để hiển thị biểu đồ thống kê
 */

document.addEventListener('DOMContentLoaded', function() {
    // Load chart data từ API
    loadRevenueChart();
    loadOrderStatusChart();
    loadSentimentChart();
    loadCategoryChart();
});

/**
 * Biểu đồ doanh thu theo ngày
 */
async function loadRevenueChart() {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;
    
    try {
        const response = await fetch('/admin/api/chart-data/?type=revenue');
        const data = await response.json();
        
        new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    } catch (error) {
        console.error('Error loading revenue chart:', error);
        showChartError(ctx, 'Không thể tải dữ liệu doanh thu');
    }
}

/**
 * Biểu đồ trạng thái đơn hàng
 */
async function loadOrderStatusChart() {
    const ctx = document.getElementById('orderStatusChart');
    if (!ctx) return;
    
    try {
        const response = await fetch('/admin/api/chart-data/?type=orders');
        const data = await response.json();
        
        new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 10
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading order status chart:', error);
        showChartError(ctx, 'Không thể tải dữ liệu đơn hàng');
    }
}

/**
 * Biểu đồ phân tích sentiment
 */
async function loadSentimentChart() {
    const ctx = document.getElementById('sentimentChart');
    if (!ctx) return;
    
    try {
        const response = await fetch('/admin/api/chart-data/?type=sentiment');
        const data = await response.json();
        
        new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            padding: 15
                        }
                    }
                },
                cutout: '60%'
            }
        });
    } catch (error) {
        console.error('Error loading sentiment chart:', error);
        showChartError(ctx, 'Không thể tải dữ liệu sentiment');
    }
}

/**
 * Biểu đồ doanh thu theo danh mục
 */
async function loadCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    try {
        const response = await fetch('/admin/api/chart-data/?type=category');
        const data = await response.json();
        
        new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading category chart:', error);
        showChartError(ctx, 'Không thể tải dữ liệu danh mục');
    }
}

/**
 * Format số tiền VNĐ
 */
function formatCurrency(value) {
    if (value >= 1000000000) {
        return (value / 1000000000).toFixed(1) + ' tỷ';
    } else if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + ' tr';
    } else if (value >= 1000) {
        return (value / 1000).toFixed(0) + 'k';
    }
    return value.toLocaleString('vi-VN') + 'đ';
}

/**
 * Hiển thị lỗi khi không load được chart
 */
function showChartError(canvas, message) {
    const parent = canvas.parentElement;
    const errorDiv = document.createElement('div');
    errorDiv.className = 'chart-error';
    errorDiv.innerHTML = `<p style="color: #999; text-align: center; padding: 40px 0;">
        ⚠️ ${message}
    </p>`;
    canvas.style.display = 'none';
    parent.appendChild(errorDiv);
}
