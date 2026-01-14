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

function toISOStringFromLocal(datetimeLocalValue) {
  // datetime-local returns "YYYY-MM-DDTHH:MM" (no timezone)
  // Convert to JS Date (assumes local timezone) and return ISO string (UTC)
  const dt = new Date(datetimeLocalValue);
  if (isNaN(dt)) return null;
  return dt.toISOString();
}

async function checkAvailability(inventoryId, startIso, endIso) {
  const url = new URL('/inventory/availability', window.location.origin);
  url.searchParams.set('inventory_id', inventoryId);
  url.searchParams.set('start_at', startIso);
  url.searchParams.set('end_at', endIso);

  const res = await fetch(url.toString(), {
    method: 'GET',
    credentials: 'include',
    headers: { 'Accept': 'application/json' },
  });

  if (!res.ok) throw new Error('Availability check failed');
  const data = await res.json()
  console.log(data)
  return data; // { available: number }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.add-form').forEach(form => {
    const idx = form.dataset.rowIndex;

    const btn = form.querySelector(`.check-availability`);
    const qtyInput = form.querySelector('input[name="quantity"]');
    const startInput = form.querySelector('input[name="start_at"]');
    const endInput = form.querySelector('input[name="end_at"]');
    const msgEl = document.getElementById(`avail_msg_${idx}`);

    btn.addEventListener('click', async () => {
      // front-end validation
      msgEl.textContent = '';
      const qty = parseInt(qtyInput.value, 10);
      const startVal = startInput.value;
      const endVal = endInput.value;

      if (!startVal || !endVal) {
        msgEl.textContent = 'Please pick both start and end times.';
        msgEl.style.color = 'crimson';
        return;
      }

      const startIso = toISOStringFromLocal(startVal);
      const endIso = toISOStringFromLocal(endVal);
      if (!startIso || !endIso) {
        msgEl.textContent = 'Invalid date/time.';
        msgEl.style.color = 'crimson';
        return;
      }

      if (new Date(startIso) >= new Date(endIso)) {
        msgEl.textContent = 'End must be after start.';
        msgEl.style.color = 'crimson';
        return;
      }

      // inventory id comes from hidden input 'warehouse_id' or you may have inventory_id
      const inventoryId = form.querySelector('input[name="inventory_id"]').value;
      try {
        btn.disabled = true;
        btn.textContent = 'Checking...';

        const data = await checkAvailability(inventoryId, startIso, endIso);
        const available = data?.available ?? 0;
        console.log(available)

        if (available >= qty) {
          msgEl.textContent = `Available (${available}). Adding to cart...`;
          msgEl.style.color = 'green';

          // Prepare to submit: ensure backend sees ISO timestamps.
          // Create hidden inputs with ISO strings (server expects start_at/end_at)
          let hStart = form.querySelector('input[name="start_at_iso"]');
          if (!hStart) {
            hStart = document.createElement('input');
            hStart.type = 'hidden';
            hStart.name = 'start_at';
            form.appendChild(hStart);
          }
          let hEnd = form.querySelector('input[name="end_at_iso"]');
          if (!hEnd) {
            hEnd = document.createElement('input');
            hEnd.type = 'hidden';
            hEnd.name = 'end_at';
            form.appendChild(hEnd);
          }
          hStart.value = startIso;
          hEnd.value = endIso;


          // Option B (uncomment to do via fetch/JSON instead):
          const payload = {
            inventory_id:inventoryId,
            quantity: qty,
            start_at: startIso,
            end_at: endIso,
          };
          const csrftoken = getCookie('csrftoken'); // adapt name to your CSRF cookie
          const postRes = await fetch('http://localhost:8000/cart/items', {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              'x-csrftoken': csrftoken || '',
            },
            body: JSON.stringify(payload),
          });
          // handle postRes.ok etc.
        } else {
          msgEl.textContent = `Only ${available} available in that window.`;
          msgEl.style.color = 'crimson';
        }
      } catch (err) {
        console.error(err);
        msgEl.textContent = 'Error checking availability.';
        msgEl.style.color = 'crimson';
      } finally {
        btn.disabled = false;
        btn.textContent = 'Check & Add to cart';
      }
    });
  }); // forEach form
});

