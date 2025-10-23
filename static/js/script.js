// ===== Scroll to About section =====
document.querySelector('a[href="about.html"]')?.addEventListener("click", (e) => {
  e.preventDefault();
  document.getElementById("about")?.scrollIntoView({ behavior: "smooth" });
});

// ===== Scroll to Contact (footer) =====
document.querySelector('a[href="#contact"]')?.addEventListener("click", (e) => {
  e.preventDefault();
  document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" });
});

// ===== Login button =====
document.querySelector('.login-btn')?.addEventListener("click", (e) => {
  e.preventDefault();
  alert("Login popup coming soon!");
});

// ===== Account Check Modal System =====
let currentUserType = null; // 'vendor' or 'supplier'



// Hide account check modal
function hideAccountCheckModal() {
  const modal = document.getElementById('accountCheckModal');
  modal.style.display = 'none';
  currentUserType = null;
}

// Handle account check responses
function handleHasAccount() {
  hideAccountCheckModal();
  // Redirect to login page
  window.location.href = 'login.html';
}

function handleNoAccount() {
  hideAccountCheckModal();
  // Redirect to appropriate signup page
  if (currentUserType === 'vendor') {
    window.location.href = 'vendorsignup.html';
  } else if (currentUserType === 'supplier') {
    window.location.href = 'suppliersignup.html';
  }
}

// Initialize account check system
document.addEventListener('DOMContentLoaded', function() {
  // Get all the elements
  const vendorBtn = document.getElementById('vendorBtn');
  const supplierBtn = document.getElementById('supplierBtn');
  
  // Vendor flow elements
  const vendorChoice = document.getElementById('vendorChoice');
  const loginChoice = document.getElementById('loginChoice');
  const signupChoice = document.getElementById('signupChoice');
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  
  // Supplier flow elements
  const supplierChoice = document.getElementById('supplierChoice');
  const supplierLoginChoice = document.getElementById('supplierLoginChoice');
  const supplierSignupChoice = document.getElementById('supplierSignupChoice');
  const supplierLoginForm = document.getElementById('supplierLoginForm');
  const supplierSignupForm = document.getElementById('supplierSignupForm');
  
  // Hide all sections initially
  function hideAllSections() {
    const sections = [vendorChoice, loginForm, signupForm, supplierChoice, supplierLoginForm, supplierSignupForm];
    sections.forEach(section => {
      if (section) section.classList.add('hidden');
    });
  }
  
  // Show a specific section
  function showSection(section) {
    if (section) section.classList.remove('hidden');
  }
  
  // Handle vendor button click
  if (vendorBtn) {
    vendorBtn.addEventListener('click', function() {
      hideAllSections();
      showSection(vendorChoice);
    });
  }
  
  // Handle supplier button click
  if (supplierBtn) {
    supplierBtn.addEventListener('click', function() {
      hideAllSections();
      showSection(supplierChoice);
    });
  }
  
  // Handle vendor login choice
  if (loginChoice) {
    loginChoice.addEventListener('click', function() {
      window.location.href = 'login.html';
    });
  }
  
  // Handle vendor signup choice
  if (signupChoice) {
    signupChoice.addEventListener('click', function() {
      window.location.href = 'vendorsignup.html';
    });
  }
  
  // Handle supplier login choice
  if (supplierLoginChoice) {
    supplierLoginChoice.addEventListener('click', function() {
      window.location.href = 'login.html';
    });
  }
  
  // Handle supplier signup choice
  if (supplierSignupChoice) {
    supplierSignupChoice.addEventListener('click', function() {
      window.location.href = 'suppliersignup.html';
    });
  }
});

// ===== Create Account buttons (legacy - now handled above) =====
document.querySelectorAll('.create-btn')?.forEach(btn => {
  btn.addEventListener("click", () => {
    alert("Create Account feature coming soon!");
  });
});

// ===== Order Now buttons =====
document.querySelectorAll('.action-btn')?.forEach(btn => {
  btn.addEventListener("click", () => {
    alert("Your order has been placed successfully!");
  });
});

// ===== Dynamic Price Comparison System =====

// Real vegetable price data (simulated market prices)
const vegetablePrices = {
  onions: { basePrice: 25, variation: 0.3, suppliers: [
    { name: "Fresh Farm Supplies", icon: "fas fa-crown", color: "#27ae60", note: "Best Price · Verified", rating: 4.8, distance: 2.3 },
    { name: "Delhi Vegetable Market", icon: "fas fa-store", color: "#3498db", note: "Traditional Supplier", rating: 4.2, distance: 4.1 },
    { name: "Quick Supply Co", icon: "fas fa-truck", color: "#c0392b", note: "Fast Delivery", rating: 4.0, distance: 1.5 },
    { name: "Green Valley Farms", icon: "fas fa-seedling", color: "#27ae60", note: "Organic Certified", rating: 4.5, distance: 3.2 },
    { name: "Metro Wholesale", icon: "fas fa-warehouse", color: "#9b59b6", note: "Bulk Discounts", rating: 4.3, distance: 5.8 }
  ]},
  tomatoes: { basePrice: 35, variation: 0.4, suppliers: [
    { name: "Fresh Farm Supplies", icon: "fas fa-crown", color: "#27ae60", note: "Best Price · Verified", rating: 4.8, distance: 2.3 },
    { name: "Delhi Vegetable Market", icon: "fas fa-store", color: "#3498db", note: "Traditional Supplier", rating: 4.2, distance: 4.1 },
    { name: "Quick Supply Co", icon: "fas fa-truck", color: "#c0392b", note: "Fast Delivery", rating: 4.0, distance: 1.5 },
    { name: "Green Valley Farms", icon: "fas fa-seedling", color: "#27ae60", note: "Organic Certified", rating: 4.5, distance: 3.2 }
  ]},
  potatoes: { basePrice: 20, variation: 0.25, suppliers: [
    { name: "Fresh Farm Supplies", icon: "fas fa-crown", color: "#27ae60", note: "Best Price · Verified", rating: 4.8, distance: 2.3 },
    { name: "Delhi Vegetable Market", icon: "fas fa-store", color: "#3498db", note: "Traditional Supplier", rating: 4.2, distance: 4.1 },
    { name: "Quick Supply Co", icon: "fas fa-truck", color: "#c0392b", note: "Fast Delivery", rating: 4.0, distance: 1.5 },
    { name: "Metro Wholesale", icon: "fas fa-warehouse", color: "#9b59b6", note: "Bulk Discounts", rating: 4.3, distance: 5.8 }
  ]},
  carrots: { basePrice: 30, variation: 0.35, suppliers: [
    { name: "Fresh Farm Supplies", icon: "fas fa-crown", color: "#27ae60", note: "Best Price · Verified", rating: 4.8, distance: 2.3 },
    { name: "Green Valley Farms", icon: "fas fa-seedling", color: "#27ae60", note: "Organic Certified", rating: 4.5, distance: 3.2 },
    { name: "Quick Supply Co", icon: "fas fa-truck", color: "#c0392b", note: "Fast Delivery", rating: 4.0, distance: 1.5 },
    { name: "Delhi Vegetable Market", icon: "fas fa-store", color: "#3498db", note: "Traditional Supplier", rating: 4.2, distance: 4.1 }
  ]},
  cabbage: { basePrice: 18, variation: 0.3, suppliers: [
    { name: "Fresh Farm Supplies", icon: "fas fa-crown", color: "#27ae60", note: "Best Price · Verified", rating: 4.8, distance: 2.3 },
    { name: "Delhi Vegetable Market", icon: "fas fa-store", color: "#3498db", note: "Traditional Supplier", rating: 4.2, distance: 4.1 },
    { name: "Metro Wholesale", icon: "fas fa-warehouse", color: "#9b59b6", note: "Bulk Discounts", rating: 4.3, distance: 5.8 },
    { name: "Quick Supply Co", icon: "fas fa-truck", color: "#c0392b", note: "Fast Delivery", rating: 4.0, distance: 1.5 }
  ]},
  cauliflower: { basePrice: 28, variation: 0.4, suppliers: [
    { name: "Fresh Farm Supplies", icon: "fas fa-crown", color: "#27ae60", note: "Best Price · Verified", rating: 4.8, distance: 2.3 },
    { name: "Green Valley Farms", icon: "fas fa-seedling", color: "#27ae60", note: "Organic Certified", rating: 4.5, distance: 3.2 },
    { name: "Delhi Vegetable Market", icon: "fas fa-store", color: "#3498db", note: "Traditional Supplier", rating: 4.2, distance: 4.1 },
    { name: "Quick Supply Co", icon: "fas fa-truck", color: "#c0392b", note: "Fast Delivery", rating: 4.0, distance: 1.5 }
  ]}
};

// Generate realistic price variations
function generatePrice(basePrice, variation) {
  const minPrice = basePrice * (1 - variation);
  const maxPrice = basePrice * (1 + variation);
  return Math.round((Math.random() * (maxPrice - minPrice) + minPrice) * 10) / 10;
}

// Generate star rating display
function generateStars(rating) {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
  
  return '★'.repeat(fullStars) + 
         (hasHalfStar ? '☆' : '') + 
         '☆'.repeat(emptyStars);
}

// Update product display
function updateProductDisplay() {
  const productSelect = document.getElementById('productSelect');
  const quantitySelect = document.getElementById('quantitySelect');
  const selectedProduct = document.getElementById('selectedProduct');
  const selectedQuantity = document.getElementById('selectedQuantity');
  
  const productNames = {
    onions: 'Red Onions',
    tomatoes: 'Tomatoes',
    potatoes: 'Potatoes',
    carrots: 'Carrots',
    cabbage: 'Cabbage',
    cauliflower: 'Cauliflower'
  };
  
  selectedProduct.textContent = productNames[productSelect.value];
  selectedQuantity.textContent = quantitySelect.value;
}

// Load price comparison data
function loadPriceComparison() {
  const productSelect = document.getElementById('productSelect');
  const quantitySelect = document.getElementById('quantitySelect');
  const tableBody = document.getElementById('priceTableBody');
  const loadingIndicator = document.getElementById('loadingIndicator');
  const updateTime = document.getElementById('updateTime');
  const savingsMessage = document.getElementById('savingsMessage');
  
  // Show loading
  loadingIndicator.style.display = 'block';
  tableBody.innerHTML = '';
  
  // Simulate API delay
  setTimeout(() => {
    const selectedProduct = productSelect.value;
    const quantity = parseInt(quantitySelect.value);
    const productData = vegetablePrices[selectedProduct];
    
    if (!productData) return;
    
    // Generate prices for each supplier
    const suppliersWithPrices = productData.suppliers.map(supplier => ({
      ...supplier,
      pricePerKg: generatePrice(productData.basePrice, productData.variation),
      totalPrice: 0
    }));
    
    // Calculate total prices
    suppliersWithPrices.forEach(supplier => {
      supplier.totalPrice = Math.round(supplier.pricePerKg * quantity);
    });
    
    // Sort by price (best price first)
    suppliersWithPrices.sort((a, b) => a.pricePerKg - b.pricePerKg);
    
    // Clear table and populate with new data
    tableBody.innerHTML = '';
    
    suppliersWithPrices.forEach((supplier, index) => {
      const isBestPrice = index === 0;
      const row = document.createElement('tr');
      if (isBestPrice) row.classList.add('best-price-row');
      
      row.innerHTML = `
        <td>
          <span class="supplier-name">
            <i class="${supplier.icon} supplier-icon" style="color:${supplier.color};"></i>
            ${supplier.name}
          </span><br>
          <span class="supplier-note">${supplier.note}</span>
        </td>
        <td class="${isBestPrice ? 'price-green' : ''}">₹${supplier.pricePerKg}</td>
        <td>₹${supplier.totalPrice.toLocaleString()}</td>
        <td>${supplier.distance} km</td>
        <td><span class="rating">${generateStars(supplier.rating)}</span> ${supplier.rating}</td>
        <td><button class="action-btn ${isBestPrice ? 'green' : ''}" onclick="placeOrder('${supplier.name}', '${selectedProduct}', ${quantity})">Order Now</button></td>
      `;
      
      tableBody.appendChild(row);
    });
    
    // Update savings message
    if (suppliersWithPrices.length > 1) {
      const bestPrice = suppliersWithPrices[0].totalPrice;
      const worstPrice = suppliersWithPrices[suppliersWithPrices.length - 1].totalPrice;
      const savings = worstPrice - bestPrice;
      savingsMessage.textContent = `You save ₹${savings} with the best price!`;
    } else {
      savingsMessage.textContent = 'Only one supplier available for this product.';
    }
    
    // Update timestamp
    updateTime.textContent = 'just now';
    
    // Hide loading
    loadingIndicator.style.display = 'none';
  }, 1500); // 1.5 second delay to simulate real API call
}

// Place order function
function placeOrder(supplierName, product, quantity) {
  const productNames = {
    onions: 'Red Onions',
    tomatoes: 'Tomatoes',
    potatoes: 'Potatoes',
    carrots: 'Carrots',
    cabbage: 'Cabbage',
    cauliflower: 'Cauliflower'
  };
  
  alert(`Order placed successfully!\n\nSupplier: ${supplierName}\nProduct: ${productNames[product]}\nQuantity: ${quantity}kg\n\nYou will receive a confirmation call shortly.`);
}

// Initialize price comparison system
document.addEventListener('DOMContentLoaded', function() {
  // Load initial data
  loadPriceComparison();
  
  // Add event listeners
  document.getElementById('productSelect')?.addEventListener('change', () => {
    updateProductDisplay();
    loadPriceComparison();
  });
  
  document.getElementById('quantitySelect')?.addEventListener('change', () => {
    updateProductDisplay();
    loadPriceComparison();
  });
  
  document.getElementById('refreshBtn')?.addEventListener('click', () => {
    loadPriceComparison();
  });
});

// ===== Refresh Prices button (legacy - now handled above) =====
document.querySelector('.refresh-btn')?.addEventListener("click", () => {
  // This is now handled by the dynamic system above
});

// ===== Social Media Links in Footer =====
document.querySelector('.fa-twitter')?.parentElement.setAttribute("href", "https://twitter.com");
document.querySelector('.fa-facebook-f')?.parentElement.setAttribute("href", "https://facebook.com");
document.querySelector('.fa-instagram')?.parentElement.setAttribute("href", "https://instagram.com");

// ===== Features Section Buttons (optional if added later) =====
// Add listeners to buttons like "Powerful Features" or "Smart Price Comparison" if added in nav
document.querySelector('a[href="#features"]')?.addEventListener("click", (e) => {
  e.preventDefault();
  document.querySelector(".features-section")?.scrollIntoView({ behavior: "smooth" });
});

document.querySelector('a[href="#compare"]')?.addEventListener("click", (e) => {
  e.preventDefault();
  document.querySelector(".comparison-section")?.scrollIntoView({ behavior: "smooth" });
});
document.addEventListener('DOMContentLoaded', function() {
  const vendorLoginBtn = document.getElementById('vendorLoginBtn');
  const vendorSignupBtn = document.getElementById('vendorSignupBtn');
  const supplierLoginBtn = document.getElementById('supplierLoginBtn');
  const supplierSignupBtn = document.getElementById('supplierSignupBtn');

  vendorLoginBtn && vendorLoginBtn.addEventListener('click', () => {
    window.location.href = 'login.html';
  });
  vendorSignupBtn && vendorSignupBtn.addEventListener('click', () => {
    window.location.href = 'vendorsignup.html';
  });
  supplierLoginBtn && supplierLoginBtn.addEventListener('click', () => {
    window.location.href = 'login.html';
  });
  supplierSignupBtn && supplierSignupBtn.addEventListener('click', () => {
    window.location.href = 'suppliersignup.html';
  });
});
