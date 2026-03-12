(() => {
  const cfg = window.POS_CONFIG || {};

  const cart = new Map(); // product_id -> {product_id,name,price,size,color,quantity,stock}
  const productCache = new Map(); // product_id -> {data,ts}

  const els = {
    status: document.getElementById("scan-status"),
    preview: document.getElementById("preview"),
    previewError: document.getElementById("preview-error"),
    cartItems: document.getElementById("cart-items"),
    cartEmpty: document.getElementById("cart-empty"),
    totalItems: document.getElementById("cart-total-items"),
    totalAmount: document.getElementById("cart-total-amount"),
    clearCart: document.getElementById("clear-cart"),
    completeSale: document.getElementById("complete-sale"),
    message: document.getElementById("checkout-message"),
    startScannerBtn: document.getElementById("start-scanner"),
  };

  let lastScan = { code: null, time: 0 };
  let scanInFlight = false;
  let scannerStarted = false;

  function formatUzs(amount) {
    const intVal = Math.floor(Number(amount || 0));
    return intVal.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " UZS";
  }

  function beep() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = 880;
      gain.gain.value = 0.07;
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      setTimeout(() => {
        osc.stop();
        ctx.close();
      }, 80);
    } catch (_) {}
  }

  function vibrate() {
    try {
      if (navigator.vibrate) navigator.vibrate(35);
    } catch (_) {}
  }

  function showError(msg) {
    els.previewError.textContent = msg;
    els.previewError.classList.remove("hidden");
  }

  function clearError() {
    els.previewError.textContent = "";
    els.previewError.classList.add("hidden");
  }

  function renderPreview(p) {
    const low = Number(p.quantity) < Number(cfg.lowStockThreshold || 5);
    els.preview.innerHTML = `
      <div class="text-lg font-semibold leading-tight">${p.name}</div>
      <div class="text-sm text-slate-600 mt-1">${formatUzs(p.price)}</div>
      <div class="text-xs text-slate-500 mt-1">${p.product_id} · ${p.size} · ${p.color}</div>
      <div class="mt-2 flex items-center gap-2">
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${
          p.quantity === 0 ? "bg-red-100 text-red-700" : low ? "bg-amber-100 text-amber-800" : "bg-emerald-100 text-emerald-800"
        }">
          Qoldiq: ${p.quantity}
        </span>
        ${
          low && p.quantity > 0
            ? `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700">KAM QOLDI</span>`
            : ""
        }
        ${
          p.quantity === 0
            ? `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700">TUGAGAN</span>`
            : ""
        }
      </div>
    `;
  }

  function renderCart() {
    const items = Array.from(cart.values());
    els.cartItems.innerHTML = "";

    if (items.length === 0) {
      els.cartEmpty.style.display = "block";
      els.cartItems.appendChild(els.cartEmpty);
    } else {
      els.cartEmpty.style.display = "none";
      for (const item of items) {
        const low = Number(item.stock) < Number(cfg.lowStockThreshold || 5);
        const row = document.createElement("div");
        row.className = "flex items-center justify-between px-3 py-3";
        row.innerHTML = `
          <div class="min-w-0">
            <div class="font-semibold truncate">${item.name}</div>
            <div class="text-xs text-slate-500 truncate">${item.product_id} · ${item.size} · ${item.color}</div>
            <div class="text-xs mt-1 ${low ? "text-red-700 font-semibold" : "text-slate-500"}">
              ${low ? "KAM QOLDI" : ""}
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button data-id="${item.product_id}" data-action="dec"
              class="px-3 py-2 rounded-full border text-lg leading-none">-</button>
            <div class="w-8 text-center text-lg font-bold">${item.quantity}</div>
            <button data-id="${item.product_id}" data-action="inc"
              class="px-3 py-2 rounded-full border text-lg leading-none">+</button>
            <div class="w-28 text-right text-lg font-bold">${formatUzs(item.price * item.quantity)}</div>
            <button data-id="${item.product_id}" data-action="remove"
              class="text-sm text-red-600 hover:underline">O'chirish</button>
          </div>
        `;
        els.cartItems.appendChild(row);
      }
    }

    const totalItems = items.reduce((sum, it) => sum + it.quantity, 0);
    const totalAmount = items.reduce((sum, it) => sum + it.quantity * it.price, 0);
    els.totalItems.textContent = `${totalItems} ta`;
    els.totalAmount.textContent = formatUzs(totalAmount);
    els.completeSale.disabled = items.length === 0;
  }

  function cartAddProduct(p) {
    const existing = cart.get(p.product_id);
    if (!existing) {
      cart.set(p.product_id, {
        product_id: p.product_id,
        name: p.name,
        price: Number(p.price),
        size: p.size,
        color: p.color,
        quantity: 1,
        stock: Number(p.quantity),
      });
    } else {
      existing.quantity += 1;
      existing.stock = Number(p.quantity);
      cart.set(p.product_id, existing);
    }
    renderCart();
  }

  async function fetchProduct(productId) {
    const now = Date.now();
    const cached = productCache.get(productId);
    if (cached && now - cached.ts < 30_000) return cached.data;

    const url = `${cfg.apiProductBase}${encodeURIComponent(productId)}/`;
    const resp = await fetch(url, { method: "GET" });
    if (!resp.ok) throw new Error("Mahsulot topilmadi");
    const data = await resp.json();
    productCache.set(productId, { data, ts: now });
    return data;
  }

  async function handleScan(code) {
    const now = Date.now();
    if (lastScan.code === code && now - lastScan.time < 600) return;
    lastScan = { code, time: now };
    if (scanInFlight) return;
    scanInFlight = true;

    clearError();
    els.status.textContent = `O'qildi: ${code}`;

    const t0 = performance.now();
    try {
      const p = await fetchProduct(code);
      renderPreview(p);
      cartAddProduct(p);
      vibrate();
      beep();

      const dt = Math.round(performance.now() - t0);
      els.status.textContent = `Qo'shildi: ${p.name} · ${dt} ms`;
    } catch (err) {
      showError("Mahsulot topilmadi");
      els.status.textContent = "Xatolik: mahsulot topilmadi";
    } finally {
      scanInFlight = false;
    }
  }

  function attachCartHandlers() {
    els.cartItems.addEventListener("click", (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      const productId = btn.getAttribute("data-id");
      const action = btn.getAttribute("data-action");
      if (!productId || !action) return;

      const item = cart.get(productId);
      if (!item) return;

      if (action === "inc") item.quantity += 1;
      if (action === "dec") item.quantity -= 1;
      if (action === "remove" || item.quantity <= 0) cart.delete(productId);
      else cart.set(productId, item);

      renderCart();
    });

    els.clearCart.addEventListener("click", () => {
      cart.clear();
      renderCart();
      els.message.textContent = "";
    });

    els.completeSale.addEventListener("click", async () => {
      const items = Array.from(cart.values()).map((it) => ({
        product_id: it.product_id,
        quantity: it.quantity,
      }));
      if (items.length === 0) return;

      els.message.className = "mt-2 text-sm text-slate-600";
      els.message.textContent = "Savdo yakunlanmoqda...";
      els.completeSale.disabled = true;

      try {
        const resp = await fetch(cfg.apiSaleComplete, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ items }),
        });
        const data = await resp.json();
        if (!resp.ok) {
          els.message.className = "mt-2 text-sm text-red-600";
          els.message.textContent = data.error || "Xatolik yuz berdi";
          els.completeSale.disabled = false;
          return;
        }

        els.message.className = "mt-2 text-sm text-emerald-700 font-semibold";
        els.message.textContent = `Savdo #${data.sale_id} yakunlandi. Umumiy: ${formatUzs(
          data.total_amount
        )}`;
        cart.clear();
        renderCart();
      } catch (_) {
        els.message.className = "mt-2 text-sm text-red-600";
        els.message.textContent = "Tarmoq xatosi. Qayta urinib ko'ring.";
        els.completeSale.disabled = false;
      }
    });
  }

  function startScanner() {
    if (scannerStarted) return;
    scannerStarted = true;
    clearError();
    if (els.status) {
      els.status.textContent = "Kamera ishga tushirilmoqda, iltimos kuting...";
    }
    if (els.startScannerBtn) {
      els.startScannerBtn.disabled = true;
      els.startScannerBtn.textContent = "Skaner ishlayapti...";
    }

    try {
      const scanner = new Html5QrcodeScanner(
        "qr-reader",
        {
          fps: 10,
          qrbox: { width: 260, height: 260 },
        },
        /* verbose */ false
      );
      scanner.render(
        (decodedText) => {
          handleScan(decodedText);
        },
        (err) => {
          // do nothing on failure, skaner oqimini to'xtatmaymiz
        }
      );
    } catch (e) {
      showError("Kamerani ishga tushirib bo'lmadi. Brauzer sozlamasidan kameraga ruxsat bering.");
      if (els.status) {
        els.status.textContent =
          "Kamera ochilmadi. Sayt uchun kameraga ruxsat bor-yo'qligini tekshiring.";
      }
      if (els.startScannerBtn) {
        els.startScannerBtn.disabled = false;
        els.startScannerBtn.textContent = "QR skanerini qayta ishga tushirish";
      }
      scannerStarted = false;
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    attachCartHandlers();
    renderCart();
    if (els.startScannerBtn) {
      els.startScannerBtn.addEventListener("click", () => {
        startScanner();
      });
    } else {
      startScanner();
    }
  });
})();

