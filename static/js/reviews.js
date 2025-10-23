const form = document.getElementById('reviewForm');
const successMessage = document.getElementById('successMessage');
const reviewList = document.getElementById('reviewList');

document.addEventListener("DOMContentLoaded", showReviews);

form.addEventListener('submit', function (e) {
  e.preventDefault();

  const supplier = document.getElementById('supplier').value.trim();
  const name = document.getElementById('name').value.trim();
  const review = document.getElementById('review').value.trim();

  if (supplier && name && review) {
    const newReview = { supplier, name, review };

    let reviews = JSON.parse(localStorage.getItem("reviews")) || [];
    reviews.push(newReview);
    localStorage.setItem("reviews", JSON.stringify(reviews));

    successMessage.style.display = 'block';
    form.reset();
    setTimeout(() => successMessage.style.display = 'none', 3000);

    showReviews();
  }
});

function showReviews() {
  const reviews = JSON.parse(localStorage.getItem("reviews")) || [];
  reviewList.innerHTML = "";

  if (reviews.length === 0) {
    reviewList.innerHTML = "<p style='color: #777;'>No reviews yet.</p>";
    return;
  }

  reviews.forEach(({ supplier, name, review }) => {
    const card = document.createElement("div");
    card.style.cssText = `
      background-color: #fffef2;
      padding: 15px;
      border-radius: 8px;
      margin-bottom: 15px;
      border-left: 4px solid #6c82d7;
    `;
    card.innerHTML = `
      <strong>${supplier}</strong><br>
      <em>${name}</em><br>
      <p style="margin-top: 5px;">${review}</p>
    `;
    reviewList.appendChild(card);
  });
}
