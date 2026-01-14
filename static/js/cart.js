document.addEventListener("DOMContentLoaded", () => {
  bindRemoveItemForms();
  bindClearCartForm();
  bindConfirmOrderForm();
});

/* ---------------------------------------------
   Helpers
----------------------------------------------*/

function getCookie(name) {
    if (!document.cookie) {
        return null;
    }

    // Split document.cookie into an array of individual cookie strings
    const cookies = document.cookie.split(';');

    // Find the cookie that starts with the desired name
    const xsrfCookies = cookies
        .map(c => c.trim())
        .filter(c => c.startsWith(name + '='));

    // If the cookie is not found, return null
    if (xsrfCookies.length === 0) {
        return null;
    }

    // Return the decoded value of the cookie
    return decodeURIComponent(xsrfCookies[0].split('=')[1]);
}

async function request(url, method, body = null, csrfToken = null) {
  const headers = {
    "Content-Type": "application/json",
    "x-csrftoken": csrfToken,
  };


  const response = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
    credentials: "include",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }

  return response.status === 204 ? null : response.json();
}

function reloadCart() {
  window.location.reload();
}

/* ---------------------------------------------
   Remove single cart item
----------------------------------------------*/

function bindRemoveItemForms() {
  const forms = document.querySelectorAll("form[class='inline-form']");

  forms.forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const orderItemId = form.querySelector(
        "input[name='order_item_id']"
      ).value;

      const csrftoken = getCookie('csrftoken');

      try {
        await request(`/cart/items/${orderItemId}`, "DELETE", null, csrftoken);
        reloadCart();
      } catch (err) {
        alert("Failed to remove item from cart");
        console.error(err);
      }
    });
  });
}

/* ---------------------------------------------
   Clear entire cart
----------------------------------------------*/

function bindClearCartForm() {
  const form = document.querySelector("form[action='/cart/clear']");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const csrftoken = getCookie('csrftoken')

    if (!confirm("Are you sure you want to clear the cart?")) {
      return;
    }

    try {
      await request("/cart/clear", "DELETE", null, csrftoken);
      reloadCart();
    } catch (err) {
      alert("Failed to clear cart");
      console.error(err);
    }
  });
}

/* ---------------------------------------------
   Confirm rental order
----------------------------------------------*/

function bindConfirmOrderForm() {
  const form = document.querySelector("form[action='/cart/confirm']");
  console.log(form)
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const orderId = form.querySelector(
      "input[name='order_id']"
    ).value;

    const csrftoken = getCookie('csrftoken');

    try {
      await request("/cart/confirm", "POST", { order_id: Number(orderId) }, csrftoken);
      alert("Rental confirmed successfully!");
      window.location.href = "/orders";
    } catch (err) {
      alert("Failed to confirm rental");
      console.error(err);
    }
  });
}
