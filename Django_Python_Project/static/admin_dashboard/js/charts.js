/**
 * ElectroShop Admin Dashboard Charts
 * Modern Chart.js configurations
 * Note: Chart.js is loaded from CDN in the HTML template
 */

// Chart.js default configurations - Chart is available globally from CDN
if (typeof Chart !== "undefined") {
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    Chart.defaults.color = "#64748b";
}

/**
 * Format currency VND
 */
function formatCurrency(value) {
    if (value >= 1000000000) {
        return (value / 1000000000).toFixed(1) + " tỷ";
    } else if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + " tr";
    } else if (value >= 1000) {
        return (value / 1000).toFixed(0) + "k";
    }
    return value.toLocaleString("vi-VN") + "đ";
}

/**
 * Show chart error message
 */
function showChartError(canvas, message) {
    var parent = canvas.parentElement;
    var errorDiv = document.createElement("div");
    errorDiv.style.cssText = "text-align: center; padding: 60px 20px; color: #94a3b8;";
    errorDiv.innerHTML = '<p style="margin: 0; font-size: 14px;">' + message + "</p>";
    canvas.style.display = "none";
    parent.appendChild(errorDiv);
}
