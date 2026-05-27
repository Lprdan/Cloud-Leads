document.addEventListener('DOMContentLoaded', () => {

    // ── Init Map ──────────────────────────────
    let map;
    let searchMarker;
    let searchCenter = { lat: -23.3522, lng: -46.9185 };

    try {
        map = L.map('map').setView([-23.3522, -46.9185], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        searchMarker = L.marker([searchCenter.lat, searchCenter.lng], {
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

        setTimeout(() => {
            if (map) map.invalidateSize();
        }, 500);

    } catch (e) {
        console.error('Map setup failed!', e);
        document.getElementById('map').innerHTML = `<div style="background:#1f2937;color:#ef4444;display:flex;align-items:center;justify-content:center;height:100%;text-align:center;padding:20px;font-family:monospace;font-size:12px;">
            Erro crítico no mapa. Veja o console (F12).
        </div>`;
    }


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
        leadsCount.textContent = 'Iniciando busca...';

        // Clear map markers
        map.eachLayer(layer => {
            if (layer instanceof L.CircleMarker) map.removeLayer(layer);
        });

        try {
            const res = await fetch(`/api/search?niche=${encodeURIComponent(niche)}&radius=${radius}&lat=${searchCenter.lat}&lng=${searchCenter.lng}`);

            if (!res.ok) throw new Error(`Erro no servidor: ${res.status}`);
            const data = await res.json();

            if (data.status === 'processing') {
                // ── Start Polling ──
                leadsCount.textContent = 'Processando leads no Worker...';
                await pollForLeads();
            } else if (Array.isArray(data)) {
                // Fallback for synchronous response (if it's already a list)
                renderLeads(data);
            } else {
                throw new Error(data.message || 'A busca não retornou leads no formato esperado.');
            }

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
            loadingOverlay.style.display = 'none';
            setStatus('ready');
        }
    }

    async function pollForLeads() {
        const maxAttempts = 60; // ~3 minutes
        let attempts = 0;

        while (attempts < maxAttempts) {
            attempts++;
            try {
                const res = await fetch('/api/leads');
                if (!res.ok) throw new Error('Network response was not ok');

                const leads = await res.json();

                if (Array.isArray(leads) && leads.length > 0) {
                    renderLeads(leads);
                    break;
                }
            } catch (e) {
                console.error('Polling error:', e);
            }

            // Update count every 3 seconds
            leadsCount.textContent = `Aguardando Worker... (${attempts * 3}s)`;
            await new Promise(resolve => setTimeout(resolve, 3000));
        }

        if (attempts >= maxAttempts) {
            leadsCount.textContent = 'Tempo esgotado';
            leadsList.innerHTML = '<div class="empty-state">Busca demorou demais. Tente novamente.</div>';
        }

        loadingOverlay.style.display = 'none';
        setStatus('ready');
    }

    async function renderLeads(leads) {
        if (!Array.isArray(leads)) {
            console.error('renderLeads expected an array, got:', leads);
            return;
        }
        leadsCount.textContent = `${leads.length} encontrados`;

        leadsList.innerHTML = ''; // Clear list before rendering

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
                    ${lead.instagram ? `<br><a href="${lead.instagram}" target="_blank" style="color:var(--cyan)">📸 Instagram</a>` : ''}
                    ${lead.linkedin ? `<br><a href="${lead.linkedin}" target="_blank" style="color:var(--cyan)">💼 LinkedIn</a>` : ''}
                    ${lead.email ? `<br><span style="color:var(--text-muted)">✉️ ${lead.email}</span>` : ''}
                    <div style="margin-top:4px; font-size:10px; color:var(--text-dimmer)">
                        Tech: ${lead.tech_stack || 'Desconhecida'} | Pegada: ${lead.digital_footprint || 'Baixa'}
                    </div>
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
