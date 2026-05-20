document.addEventListener('DOMContentLoaded', () => {

    // ── Init Map ──────────────────────────────
    const map = L.map('map').setView([-23.3522, -46.9185], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Search Center Logic
    let searchCenter = { lat: -23.3522, lng: -46.9185 };
    const searchMarker = L.marker([searchCenter.lat, searchCenter.lng], {
        draggable: true,
        icon: L.divIcon({
            className: 'search-center-marker',
            html: '<div style="background: #2dd4bf; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px #2dd4bf;"></div>'
        })
    }).addTo(map);

    map.on('click', (e) => {
        searchCenter.lat = e.latlng.lat;
        searchCenter.lng = e.latlng.lng;
        searchMarker.setLatLng(e.latlng);
    });

    searchMarker.on('dragend', () => {
        searchCenter.lat = searchMarker.getLatLng().lat;
        searchCenter.lng = searchMarker.getLatLng().lng;
    });


    // ── Elements ──────────────────────────────
    const leadsList     = document.getElementById('leads-list');
    const leadsCount    = document.getElementById('leads-count');
    const searchBtn     = document.getElementById('search-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const statusDot     = document.getElementById('status-dot');
    const statusText    = document.getElementById('status-text');

    // ── Colors per potential ──────────────────
    const colors = {
        'High Potential':   '#f87171',
        'Medium Potential': '#f59e0b',
        'Low Potential':    '#2dd4bf'
    };

    const badgeClass = {
        'High Potential':   'badge-high',
        'Medium Potential': 'badge-med',
        'Low Potential':    'badge-low'
    };

    const badgeLabel = {
        'High Potential':   'High',
        'Medium Potential': 'Med',
        'Low Potential':    'Low'
    };

    // ── Set status pill ───────────────────────
    function setStatus(state) {
        statusDot.className = `status-dot ${state}`;
        statusText.textContent = state === 'loading' ? 'escaneando...' : 'pronto';
    }

    // ── Update stats bar ──────────────────────
    async function updateStats() {
        try {
            const res  = await fetch('/api/stats');
            const data = await res.json();
            document.getElementById('stat-total').textContent   = data.total_leads;
            document.getElementById('stat-no-site').textContent = data.no_website;
            document.getElementById('stat-high').textContent    = data.high_potential;
        } catch (e) {
            console.error('Stats error:', e);
        }
    }

    // ── Main search ───────────────────────────
    async function search() {
        const niche  = document.getElementById('niche-input').value.trim();
        const radius = document.getElementById('radius-input').value;
        if (!niche) {
            document.getElementById('niche-input').focus();
            return;
        }


        // Loading state
        loadingOverlay.style.display = 'flex';
        setStatus('loading');
        leadsList.innerHTML = '';
        leadsCount.textContent = '0 encontrados';

        // Clear map markers
        map.eachLayer(layer => {
            if (layer instanceof L.CircleMarker) map.removeLayer(layer);
        });

        try {
            const res   = await fetch(`/api/search?niche=${encodeURIComponent(niche)}&radius=${radius}&lat=${searchCenter.lat}&lng=${searchCenter.lng}`);

            if (!res.ok) {
                throw new Error(`Server responded with ${res.status}: ${res.statusText}`);
            }

            const leads = await res.json();

            leadsCount.textContent = `${leads.length} encontrados`;

            leads.forEach(lead => {

                // ── Map marker ──
                L.circleMarker([lead.lat, lead.lng], {
                    color:       colors[lead.potential] || '#6b7280',
                    fillColor:   colors[lead.potential] || '#6b7280',
                    fillOpacity: 0.85,
                    radius:      7,
                    weight:      1.5
                })
                .addTo(map)
                .bindPopup(`
                    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;line-height:1.6;">
                        <strong style="color:#e2e8f0">${lead.name}</strong><br>
                        <span style="color:#6b7280">${lead.potential}</span>
                    </div>
                `);

                // ── Lead card ──
                const card = document.createElement('div');
                card.className = 'lead-card';

                const bClass = badgeClass[lead.potential] || 'badge-low';
                const bLabel = badgeLabel[lead.potential] || lead.potential;
                const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(lead.name + ' ' + (lead.address || ''))}`;

                card.innerHTML = `
                    <div class="lead-header">
                        <span class="lead-name">${lead.name}</span>
                        <span class="badge ${bClass}">${bLabel}</span>
                    </div>
                    <div class="lead-details">
                        ${lead.address || 'Endereço não disponível'}<br>
                        ${lead.phone   || 'Sem telefone'}<br>
                        ${lead.website
                            ? `<a href="${lead.website}" target="_blank">↗ Site</a>`
                            : '<span style="color:#374151">sem site</span>'}
                    </div>
                    <div class="lead-actions">
                        <a href="${googleMapsUrl}" target="_blank" class="btn-map">📍 Ver no Maps</a>
                    </div>
                    <div class="lead-approach">
                        <strong>→</strong> ${lead.approach}
                    </div>
                `;

                card.addEventListener('click', () => {
                    map.flyTo([lead.lat, lead.lng], 15, { duration: 0.8 });
                });

                leadsList.appendChild(card);
            });

            await updateStats();

        } catch (err) {
            console.error('Search error:', err);
            leadsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">✕</div>
                    <span style="font-size:12px; line-height:1.4;">
                        <strong style="color: var(--red);">Erro de Busca</strong><br>
                        ${err.message || 'Verifique a configuração da API.'}
                    </span>
                </div>
            `;
            leadsCount.textContent = 'erro';
        } finally {
            loadingOverlay.style.display = 'none';
            setStatus('ready');
        }
    }

    // ── Events ────────────────────────────────
    searchBtn.addEventListener('click', search);

    document.getElementById('niche-input').addEventListener('keydown', e => {
        if (e.key === 'Enter') search();
    });

    // ── Init ──────────────────────────────────
    updateStats();
});

// ── Export ────────────────────────────────────
async function exportLeads(format) {
    const loadingOverlay = document.getElementById('loading-overlay');
    loadingOverlay.style.display = 'flex';

    try {
        const res  = await fetch(`/api/export?format=${format}`);
        const data = await res.json();
        if (data.error) {
            alert(data.error);
        } else {
            alert(`Export completed! File saved to: ${data.path}`);
        }
    } catch (err) {
        alert('Export failed. Please try again.');
    } finally {
        loadingOverlay.style.display = 'none';
    }
}
