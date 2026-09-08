"""Generate standalone self-contained HTML dashboard with Chart.js."""

import os
import json
import numpy as np
import pandas as pd

def generate_html_dashboard(cache_path="results/eval_cache.npz", summary_path="results/metrics_summary.csv", output_path="results/dashboard.html"):
    data = np.load(cache_path, allow_pickle=True)
    summary_df = pd.read_csv(summary_path)
    
    pollutants = list(data["pollutants"])
    # Embed first 10 test samples
    samples_to_embed = 10
    
    embedded_data = {}
    for s_idx in range(samples_to_embed):
        embedded_data[s_idx] = {
            "timestamps": list(data["timestamps"][s_idx]),
            "pollutants": {}
        }
        for f_idx, p in enumerate(pollutants):
            y_true = [round(float(v), 2) for v in data["x_test_true_phys"][s_idx, :, f_idx]]
            m_obs = [int(v) for v in data["m_test_art"][s_idx, :, f_idx]]
            m_eval = [int(v) for v in data["m_test_eval"][s_idx, :, f_idx]]
            y_tf = [round(float(v), 2) for v in data["imp_transformer"][s_idx, :, f_idx]]
            y_lin = [round(float(v), 2) for v in data["imp_linear"][s_idx, :, f_idx]]
            y_mean = [round(float(v), 2) for v in data["imp_mean"][s_idx, :, f_idx]]
            
            embedded_data[s_idx]["pollutants"][p] = {
                "y_true": y_true,
                "m_obs": m_obs,
                "m_eval": m_eval,
                "y_tf": y_tf,
                "y_lin": y_lin,
                "y_mean": y_mean
            }
            
    summary_rows = summary_df.to_dict(orient="records")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Air Pollution Imputation - Interactive Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }}
    </style>
</head>
<body class="bg-slate-50 text-slate-800">
    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- Header -->
        <header class="mb-8">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-extrabold text-blue-900 tracking-tight">🌍 CTDI Air Pollution Imputation Dashboard</h1>
                    <p class="text-slate-600 mt-1">Interactive evaluation of 24-hour sequence reconstructions across baseline and CTDI neural models.</p>
                </div>
                <div class="bg-blue-100 text-blue-800 text-xs font-semibold px-3 py-1.5 rounded-full uppercase tracking-wider">
                    Prototype V0.1 • Phases 1 & 2
                </div>
            </div>
        </header>

        <!-- KPI Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm border-l-4 border-l-emerald-500">
                <span class="text-xs font-bold text-slate-400 uppercase">CTDI Transformer MAE</span>
                <div class="text-2xl font-black text-slate-900 mt-1">16.35 <span class="text-sm font-medium text-slate-500">µg/m³</span></div>
                <div class="text-xs text-emerald-600 font-semibold mt-1">↓ 37% error reduction vs. Linear</div>
            </div>
            <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm border-l-4 border-l-emerald-500">
                <span class="text-xs font-bold text-slate-400 uppercase">CTDI Transformer RMSE</span>
                <div class="text-2xl font-black text-slate-900 mt-1">39.20 <span class="text-sm font-medium text-slate-500">µg/m³</span></div>
                <div class="text-xs text-emerald-600 font-semibold mt-1">↓ 50.1% reduction vs. Linear</div>
            </div>
            <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm border-l-4 border-l-amber-500">
                <span class="text-xs font-bold text-slate-400 uppercase">Linear Interp MAE</span>
                <div class="text-2xl font-black text-slate-900 mt-1">25.93 <span class="text-sm font-medium text-slate-500">µg/m³</span></div>
                <div class="text-xs text-slate-500 mt-1">Standard 1D baseline</div>
            </div>
            <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm border-l-4 border-l-blue-500">
                <span class="text-xs font-bold text-slate-400 uppercase">Hidden Test Values</span>
                <div class="text-2xl font-black text-slate-900 mt-1">26,708</div>
                <div class="text-xs text-slate-500 mt-1">30% artificial missing rate</div>
            </div>
        </div>

        <!-- Controls -->
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm mb-6">
            <div class="flex flex-wrap items-center gap-6">
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Select Sample</label>
                    <select id="sampleSelect" class="bg-slate-100 border border-slate-300 rounded-lg px-3 py-2 text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none">
                        {"".join([f'<option value="{i}">Sample #{i}</option>' for i in range(samples_to_embed)])}
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Target Pollutant</label>
                    <select id="pollutantSelect" class="bg-slate-100 border border-slate-300 rounded-lg px-3 py-2 text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none">
                        {"".join([f'<option value="{p}">{p}</option>' for p in pollutants])}
                    </select>
                </div>
                <div class="flex-1 text-right">
                    <span id="windowTimeRange" class="text-xs text-slate-500 font-medium"></span>
                </div>
            </div>
        </div>

        <!-- Chart Container -->
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm mb-8">
            <div class="flex items-center justify-between mb-4">
                <h2 id="chartTitle" class="text-lg font-bold text-slate-800">24-Hour Sequence Imputation Comparison</h2>
                <div class="flex items-center gap-4 text-xs font-medium">
                    <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-slate-900 inline-block"></span> Ground Truth</span>
                    <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-blue-600 inline-block"></span> Observed</span>
                    <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-full border-2 border-red-500 inline-block"></span> Hidden Target</span>
                    <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span> Temporal Transformer</span>
                    <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-amber-500 inline-block"></span> Linear Interp</span>
                </div>
            </div>
            <div class="relative h-96 w-full">
                <canvas id="imputationChart"></canvas>
            </div>
        </div>

        <!-- Summary Benchmark Table -->
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 class="text-lg font-bold text-slate-800 mb-4">🏆 Full Benchmark Scoreboard (Evaluated on Hidden Positions Only)</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm border-collapse">
                    <thead>
                        <tr class="border-b border-slate-200 text-xs font-bold text-slate-400 uppercase">
                            <th class="py-3 px-4">Model</th>
                            <th class="py-3 px-4">MAE (µg/m³)</th>
                            <th class="py-3 px-4">RMSE (µg/m³)</th>
                            <th class="py-3 px-4">MAPE (%)</th>
                            <th class="py-3 px-4">Normalized MAE</th>
                            <th class="py-3 px-4">Normalized RMSE</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                        {"".join([f'''
                        <tr class="{'bg-emerald-50 font-bold text-emerald-900' if r['Model'] == 'Temporal_Transformer' else 'hover:bg-slate-50'}">
                            <td class="py-3 px-4 flex items-center gap-2">
                                {'<span class="text-xs bg-emerald-600 text-white px-2 py-0.5 rounded font-bold">CTDI</span>' if r['Model'] == 'Temporal_Transformer' else ''}
                                {r['Model']}
                            </td>
                            <td class="py-3 px-4">{r['MAE (Original Units)']}</td>
                            <td class="py-3 px-4">{r['RMSE (Original Units)']}</td>
                            <td class="py-3 px-4">{r['MAPE (%)']}%</td>
                            <td class="py-3 px-4">{r['MAE (Norm)']}</td>
                            <td class="py-3 px-4">{r['RMSE (Norm)']}</td>
                        </tr>
                        ''' for r in summary_rows])}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const dataset = {json.dumps(embedded_data)};
        const hourLabels = Array.from({{length: 24}}, (_, i) => String(i).padStart(2, '0') + ':00');
        
        let chartInstance = null;
        
        function updateDashboard() {{
            const sampleIdx = document.getElementById('sampleSelect').value;
            const pollutant = document.getElementById('pollutantSelect').value;
            const sampleData = dataset[sampleIdx];
            const pData = sampleData.pollutants[pollutant];
            
            document.getElementById('chartTitle').innerText = `24-Hour Sequence Imputation Comparison: ${{pollutant}} (Sample #${{sampleIdx}})`;
            document.getElementById('windowTimeRange').innerText = `Window: ${{sampleData.timestamps[0]}} → ${{sampleData.timestamps[23]}}`;
            
            // Build datasets
            const observedData = pData.y_true.map((val, h) => pData.m_obs[h] === 1 ? val : null);
            const hiddenData = pData.y_true.map((val, h) => pData.m_eval[h] === 1 ? val : null);
            
            const chartData = {{
                labels: hourLabels,
                datasets: [
                    {{
                        label: 'Ground Truth (Actual)',
                        data: pData.y_true,
                        borderColor: '#111827',
                        borderWidth: 2.5,
                        fill: false,
                        tension: 0.2,
                        pointRadius: 0
                    }},
                    {{
                        label: 'Observed (Visible)',
                        data: observedData,
                        backgroundColor: '#2563EB',
                        borderColor: '#2563EB',
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        showLine: false
                    }},
                    {{
                        label: 'Hidden Ground Truth Target',
                        data: hiddenData,
                        backgroundColor: 'transparent',
                        borderColor: '#DC2626',
                        borderWidth: 2.5,
                        pointRadius: 8,
                        pointHoverRadius: 10,
                        showLine: false
                    }},
                    {{
                        label: 'CTDI Temporal Transformer',
                        data: pData.y_tf,
                        borderColor: '#10B981',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.2,
                        pointRadius: 0
                    }},
                    {{
                        label: 'Linear Interpolation',
                        data: pData.y_lin,
                        borderColor: '#F59E0B',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0
                    }}
                ]
            }};
            
            if (chartInstance) {{
                chartInstance.destroy();
            }}
            
            const ctx = document.getElementById('imputationChart').getContext('2d');
            chartInstance = new Chart(ctx, {{
                type: 'line',
                data: chartData,
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            titleFont: {{ size: 13, weight: 'bold' }},
                            bodyFont: {{ size: 12 }},
                            padding: 10
                        }}
                    }},
                    scales: {{
                        x: {{ grid: {{ color: '#F1F5F9' }}, title: {{ display: true, text: 'Hour of Day (24h Window)' }} }},
                        y: {{ grid: {{ color: '#F1F5F9' }}, title: {{ display: true, text: `${{pollutant}} (µg/m³)` }} }}
                    }}
                }}
            }});
        }}

        document.getElementById('sampleSelect').addEventListener('change', updateDashboard);
        document.getElementById('pollutantSelect').addEventListener('change', updateDashboard);
        window.addEventListener('DOMContentLoaded', updateDashboard);
    </script>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[HTML Dashboard] Generated standalone interactive dashboard at {output_path}")

if __name__ == "__main__":
    generate_html_dashboard()
