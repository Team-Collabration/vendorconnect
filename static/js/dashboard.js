// Dashboard JS: Geolocation + Nearby suppliers + Real-time-like price refresh

async function getJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

function getPosition(options = { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }) {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) return reject(new Error('Geolocation not supported'));
    navigator.geolocation.getCurrentPosition((pos) => resolve(pos.coords), reject, options);
  });
}

async function loadNearbySuppliers(token, radiusKm = 25) {
  let lat = null, lng = null;
  try {
    const coords = await getPosition();
    lat = coords.latitude;
    lng = coords.longitude;
  } catch (_) {
    // fallback could be city center if available; skip for now
  }
  const params = new URLSearchParams();
  if (lat && lng) {
    params.set('lat', lat);
    params.set('lng', lng);
    params.set('radius', radiusKm);
  }
  const data = await getJSON(`/api/accounts/suppliers/?${params.toString()}`, {
    headers: { 'Authorization': token ? `Token ${token}` : undefined }
  });
  return data;
}

function simulateSupplierPrices(suppliers, base = 25, pct = 0.35) {
  return suppliers.map(s => {
    const min = base * (1 - pct);
    const max = base * (1 + pct);
    const price = Math.round((Math.random() * (max - min) + min) * 10) / 10;
    return { ...s, price_per_kg: price };
  }).sort((a,b) => a.price_per_kg - b.price_per_kg);
}

function renderSuppliers(list, containerSelector) {
  const el = document.querySelector(containerSelector);
  if (!el) return;
  el.innerHTML = '';
  list.forEach((s, idx) => {
    const row = document.createElement('div');
    row.className = 'supplier-row';
    row.innerHTML = `
      <div class="name">${s.business_name || (s.user && s.user.username) || 'Supplier'}</div>
      <div class="price ${idx === 0 ? 'best' : ''}">₹${s.price_per_kg ?? '-'} / kg</div>
      <div class="distance">${s.distance_km != null ? s.distance_km + ' km' : '-'}</div>
      <div class="action"><button class="btn">Order</button></div>
    `;
    el.appendChild(row);
  });
}

async function initVendorDashboard() {
  try {
    const suppliers = await loadNearbySuppliers();
    const withPrices = simulateSupplierPrices(suppliers, 28, 0.3);
    renderSuppliers(withPrices, '#nearbySuppliers');
    const refreshBtn = document.getElementById('refreshPrices');
    refreshBtn && refreshBtn.addEventListener('click', async () => {
      const refreshed = simulateSupplierPrices(suppliers, 28, 0.3);
      renderSuppliers(refreshed, '#nearbySuppliers');
      const stamp = document.getElementById('updatedAt');
      if (stamp) stamp.textContent = 'just now';
    });
  } catch (e) {
    console.error(e);
  }
}

async function initSupplierDashboard() {
  try {
    // For suppliers, show nearby vendors (demand)
    const params = new URLSearchParams();
    const data = await getJSON(`/api/accounts/vendors/?${params.toString()}`);
    renderSuppliers(data, '#nearbyVendors');
  } catch (e) {
    console.error(e);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('vendorDashboard')) {
    initVendorDashboard();
  }
  if (document.getElementById('supplierDashboard')) {
    initSupplierDashboard();
  }
});


