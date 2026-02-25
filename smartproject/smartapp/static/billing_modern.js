document.addEventListener('DOMContentLoaded', function () {
    let currentItems = [];
    const manualModeBtn = document.getElementById('btn-manual');
    const chatModeBtn = document.getElementById('btn-chat');
    const manualSection = document.getElementById('manual-mode');
    const chatSection = document.getElementById('chat-mode');

    const productInput = document.getElementById('pname');
    const productList = document.getElementById('product-list');
    const priceInput = document.getElementById('price');
    const customerInput = document.getElementById('customer-name');
    const customerPhoneInput = document.getElementById('customer-phone');
    const customerList = document.getElementById('customer-list');
    const chatInput = document.getElementById('chat-input');

    // --- Persistance Logic ---
    function saveState() {
        const state = {
            items: currentItems,
            customerName: customerInput ? customerInput.value : '',
            customerPhone: customerPhoneInput ? customerPhoneInput.value : '',
            chatText: chatInput ? chatInput.value : '',
            mode: manualModeBtn.classList.contains('active') ? 'manual' : 'chat'
        };
        localStorage.setItem('billing_workspace_state', JSON.stringify(state));
    }

    function loadState() {
        const saved = localStorage.getItem('billing_workspace_state');
        if (!saved) return;

        try {
            const state = JSON.parse(saved);
            currentItems = state.items || [];
            if (customerInput) customerInput.value = state.customerName || '';
            if (customerPhoneInput) customerPhoneInput.value = state.customerPhone || '';
            if (chatInput) chatInput.value = state.chatText || '';

            if (state.mode === 'chat' && chatModeBtn) {
                switchMode('chat');
            } else {
                switchMode('manual');
            }

            renderItemTable();
            updateSummary();
        } catch (e) {
            console.error("Error loading saved state:", e);
        }
    }

    function clearState() {
        localStorage.removeItem('billing_workspace_state');
    }

    function switchMode(mode) {
        if (mode === 'manual') {
            manualModeBtn.classList.add('active');
            chatModeBtn.classList.remove('active');
            manualSection.style.display = 'block';
            chatSection.style.display = 'none';
        } else {
            chatModeBtn.classList.add('active');
            manualModeBtn.classList.remove('active');
            chatSection.style.display = 'block';
            manualSection.style.display = 'none';
        }
    }

    // --- Event Listeners with Auto-Save ---

    // Mode Switching
    if (manualModeBtn) {
        manualModeBtn.addEventListener('click', () => {
            switchMode('manual');
            currentItems = []; // Only reset items
            renderItemTable();
            updateSummary();
            saveState();
        });
    }

    if (chatModeBtn) {
        chatModeBtn.addEventListener('click', () => {
            switchMode('chat');
            currentItems = []; // Only reset items
            renderItemTable();
            updateSummary();
            saveState();
        });
    }

    if (customerInput) {
        customerInput.addEventListener('input', saveState);

        // Auto-fill phone on selection
        customerInput.addEventListener('input', function () {
            const val = this.value;
            const options = customerList.options;
            for (let i = 0; i < options.length; i++) {
                if (options[i].value === val) {
                    const phone = options[i].getAttribute('data-phone');
                    if (phone && customerPhoneInput) {
                        customerPhoneInput.value = phone;
                        saveState();
                    }
                    break;
                }
            }
        });
    }

    if (customerPhoneInput) {
        customerPhoneInput.addEventListener('input', saveState);
    }

    // Auto-fill Price on Product Selection
    if (productInput) {
        productInput.addEventListener('input', function () {
            const val = this.value;
            const options = productList.options;
            for (let i = 0; i < options.length; i++) {
                if (options[i].value === val) {
                    const price = options[i].getAttribute('data-price');
                    if (price) {
                        priceInput.value = price;
                    }
                    break;
                }
            }
        });
    }

    window.addItem = function () {
        const qtyInput = document.getElementById('qty');
        const name = productInput.value;
        const qty = parseInt(qtyInput.value);
        const price = parseFloat(priceInput.value);

        if (!name || isNaN(qty) || isNaN(price)) {
            alert('Please fill product name, quantity and price.');
            return;
        }

        // Price Validation
        let correctPrice = null;
        for (let i = 0; i < productList.options.length; i++) {
            if (productList.options[i].value === name) {
                correctPrice = parseFloat(productList.options[i].getAttribute('data-price'));
                break;
            }
        }

        if (correctPrice !== null && price !== correctPrice) {
            alert(`Error: The price for "${name}" must be ₹${correctPrice.toFixed(2)}. You entered ₹${price.toFixed(2)}.`);
            return;
        }

        currentItems.push({ name, qty, price, total: qty * price });
        productInput.value = '';
        if (qtyInput) qtyInput.value = '';
        if (priceInput) priceInput.value = '';
        renderItemTable();
        updateSummary();
        saveState();
        productInput.focus();
    };

    function renderItemTable() {
        const tbody = document.getElementById('item-tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        currentItems.forEach((item, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.name}</td>
                <td>${item.qty}</td>
                <td>₹${item.price.toFixed(2)}</td>
                <td>₹${item.total.toFixed(2)}</td>
                <td><button class="btn-delete" onclick="removeItem(${index})"><i class="fas fa-trash"></i></button></td>
            `;
            tbody.appendChild(tr);
        });
    }

    window.removeItem = function (index) {
        currentItems.splice(index, 1);
        renderItemTable();
        updateSummary();
        saveState();
    };

    function updateSummary() {
        let subtotal = 0;
        currentItems.forEach(i => subtotal += i.total);
        const tax = subtotal * 0.05;
        const grandTotal = subtotal + tax;

        const subElem = document.getElementById('display-subtotal');
        const taxElem = document.getElementById('display-tax');
        const totalElem = document.getElementById('display-total');

        if (subElem) subElem.innerText = subtotal.toFixed(2);
        if (taxElem) taxElem.innerText = tax.toFixed(2);
        if (totalElem) totalElem.innerText = grandTotal.toFixed(2);
    }

    function resetOrder() {
        currentItems = [];
        renderItemTable();
        updateSummary();
        if (customerInput) customerInput.value = '';
        if (customerPhoneInput) customerPhoneInput.value = '';
        if (chatInput) chatInput.value = '';
        clearState();
    }

    if (chatInput) {
        chatInput.addEventListener('input', function () {
            const text = this.value;
            const lines = text.split('\n');
            currentItems = [];
            lines.forEach(line => {
                const parts = line.trim().split(/\s+/);
                if (parts.length >= 3) {
                    const price = parseFloat(parts[parts.length - 1]);
                    const qty = parseInt(parts[parts.length - 2]);
                    const name = parts.slice(0, parts.length - 2).join(' ');
                    if (!isNaN(price) && !isNaN(qty)) {
                        let correctPrice = null;
                        for (let i = 0; i < productList.options.length; i++) {
                            if (productList.options[i].value === name) {
                                correctPrice = parseFloat(productList.options[i].getAttribute('data-price'));
                                break;
                            }
                        }
                        if (correctPrice !== null && price !== correctPrice) return;
                        currentItems.push({ name, qty, price, total: qty * price });
                    }
                }
            });
            renderItemTable();
            updateSummary();
            saveState();
        });
    }

    window.generateBill = function () {
        const customerName = customerInput ? customerInput.value : '';
        const phone = customerPhoneInput ? customerPhoneInput.value : '';

        if (!customerName || currentItems.length === 0) {
            alert('Customer name and at least one item are required.');
            return;
        }

        // Final Price Sanity Check
        for (let item of currentItems) {
            let correctPrice = null;
            for (let i = 0; i < productList.options.length; i++) {
                if (productList.options[i].value === item.name) {
                    correctPrice = parseFloat(productList.options[i].getAttribute('data-price'));
                    break;
                }
            }
            if (correctPrice !== null && item.price !== correctPrice) {
                alert(`Error: Price for ${item.name} is wrong.`);
                return;
            }
        }

        const payload = {
            customer: customerName,
            phone: phone,
            items: currentItems
        };

        fetch('/smart/save_bill/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Success: Invoice generated and inventory updated!');
                    clearState();
                    location.reload();
                } else {
                    alert('Server Error: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(err => {
                console.error("Fetch error:", err);
                alert('Network Error: Could not connect to the server.');
            });
    };

    window.sendToWhatsApp = function () {
        const customerName = customerInput ? customerInput.value : '';
        const phone = customerPhoneInput ? customerPhoneInput.value : '';

        if (!customerName || !phone) {
            alert('Please enter customer name and phone number.');
            return;
        }

        if (currentItems.length === 0) {
            alert('No items in the order.');
            return;
        }

        const subtotal = document.getElementById('display-subtotal').innerText;
        const tax = document.getElementById('display-tax').innerText;
        const total = document.getElementById('display-total').innerText;

        let message = `*--- SmartStock Invoice ---*\n`;
        message += `*Customer:* ${customerName}\n`;
        if (phone) message += `*Phone:* ${phone}\n\n`;
        message += `*Items:*\n`;

        currentItems.forEach(item => {
            message += `- ${item.name}: ${item.qty} x ₹${item.price.toFixed(2)} = *₹${item.total.toFixed(2)}*\n`;
        });

        message += `\n*Subtotal:* ₹${subtotal}\n`;
        message += `*GST (5%):* ₹${tax}\n`;
        message += `*Grand Total: ₹${total}*\n\n`;
        message += `_Thank you for shopping with us!_`;

        const encodedMessage = encodeURIComponent(message);
        const whatsappURL = `https://wa.me/${phone}?text=${encodedMessage}`;
        window.open(whatsappURL, '_blank');
    };

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

    // INITIAL LOAD
    loadState();
});
