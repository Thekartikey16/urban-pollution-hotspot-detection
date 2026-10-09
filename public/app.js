// ==========================================
// P_286 - URBAN POLLUTION HOTSPOT DASHBOARD
// Application JavaScript
// ==========================================


// ==========================================
// STATE
// ==========================================

let summaryData = null;
let mapPointsData = null;
let cityStatsData = null;
let cityPollutionData = null;
let hotspotTableData = null;

let currentCity = "All";


// ==========================================
// PLOTLY DARK THEME LAYOUT
// ==========================================

const DARK_LAYOUT = {
    paper_bgcolor: "transparent",
    plot_bgcolor: "rgba(17, 24, 39, 0.5)",
    font: {
        family: "'Inter', sans-serif",
        color: "#94a3b8",
        size: 12
    },
    margin: { t: 40, r: 20, b: 50, l: 60 },
    xaxis: {
        gridcolor: "rgba(148, 163, 184, 0.06)",
        zerolinecolor: "rgba(148, 163, 184, 0.08)",
        tickfont: { size: 11 }
    },
    yaxis: {
        gridcolor: "rgba(148, 163, 184, 0.06)",
        zerolinecolor: "rgba(148, 163, 184, 0.08)",
        tickfont: { size: 11 }
    }
};

const PLOTLY_CONFIG = {
    responsive: true,
    displayModeBar: true,
    modeBarButtonsToRemove: [
        "select2d", "lasso2d",
        "autoScale2d", "resetScale2d"
    ],
    displaylogo: false
};


// ==========================================
// UTILITY: FORMAT NUMBER
// ==========================================

function formatNumber(num) {

    if (num === null || num === undefined) {
        return "—";
    }

    if (typeof num === "number") {

        if (Number.isInteger(num)) {
            return num.toLocaleString("en-IN");
        }

        return num.toFixed(2);
    }

    return String(num);
}


// ==========================================
// LOAD ALL DATA
// ==========================================

async function loadAllData() {

    try {

        const [
            summaryRes,
            mapRes,
            cityStatsRes,
            cityPollutionRes,
            hotspotRes
        ] = await Promise.all([
            fetch("/data/summary.json"),
            fetch("/data/map_points.json"),
            fetch("/data/city_stats.json"),
            fetch("/data/city_pollution.json"),
            fetch("/data/hotspot_table.json")
        ]);

        summaryData = await summaryRes.json();
        mapPointsData = await mapRes.json();
        cityStatsData = await cityStatsRes.json();
        cityPollutionData = await cityPollutionRes.json();
        hotspotTableData = await hotspotRes.json();

        // Populate city filter
        populateCityFilter();

        // Render all
        renderAll();

    } catch (error) {

        console.error(
            "Error loading data:", error
        );
    }
}


// ==========================================
// POPULATE CITY FILTER
// ==========================================

function populateCityFilter() {

    const select = document.getElementById(
        "city-select"
    );

    if (summaryData && summaryData.cities) {

        summaryData.cities.forEach(city => {

            const option = document.createElement(
                "option"
            );

            option.value = city;
            option.textContent = city;

            select.appendChild(option);
        });
    }

    // Listen for changes
    select.addEventListener("change", (e) => {

        currentCity = e.target.value;

        renderAll();
    });
}


// ==========================================
// RENDER ALL SECTIONS
// ==========================================

function renderAll() {

    renderMetrics();
    renderMap();
    renderPollutionChart();
    renderClusterChart();
    renderCityPM25Chart();
    renderHotspotTable();
}


// ==========================================
// RENDER METRICS
// ==========================================

function renderMetrics() {

    if (!summaryData) return;

    if (currentCity === "All") {

        document.getElementById("val-total")
            .textContent = formatNumber(
                summaryData.total_records
            );

        document.getElementById("val-hotspot")
            .textContent = formatNumber(
                summaryData.hotspot_records
            );

        document.getElementById("val-normal")
            .textContent = formatNumber(
                summaryData.normal_records
            );

        document.getElementById("val-pm25")
            .textContent = formatNumber(
                summaryData.average_pm25
            );

    } else {

        const cityStat = cityStatsData.find(
            c => c.city === currentCity
        );

        if (cityStat) {

            document.getElementById("val-total")
                .textContent = formatNumber(
                    cityStat.total_records
                );

            document.getElementById("val-hotspot")
                .textContent = formatNumber(
                    cityStat.hotspot_records
                );

            document.getElementById("val-normal")
                .textContent = formatNumber(
                    cityStat.normal_records
                );

            document.getElementById("val-pm25")
                .textContent = formatNumber(
                    cityStat.avg_pm25
                );
        }
    }
}


// ==========================================
// RENDER MAP
// ==========================================

function renderMap() {

    if (!mapPointsData) return;

    let points = mapPointsData;

    if (currentCity !== "All") {

        points = points.filter(
            p => p.city === currentCity
        );
    }

    // Update subtitle
    document.getElementById("map-subtitle")
        .textContent = `${points.length.toLocaleString()} points`;

    // Separate hotspot vs normal
    const hotspots = points.filter(
        p => p.status === "HOTSPOT"
    );

    const normals = points.filter(
        p => p.status === "NORMAL"
    );

    const traces = [];

    // Normal points
    if (normals.length > 0) {

        traces.push({
            type: "scattermap",
            lat: normals.map(p => p.lat),
            lon: normals.map(p => p.lon),
            mode: "markers",
            name: "Normal",
            marker: {
                size: 6,
                color: "#10b981",
                opacity: 0.5
            },
            text: normals.map(p =>
                `${p.city}<br>` +
                `PM2.5: ${p.pm25}<br>` +
                `PM10: ${p.pm10}<br>` +
                `Cluster: ${p.cluster}`
            ),
            hoverinfo: "text"
        });
    }

    // Hotspot points
    if (hotspots.length > 0) {

        traces.push({
            type: "scattermap",
            lat: hotspots.map(p => p.lat),
            lon: hotspots.map(p => p.lon),
            mode: "markers",
            name: "Hotspot",
            marker: {
                size: 9,
                color: "#f43f5e",
                opacity: 0.85
            },
            text: hotspots.map(p =>
                `🔴 HOTSPOT<br>` +
                `${p.city}<br>` +
                `PM2.5: ${p.pm25}<br>` +
                `PM10: ${p.pm10}<br>` +
                `Cluster: ${p.cluster}`
            ),
            hoverinfo: "text"
        });
    }

    // Calculate center
    let centerLat = 22.5;
    let centerLon = 82.5;
    let zoom = 4;

    if (currentCity !== "All" && points.length > 0) {

        centerLat = points.reduce(
            (s, p) => s + p.lat, 0
        ) / points.length;

        centerLon = points.reduce(
            (s, p) => s + p.lon, 0
        ) / points.length;

        zoom = 9;
    }

    const layout = {
        ...DARK_LAYOUT,
        margin: { t: 0, r: 0, b: 0, l: 0 },
        map: {
            style: "carto-darkmatter",
            center: {
                lat: centerLat,
                lon: centerLon
            },
            zoom: zoom
        },
        showlegend: true,
        legend: {
            x: 0.01,
            y: 0.99,
            bgcolor: "rgba(17, 24, 39, 0.8)",
            bordercolor: "rgba(148, 163, 184, 0.1)",
            borderwidth: 1,
            font: { color: "#f1f5f9", size: 11 }
        }
    };

    Plotly.react(
        "map-chart",
        traces,
        layout,
        PLOTLY_CONFIG
    );
}


// ==========================================
// RENDER POLLUTION PARAMETERS CHART
// ==========================================

function renderPollutionChart() {

    const pollutants = [
        "PM2.5", "PM10", "NO₂", "CO", "SO₂", "O₃"
    ];

    const pollutantKeys = [
        "pm25", "pm10", "no2", "co", "so2", "o3"
    ];

    let values;

    if (currentCity === "All") {

        const avgKeys = [
            "average_pm25", "average_pm10",
            "average_no2", "average_co",
            "average_so2", "average_o3"
        ];

        values = avgKeys.map(
            k => summaryData[k] || 0
        );

    } else {

        const cityStat = cityStatsData.find(
            c => c.city === currentCity
        );

        if (cityStat) {

            const avgKeys = [
                "avg_pm25", "avg_pm10",
                "avg_no2", "avg_co",
                "avg_so2", "avg_o3"
            ];

            values = avgKeys.map(
                k => cityStat[k] || 0
            );

        } else {
            values = [0, 0, 0, 0, 0, 0];
        }
    }

    const colors = [
        "#f43f5e", "#f97316", "#f59e0b",
        "#06b6d4", "#8b5cf6", "#10b981"
    ];

    const trace = {
        type: "bar",
        x: pollutants,
        y: values,
        marker: {
            color: colors,
            line: {
                color: colors.map(
                    c => c + "33"
                ),
                width: 1
            },
            opacity: 0.85
        },
        hovertemplate:
            "<b>%{x}</b><br>" +
            "Avg: %{y:.2f}<extra></extra>"
    };

    const layout = {
        ...DARK_LAYOUT,
        title: {
            text: currentCity === "All"
                ? "All Cities — Average"
                : `${currentCity} — Average`,
            font: { size: 14, color: "#94a3b8" },
            x: 0.5
        },
        yaxis: {
            ...DARK_LAYOUT.yaxis,
            title: { text: "Concentration", standoff: 10 }
        },
        bargap: 0.3
    };

    Plotly.react(
        "pollution-chart",
        [trace],
        layout,
        PLOTLY_CONFIG
    );
}


// ==========================================
// RENDER CLUSTER DISTRIBUTION CHART
// ==========================================

function renderClusterChart() {

    let clusters;

    if (currentCity === "All") {

        clusters = summaryData.clusters;

    } else {

        const cityStat = cityStatsData.find(
            c => c.city === currentCity
        );

        clusters = cityStat
            ? cityStat.clusters
            : {};
    }

    const clusterLabels = Object.keys(clusters)
        .sort()
        .map(k => `Cluster ${k}`);

    const clusterValues = Object.keys(clusters)
        .sort()
        .map(k => clusters[k]);

    const clusterColors = [
        "#3b82f6", "#8b5cf6",
        "#f43f5e", "#f59e0b"
    ];

    const trace = {
        type: "pie",
        labels: clusterLabels,
        values: clusterValues,
        hole: 0.55,
        marker: {
            colors: clusterColors.slice(
                0, clusterLabels.length
            ),
            line: {
                color: "#0a0e17",
                width: 2
            }
        },
        textinfo: "label+percent",
        textfont: {
            color: "#f1f5f9",
            size: 11
        },
        hovertemplate:
            "<b>%{label}</b><br>" +
            "Records: %{value:,}<br>" +
            "%{percent}<extra></extra>"
    };

    const layout = {
        ...DARK_LAYOUT,
        margin: { t: 40, r: 20, b: 20, l: 20 },
        showlegend: true,
        legend: {
            font: { color: "#94a3b8", size: 11 },
            orientation: "h",
            x: 0.5,
            xanchor: "center",
            y: -0.05
        },
        annotations: [{
            text: currentCity === "All"
                ? "All"
                : currentCity.slice(0, 6),
            x: 0.5,
            y: 0.5,
            font: {
                size: 16,
                color: "#f1f5f9",
                family: "'Inter', sans-serif",
                weight: 700
            },
            showarrow: false
        }]
    };

    Plotly.react(
        "cluster-chart",
        [trace],
        layout,
        PLOTLY_CONFIG
    );
}


// ==========================================
// RENDER CITY PM2.5 COMPARISON CHART
// ==========================================

function renderCityPM25Chart() {

    if (!cityPollutionData) return;

    // Sort cities by PM2.5 descending
    const sorted = [...cityPollutionData].sort(
        (a, b) => b.pm25 - a.pm25
    );

    const cities = sorted.map(c => c.city);
    const pm25Vals = sorted.map(c => c.pm25);

    // Color by value: higher = more red
    const maxPM25 = Math.max(...pm25Vals);

    const barColors = pm25Vals.map(v => {

        const ratio = v / maxPM25;

        if (ratio > 0.7) return "#f43f5e";
        if (ratio > 0.4) return "#f59e0b";
        return "#10b981";
    });

    const trace = {
        type: "bar",
        y: cities,
        x: pm25Vals,
        orientation: "h",
        marker: {
            color: barColors,
            opacity: 0.85,
            line: {
                width: 0
            }
        },
        hovertemplate:
            "<b>%{y}</b><br>" +
            "PM2.5: %{x:.2f}<extra></extra>"
    };

    const layout = {
        ...DARK_LAYOUT,
        margin: { t: 10, r: 30, b: 50, l: 150 },
        xaxis: {
            ...DARK_LAYOUT.xaxis,
            title: {
                text: "Average PM2.5",
                standoff: 10
            }
        },
        yaxis: {
            ...DARK_LAYOUT.yaxis,
            autorange: "reversed",
            tickfont: { size: 11 }
        },
        bargap: 0.2
    };

    // Hide this chart if filtering by single city
    const container = document.getElementById(
        "section-city-pollution"
    );

    if (currentCity !== "All") {
        container.style.display = "none";
        return;
    }

    container.style.display = "block";

    Plotly.react(
        "city-pm25-chart",
        [trace],
        layout,
        PLOTLY_CONFIG
    );
}


// ==========================================
// RENDER HOTSPOT TABLE
// ==========================================

function renderHotspotTable() {

    if (!hotspotTableData) return;

    let data = hotspotTableData;

    if (currentCity !== "All") {

        data = data.filter(
            r => r.city === currentCity
        );
    }

    // Update subtitle
    document.getElementById("table-subtitle")
        .textContent = `${data.length} records`;

    // Build table HTML
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>City</th>
                    <th>Latitude</th>
                    <th>Longitude</th>
                    <th>PM2.5</th>
                    <th>PM10</th>
                    <th>NO₂</th>
                    <th>CO</th>
                    <th>SO₂</th>
                    <th>O₃</th>
                    <th>Cluster</th>
                    <th>Status</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
    `;

    data.forEach(row => {

        const statusClass = row.status === "HOTSPOT"
            ? "hotspot"
            : "normal";

        html += `
            <tr>
                <td>${row.city}</td>
                <td>${row.lat}</td>
                <td>${row.lon}</td>
                <td>${row.pm25}</td>
                <td>${row.pm10}</td>
                <td>${row.no2}</td>
                <td>${row.co}</td>
                <td>${row.so2}</td>
                <td>${row.o3}</td>
                <td>${row.cluster}</td>
                <td>
                    <span class="status-badge ${statusClass}">
                        <span class="dot"></span>
                        ${row.status}
                    </span>
                </td>
                <td>${row.score}</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    if (data.length === 0) {

        html = `
            <div class="loading-overlay">
                <div class="loading-text">
                    No hotspot records found for ${currentCity}
                </div>
            </div>
        `;
    }

    document.getElementById(
        "hotspot-table-container"
    ).innerHTML = html;
}


// ==========================================
// INITIALIZE
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    loadAllData
);
