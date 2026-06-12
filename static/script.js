let globalParsedData = null;
let chartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    const fileDropArea = document.getElementById('file-drop-area');
    const fileInput = document.getElementById('pdf-file');
    const fileMsg = document.querySelector('.file-msg');
    const form = document.getElementById('upload-form');
    const loading = document.getElementById('loading');
    const errorMsg = document.getElementById('error-msg');
    
    // Drag and drop handling
    fileDropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileDropArea.classList.add('drag-over');
    });

    fileDropArea.addEventListener('dragleave', () => {
        fileDropArea.classList.remove('drag-over');
    });

    fileDropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        fileDropArea.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            updateFileMsg();
        }
    });

    fileInput.addEventListener('change', updateFileMsg);

    function updateFileMsg() {
        if (fileInput.files.length > 0) {
            fileMsg.textContent = fileInput.files[0].name;
            fileDropArea.style.borderColor = 'var(--primary-color)';
        } else {
            fileMsg.textContent = 'Drag and drop your PDF here or click to choose file';
            fileDropArea.style.borderColor = 'var(--border-color)';
        }
    }

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (fileInput.files.length === 0) {
            showError("Please select a PDF file.");
            return;
        }

        const password = document.getElementById('password').value;
        const statementType = document.getElementById('statement-type').value;
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('password', password);
        formData.append('statement_type', statementType);

        // UI state
        errorMsg.classList.add('hidden');
        loading.classList.remove('hidden');
        document.getElementById('parse-btn').disabled = true;

        try {
            const response = await fetch('/api/parse', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to parse document');
            }

            globalParsedData = data;
            renderDashboard(data);
            
            document.getElementById('upload-section').classList.add('hidden');
            document.getElementById('dashboard-section').classList.remove('hidden');
            
        } catch (err) {
            showError(err.message);
        } finally {
            loading.classList.add('hidden');
            document.getElementById('parse-btn').disabled = false;
        }
    });

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
    }

    // Export button
    document.getElementById('download-excel-btn').addEventListener('click', async () => {
        if (!globalParsedData) return;

        try {
            const btn = document.getElementById('download-excel-btn');
            const originalText = btn.innerHTML;
            btn.innerHTML = "Generating...";
            btn.disabled = true;

            const response = await fetch('/api/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ parsed_data: globalParsedData })
            });

            if (!response.ok) throw new Error('Export failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'CAS_Analysis_Report.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            btn.innerHTML = originalText;
            btn.disabled = false;
        } catch (err) {
            alert("Error downloading Excel: " + err.message);
            document.getElementById('download-excel-btn').disabled = false;
        }
    });

    // Search functionality
    document.getElementById('search-input').addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const rows = document.querySelectorAll('#holdings-body tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    });
});

function formatCurrency(val) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(val);
}

function renderDashboard(data) {
    // Render profile
    document.getElementById('val-name').textContent = data.metadata.investor_name || 'N/A';
    document.getElementById('val-email').textContent = data.metadata.email || 'N/A';
    document.getElementById('val-date').textContent = data.metadata.statement_date || 'N/A';

    // Calculate metrics
    let totalMarket = 0;
    let totalCost = 0;

    const tbody = document.getElementById('holdings-body');
    tbody.innerHTML = '';

    const allocationData = {};

    data.holdings.forEach(h => {
        totalMarket += h.market_value;
        totalCost += h.cost_value;

        // For chart
        const amc = h.scheme_name.split(' ')[0] + ' ' + (h.scheme_name.split(' ')[1] || ''); // roughly AMC name
        allocationData[amc] = (allocationData[amc] || 0) + h.market_value;

        // Table row
        const tr = document.createElement('tr');
        
        const gain = h.market_value - h.cost_value;
        let gainClass = '';
        if (gain > 0) gainClass = 'val-positive';
        else if (gain < 0) gainClass = 'val-negative';

        tr.innerHTML = `
            <td>
                <div><strong>${h.scheme_name}</strong></div>
                <div style="font-size: 0.85em; color: var(--text-secondary)">Folio: ${h.folio}</div>
            </td>
            <td>${h.registrar}</td>
            <td class="num">${h.units.toFixed(3)}</td>
            <td class="num">₹${h.nav.toFixed(4)}</td>
            <td class="num">${formatCurrency(h.cost_value)}</td>
            <td class="num">${formatCurrency(h.market_value)}</td>
            <td class="num ${gainClass}">${formatCurrency(gain)}</td>
        `;
        tbody.appendChild(tr);
    });

    const totalGain = totalMarket - totalCost;
    const gainPct = totalCost > 0 ? (totalGain / totalCost) * 100 : 0;

    // Update metric cards
    document.getElementById('val-market').textContent = formatCurrency(totalMarket);
    document.getElementById('val-cost').textContent = formatCurrency(totalCost);
    
    const elGain = document.getElementById('val-gain');
    elGain.textContent = formatCurrency(totalGain);
    elGain.className = 'metric-value ' + (totalGain >= 0 ? 'val-positive' : 'val-negative');

    const elGainPct = document.getElementById('val-gain-pct');
    elGainPct.textContent = gainPct.toFixed(2) + '%';
    elGainPct.className = 'metric-value ' + (gainPct >= 0 ? 'val-positive' : 'val-negative');

    renderChart(allocationData);
}

function renderChart(dataObj) {
    const ctx = document.getElementById('allocationChart').getContext('2d');
    
    if (chartInstance) {
        chartInstance.destroy();
    }

    // Sort and get top 8, group rest as "Others"
    let sorted = Object.entries(dataObj).sort((a,b) => b[1] - a[1]);
    let labels = [];
    let values = [];
    
    let others = 0;
    for(let i=0; i<sorted.length; i++) {
        if(i < 8) {
            labels.push(sorted[i][0]);
            values.push(sorted[i][1]);
        } else {
            others += sorted[i][1];
        }
    }
    if (others > 0) {
        labels.push("Others");
        values.push(others);
    }

    Chart.defaults.color = '#94A3B8';
    chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#0D9488', '#3B82F6', '#8B5CF6', '#EC4899', 
                    '#F59E0B', '#10B981', '#6366F1', '#F43F5E', '#64748B'
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#F8FAFC' }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) label += ': ';
                            if (context.parsed !== null) {
                                label += new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(context.parsed);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}
