document.addEventListener('DOMContentLoaded', () => {
  const API_BASE = '/api/accounts';

  // Get CSRF token from cookie (standard for AJAX requests)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  async function postJSON(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      credentials: 'same-origin',
      body: JSON.stringify(data)
    });
    const text = await res.text();
    let json;
    try { json = JSON.parse(text); } catch { json = { raw: text }; }
    if (!res.ok) {
      const msg = json && (json.detail || JSON.stringify(json));
      throw new Error(msg || `Request failed: ${res.status}`);
    }
    return json;
  }

  function usernameFromEmail(email) {
    const at = email.indexOf('@');
    return at > 0 ? email.slice(0, at) : email;
  }

  // LOGIN: Vendor and Supplier forms on login.html
  const vendorLoginForm = document.querySelector('form.vendor');
  vendorLoginForm && vendorLoginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = vendorLoginForm.querySelector('input[type="email"]').value.trim();
    const password = vendorLoginForm.querySelector('input[type="password"]').value.trim();
    if (!email || !password) return alert('Please fill all fields');
    try {
      // Send the email directly; backend now accepts email or username
      await postJSON(`${API_BASE}/login/`, { username: email, password });
      window.location.href = 'vendordashboard.html';
    } catch (err) {
      alert(`Login failed: ${err.message}`);
    }
  });

  const supplierLoginForm = document.querySelector('form.supplier');
  supplierLoginForm && supplierLoginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = supplierLoginForm.querySelector('input[type="email"]').value.trim();
    const password = supplierLoginForm.querySelector('input[type="password"]').value.trim();
    if (!email || !password) return alert('Please fill all fields');
    try {
      await postJSON(`${API_BASE}/login/`, { username: email, password });
      window.location.href = 'suppliers-dashboard.html';
    } catch (err) {
      alert(`Login failed: ${err.message}`);
    }
  });

  // SIGNUP: Vendor
  const vendorSignupForm = document.querySelector('.signup-page .signup-form');
  if (vendorSignupForm && document.title.includes('Vendor Sign Up')) {
    vendorSignupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const firstName = vendorSignupForm.querySelector('#firstName')?.value.trim();
      const lastName = vendorSignupForm.querySelector('#lastName')?.value.trim();
      const email = vendorSignupForm.querySelector('#email')?.value.trim();
      const phone = vendorSignupForm.querySelector('#vendorPhone')?.value.trim();
      const password = vendorSignupForm.querySelector('#password')?.value.trim();
      const confirmPassword = vendorSignupForm.querySelector('#confirmPassword')?.value.trim();
      if (!email || !password || !confirmPassword || !phone) return alert('Please fill all required fields');
      const payload = {
        username: usernameFromEmail(email),
        email,
        password,
        password_confirm: confirmPassword,
        user_type: 'vendor',
        phone_number: phone,
        business_name: `${firstName || ''} ${lastName || ''}`.trim(),
      };
      try {
        await postJSON(`${API_BASE}/register/`, payload);
        alert('Vendor account created!');
        window.location.href = 'vendordashboard.html';
      } catch (err) {
        alert(`Signup failed: ${err.message}`);
      }
    });
  }

  // SIGNUP: Supplier
  const supplierSignupForm = document.querySelector('.signup-container form');
  if (supplierSignupForm && document.title.includes('Supplier Sign Up')) {
    supplierSignupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const firstName = supplierSignupForm.querySelector('#firstName')?.value.trim();
      const lastName = supplierSignupForm.querySelector('#lastName')?.value.trim();
      const email = supplierSignupForm.querySelector('#email')?.value.trim();
      const phone = supplierSignupForm.querySelector('#phone')?.value.trim();
      const password = supplierSignupForm.querySelector('#password')?.value.trim();
      const confirmPassword = supplierSignupForm.querySelector('#confirmPassword')?.value.trim();
      if (!email || !password || !confirmPassword || !phone) return alert('Please fill all required fields');
      const payload = {
        username: usernameFromEmail(email),
        email,
        password,
        password_confirm: confirmPassword,
        user_type: 'supplier',
        phone_number: phone,
        business_name: `${firstName || ''} ${lastName || ''}`.trim(),
      };
      try {
        await postJSON(`${API_BASE}/register/`, payload);
        alert('Supplier account created!');
        window.location.href = 'suppliers-dashboard.html';
      } catch (err) {
        alert(`Signup failed: ${err.message}`);
      }
    });
  }

  // GOOGLE LOGIN (both vendor/supplier pages include buttons with class .google-signup)
  async function googleLogin(idToken, userType, businessName) {
    try {
      await postJSON(`${API_BASE}/google-login/`, {
        id_token: idToken,
        user_type: userType,
        business_name: businessName || ''
      });
      if (userType === 'supplier') window.location.href = 'suppliers-dashboard.html';
      else window.location.href = 'vendordashboard.html';
    } catch (err) {
      alert(`Google login failed: ${err.message}`);
    }
  }

  // Bind Google button (using Google Identity Services token from window.google
  const googleVendorBtn = document.querySelector('.signup-page .google-signup');
  googleVendorBtn && googleVendorBtn.addEventListener('click', async () => {
    // Expect a global function getGoogleIdToken() implemented via GIS widget integration
    if (window.getGoogleIdToken) {
      const token = await window.getGoogleIdToken();
      await googleLogin(token, 'vendor', 'Google Vendor');
    } else {
      alert('Google Sign-In not initialized yet');
    }
  });

  const googleSupplierBtn = document.querySelector('.signup-container .google-signup');
  googleSupplierBtn && googleSupplierBtn.addEventListener('click', async () => {
    if (window.getGoogleIdToken) {
      const token = await window.getGoogleIdToken();
      await googleLogin(token, 'supplier', 'Google Supplier');
    } else {
      alert('Google Sign-In not initialized yet');
    }
  });
});

function logout() {
  window.location.href = 'suppliers-dashboard.html';
}