// Scripts pour ManiocAgri - Version Premium avec Toast Notifications

const API_BASE_URL = 'https://maniocagri.onrender.com/api/v1';
//const API_BASE_URL = 'http://localhost:8000/api/v1';

// ==========================================
// Globals
// ==========================================
let allUsers = [];
let currentProducts = [];
let currentPendingOrders = [];
let cart = {};


// ==========================================
// Toast Notification System
// ==========================================

function showToast(message, type = 'success', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) {
        // Create container if it doesn't exist
        const newContainer = document.createElement('div');
        newContainer.id = 'toastContainer';
        newContainer.className = 'toast-container';
        document.body.appendChild(newContainer);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <div class="d-flex align-items-center gap-3">
            <span class="fw-bold" style="font-size: 1.2rem;">${icons[type] || icons.info}</span>
            <span>${message}</span>
        </div>
    `;

    const toastContainer = document.getElementById('toastContainer');
    toastContainer.appendChild(toast);

    // Auto remove after duration
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ==========================================
// API Helper with Enhanced Error Handling
// ==========================================

async function apiCall(endpoint, method = 'GET', body = null, useToken = true) {
    const headers = {
        'Content-Type': 'application/json'
    };

    if (useToken) {
        const token = sessionStorage.getItem('token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }

    const options = {
        method,
        headers
    };

    if (body) {
        if (body instanceof FormData) {
            delete headers['Content-Type'];
            options.body = body;
        } else if (body instanceof URLSearchParams) {
            headers['Content-Type'] = 'application/x-www-form-urlencoded';
            options.body = body;
        } else {
            options.body = JSON.stringify(body);
        }
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Une erreur est survenue');
    }

    return response.json();
}

// ==========================================
// Button Loading State
// ==========================================

function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.classList.add('loading');
        button.disabled = true;
    } else {
        button.classList.remove('loading');
        button.disabled = false;
    }
}

// ==========================================
// Authentification et Inscription
// ==========================================

// ==========================================
// Custom Confirmation Modal
// ==========================================

function showConfirmModal(title, message, confirmText = 'Confirmer', variant = 'primary') {
    return new Promise((resolve) => {
        // Remove existing modal if any
        const existingModal = document.getElementById('customConfirmModal');
        if (existingModal) existingModal.remove();

        const modalHtml = `
            <div class="modal fade" id="customConfirmModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content border-0 shadow-lg">
                        <div class="modal-header border-bottom-0">
                            <h5 class="modal-title fw-bold text-${variant}">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body py-4">
                            <div class="d-flex align-items-center">
                                <div class="flex-shrink-0 text-${variant} me-3">
                                    <i class="fas fa-exclamation-circle fa-2x"></i>
                                </div>
                                <div>
                                    <p class="mb-0 fs-5">${message}</p>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer border-top-0 bg-light rounded-bottom">
                            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Annuler</button>
                            <button type="button" class="btn btn-${variant} px-4" id="confirmModalBtn">${confirmText}</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        const modalEl = document.getElementById('customConfirmModal');
        const modal = new bootstrap.Modal(modalEl);
        const confirmBtn = document.getElementById('confirmModalBtn');

        modal.show();

        const handleConfirm = () => {
            resolve(true);
            modal.hide();
        };

        const handleDismiss = () => {
            resolve(false);
        };

        confirmBtn.addEventListener('click', handleConfirm);
        modalEl.addEventListener('hidden.bs.modal', function () {
            resolve(false); // Default to false if dismissed without clicking confirm
            modalEl.remove();
        }, { once: true });
    });
}

function showSuccessModal(title, message) {
    return new Promise((resolve) => {
        const existingModal = document.getElementById('customSuccessModal');
        if (existingModal) existingModal.remove();

        const modalHtml = `
            <div class="modal fade" id="customSuccessModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content border-0 shadow-lg">
                        <div class="modal-body p-5 text-center">
                            <div class="mb-4 text-success">
                                <i class="fas fa-check-circle fa-4x"></i>
                            </div>
                            <h4 class="fw-bold mb-3">${title}</h4>
                            <p class="text-muted mb-4">${message}</p>
                            <button type="button" class="btn btn-success px-5 py-2 rounded-pill" data-bs-dismiss="modal" id="successVideoBtn">Parfait !</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modalEl = document.getElementById('customSuccessModal');
        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        modalEl.addEventListener('hidden.bs.modal', function () {
            resolve(true);
            modalEl.remove();
        }, { once: true });
    });
}

// ==========================================
// Authentification et Inscription
// ==========================================

// ==========================================
// Google Authentication
// ==========================================

async function handleGoogleCallback(response) {
    const credential = response.credential;
    if (!credential) {
        showToast('Erreur lors de la connexion via Google.', 'error');
        return;
    }

    try {
        // Obtenir le rôle demandé (utile pour les nouveaux inscrits)
        const requestedRoleEl = document.getElementById('requestedRole');
        const role = requestedRoleEl ? requestedRoleEl.value : 'client';

        // Envoyer le token au backend avec le rôle souhaité
        const data = await apiCall('/auth/google', 'POST', { token: credential, requested_role: role }, false);


        sessionStorage.setItem('token', data.access_token);
        sessionStorage.setItem('userRole', data.user.role);
        sessionStorage.setItem('username', data.user.username);

        // Mapping rôle → page dashboard
        const roleDashboards = {
            'admin': 'admin.html',
            'client': 'client.html',
            'producteur': 'producteur.html',
            'livreur': 'livreur.html',
            'gestionnaire': 'gestionnaire.html',
            'agent': 'agent_terrain.html',
        };
        const dashboard = roleDashboards[data.user.role] || 'client.html';

        showToast('Connexion réussie! Redirection...', 'success');
        setTimeout(() => {
            window.location.href = dashboard;
        }, 500);

    } catch (err) {
        console.error('Google Auth Error:', err);

        // En cas d'erreur API, afficher le message
        const errorMessage = document.getElementById('errorMessage');
        let displayMsg = err.message || "Erreur d'authentification.";

        // Personnalisation selon le message du backend
        if (displayMsg.includes("approbation")) {
            displayMsg = "⏳ Votre compte est en attente de validation par un administrateur.";
        } else if (displayMsg.includes("inactif")) {
            displayMsg = "🚫 Votre compte est inactif. Veuillez contacter le support.";
        }

        if (errorMessage) {
            errorMessage.textContent = displayMsg;
            errorMessage.style.display = 'block';
            errorMessage.classList.remove('d-none');
        }
        showToast(displayMsg, 'error');
    }
}


// Order statistics: consolidated implementation exists further below (keeps chart + counters)

// Helper for animation (optional but nice)
function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    if (!obj) return;
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerHTML = end;
        }
    };
    window.requestAnimationFrame(step);
}

function getImageUrl(url) {
    if (!url) return '/images/products/manioc2.jpg';
    // If it's a full URL (Supabase or other hosted), return it directly
    if (url.startsWith('http')) return url;
    // Otherwise it's a local path, add leading slash if missing
    return url.startsWith('/') ? url : '/' + url;
}

// ===============================
// Global Functions & Utils
// ==========================================
// Gestion Admin - Utilisateurs
// ==========================================



async function loadPendingRegistrations() {
    const pendingDiv = document.getElementById('pendingRegistrations');
    if (!pendingDiv) return;

    try {
        const users = await apiCall('/users/', 'GET');
        allUsers = users;
        const unapproved = users.filter(u => !u.is_approved);

        // Update badges
        const pendingBadge = document.getElementById('pendingBadge');
        const pendingCount = document.getElementById('pendingCount');
        const usersBadge = document.getElementById('usersBadge');
        const totalUsers = document.getElementById('totalUsers');

        if (pendingBadge) pendingBadge.textContent = unapproved.length;
        if (pendingCount) pendingCount.textContent = unapproved.length;
        if (usersBadge) usersBadge.textContent = users.filter(u => u.is_approved).length;
        if (totalUsers) totalUsers.textContent = users.filter(u => u.is_approved).length;

        if (unapproved.length === 0) {
            pendingDiv.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-check-circle fa-2x mb-3 text-success"></i>
                    <p class="mb-0">Aucune inscription en attente</p>
                </div>`;
            return;
        }

        pendingDiv.innerHTML = unapproved.map(reg => `
            <div class="d-flex justify-content-between align-items-center mb-3 p-3 bg-white rounded-3 shadow-sm border-start border-4 border-warning">
                <div>
                    <strong class="text-dark">${reg.username}</strong>
                    <span class="badge bg-secondary ms-2">${reg.role}</span>
                    <br>
                    <small class="text-muted">${reg.email}</small>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-success btn-sm px-3" onclick="approveUser(${reg.id})">
                        <i class="fas fa-check me-1"></i>Approuver
                    </button>
                    <button class="btn btn-outline-danger btn-sm px-3" onclick="rejectUser(${reg.id})">
                        <i class="fas fa-times me-1"></i>Refuser
                    </button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error("Erreur chargement utilisateurs:", err);
        pendingDiv.innerHTML = `
            <div class="text-center text-danger py-4">
                <i class="fas fa-exclamation-circle fa-2x mb-3"></i>
                <p class="mb-0">Erreur de chargement</p>
            </div>`;
    }
}

async function loadUsers() {
    const usersList = document.getElementById('usersList');
    if (!usersList) return;

    try {
        const users = await apiCall('/users/', 'GET');
        allUsers = users;
        const approved = users.filter(u => u.is_approved);
        const pending = users.filter(u => !u.is_approved);

        // Update Dashboard Stats
        const totalUsersEl = document.getElementById('totalUsers');
        if (totalUsersEl) totalUsersEl.textContent = users.length;

        const pendingCountEl = document.getElementById('pendingCount');
        if (pendingCountEl) pendingCountEl.textContent = pending.length;

        const usersBadge = document.getElementById('usersBadge');
        if (usersBadge) usersBadge.textContent = approved.length;

        const pendingBadge = document.getElementById('pendingBadge');
        if (pendingBadge) pendingBadge.textContent = pending.length;

        const pendingBadgeSidebar = document.getElementById('pendingBadgeSidebar');
        if (pendingBadgeSidebar) pendingBadgeSidebar.textContent = pending.length > 0 ? pending.length : '';

        renderUsers(approved);
    } catch (err) {
        console.error("Erreur chargement utilisateurs:", err);
    }
}

function renderUsers(users) {
    const usersList = document.getElementById('usersList');
    if (!usersList) return;

    if (users.length === 0) {
        usersList.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-users-slash fa-2x mb-3 text-secondary"></i>
                <p class="mb-0">Aucun utilisateur trouvé</p>
            </div>`;
        return;
    }

    usersList.innerHTML = users.map(user => `
        <div class="user-item d-flex align-items-center justify-content-between p-3 border-bottom hover-bg-light transition">
            <div class="d-flex align-items-center">
                <div class="bg-success bg-opacity-10 text-success rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                    <i class="fas fa-user"></i>
                </div>
                <div>
                    <h6 class="mb-0 fw-bold">${user.username}</h6>
                    <small class="text-muted">${user.email} • <span class="badge bg-light text-dark border">${user.role}</span></small>
                </div>
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-outline-danger btn-sm rounded-pill px-3" onclick="deleteUser(${user.id})">
                    <i class="fas fa-trash-alt me-1"></i>Supprimer
                </button>
            </div>
        </div>
    `).join('');
}
function filterUsers() {
    const query = document.getElementById('userSearch').value.toLowerCase();
    const approved = allUsers.filter(u => u.is_approved);
    const filtered = approved.filter(u =>
        u.username.toLowerCase().includes(query) ||
        u.email.toLowerCase().includes(query) ||
        u.role.toLowerCase().includes(query)
    );
    renderUsers(filtered);
}

async function approveUser(userId) {
    try {
        await apiCall(`/users/${userId}/approve`, 'PATCH');
        showToast('Utilisateur approuvé avec succès!', 'success');
        loadPendingRegistrations();
        loadUsers();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

window.rejectUser = async function (userId) {
    if (!await showConfirmModal('Refuser Inscription', 'Êtes-vous sûr de vouloir refuser cette inscription ?', 'Refuser', 'danger')) return;
    try {
        await apiCall(`/users/${userId}`, 'DELETE');
        showToast('Inscription refusée', 'warning');
        loadPendingRegistrations();
    } catch (err) {
        showToast(err.message, 'error');
    }
};

window.deleteUser = async function (userId) {
    if (!await showConfirmModal('Supprimer Utilisateur', 'Êtes-vous sûr de vouloir supprimer cet utilisateur ?', 'Supprimer', 'danger')) return;
    try {
        await apiCall(`/users/${userId}`, 'DELETE');
        showToast('Utilisateur supprimé', 'warning');
        loadUsers();
        loadPendingRegistrations();
    } catch (err) {
        showToast(err.message, 'error');
    }
};

// ==========================================
// Init Add User Form
// Removed initAddUserForm as per user request


// ==========================================
// Produits (CRUD Admin & Producteur)
// ==========================================

function initProductForm() {
    const productForm = document.getElementById('productForm');
    if (!productForm) return;

    productForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const productIdEl = document.getElementById('productId');
        const id = productIdEl ? productIdEl.value : null;

        const productNameEl = document.getElementById('productName');
        const name = productNameEl ? productNameEl.value : '';

        const priceEl = document.getElementById('productPrice');
        const price = priceEl ? priceEl.value : '0';

        const stockEl = document.getElementById('productStock');
        const stock = stockEl ? stockEl.value : '0';

        const descriptionEl = document.getElementById('productDescription');
        const description = descriptionEl ? descriptionEl.value : '';

        const imageUrlInput = document.getElementById('productImageUrl');
        const imageUrl = imageUrlInput ? imageUrlInput.value : '';

        const submitBtn = document.getElementById('saveProductBtn');
        const nameInput = document.getElementById('productName');
        const nameError = document.getElementById('productNameError');

        // Clear previous errors
        if (nameInput) nameInput.classList.remove('is-invalid');
        if (nameError) nameError.textContent = '';

        const data = {
            name: name,
            price: Math.round(parseFloat(price) || 0),
            stock_quantity: Math.round(parseFloat(stock) || 0),
            description: description,
            image_url: imageUrl
        };

        setButtonLoading(submitBtn, true);

        try {
            if (id) {
                await apiCall(`/products/${id}`, 'PATCH', data);
                // Handle Image Upload if file selected
                const imageFile = document.getElementById('productImage').files[0];
                if (imageFile) {
                    await uploadProductImage(id, imageFile);
                }
                showToast('Produit mis à jour avec succès!', 'success');
            } else {
                const newProduct = await apiCall('/products/', 'POST', data);
                // Handle Image Upload if file selected
                const imageFile = document.getElementById('productImage').files[0];
                if (imageFile) {
                    await uploadProductImage(newProduct.id, imageFile);
                }
                showToast('Produit ajouté avec succès!', 'success');
            }

            productForm.reset();
            document.getElementById('productId').value = '';
            // Reset file input label or preview if any (simple reset clears input)

            const title = document.getElementById('productFormTitle');
            if (title) title.innerHTML = '<i class="fas fa-plus-circle me-2 text-success"></i>Ajouter un produit';

            const cancelBtn = document.getElementById('cancelEditBtn');
            if (cancelBtn) cancelBtn.classList.add('d-none');

            loadProducts();
        } catch (err) {
            // Check for duplicate name error
            if (err.message.includes('existe déjà') || err.message.includes('duplicate')) {
                nameInput.classList.add('is-invalid');
                if (nameError) nameError.textContent = 'Un produit avec ce nom existe déjà';
                showToast('Un produit avec ce nom existe déjà!', 'error');
            } else {
                showToast(err.message, 'error');
            }
        } finally {
            setButtonLoading(submitBtn, false);
        }
    });
}

async function uploadProductImage(productId, file) {
    const formData = new FormData();
    formData.append('file', file);
    await apiCall(`/products/${productId}/image`, 'POST', formData);
}

window.editProduct = function (id) {
    const product = currentProducts.find(p => p.id === id);
    if (!product) return;

    const productIdEl = document.getElementById('productId');
    if (productIdEl) productIdEl.value = product.id;

    const productNameEl = document.getElementById('productName');
    if (productNameEl) productNameEl.value = product.name;

    const productPriceEl = document.getElementById('productPrice');
    if (productPriceEl) productPriceEl.value = product.price;

    const productStockEl = document.getElementById('productStock');
    if (productStockEl) productStockEl.value = product.stock_quantity;

    const productDescriptionEl = document.getElementById('productDescription');
    if (productDescriptionEl) productDescriptionEl.value = product.description || '';

    const imageUrlInput = document.getElementById('productImageUrl');
    if (imageUrlInput) {
        imageUrlInput.value = product.image_url || '';
    }
    // Note: Can't set file input value programmatically for security reasons

    const title = document.getElementById('productFormTitle');
    if (title) title.innerHTML = `<i class="fas fa-edit me-2 text-warning"></i>Modifier: ${product.name}`;

    const cancelBtn = document.getElementById('cancelEditBtn');
    if (cancelBtn) cancelBtn.classList.remove('d-none');

    // Clear any previous error state
    document.getElementById('productName').classList.remove('is-invalid');

    window.scrollTo({ top: 0, behavior: 'smooth' });
    showToast('Mode édition activé', 'info', 2000);
};

window.cancelEdit = function () {
    document.getElementById('productForm').reset();
    const productIdEl = document.getElementById('productId');
    if (productIdEl) productIdEl.value = '';

    const title = document.getElementById('productFormTitle');
    if (title) title.innerHTML = '<i class="fas fa-plus-circle me-2 text-success"></i>Ajouter un produit';

    const cancelBtn = document.getElementById('cancelEditBtn');
    if (cancelBtn) cancelBtn.classList.add('d-none');

    const productNameEl = document.getElementById('productName');
    if (productNameEl) productNameEl.classList.remove('is-invalid');
};

window.deleteProduct = async function (id) {
    if (!await showConfirmModal('Supprimer Produit', 'Êtes-vous sûr de vouloir supprimer ce produit ?', 'Supprimer', 'danger')) return;
    try {
        await apiCall(`/products/${id}`, 'DELETE');
        showToast('Produit supprimé avec succès!', 'warning');
        loadProducts();
    } catch (err) {
        showToast(err.message, 'error');
    }
};


async function loadProducts() {
    const productsList = document.getElementById('productsList'); // Dashboard producteur/admin
    const catalogueContainer = document.getElementById('products-container'); // Page catalogue

    if (!productsList && !catalogueContainer) return;

    try {
        const products = await apiCall('/products/', 'GET');
        currentProducts = products;

        // Update stats
        const totalProducts = document.getElementById('totalProducts');
        const productsBadge = document.getElementById('productsBadge');
        const totalStock = document.getElementById('totalStock');

        if (totalProducts) totalProducts.textContent = products.length;
        if (productsBadge) productsBadge.textContent = `${products.length} produit${products.length > 1 ? 's' : ''}`;

        const lowStockProducts = products.filter(p => (p.stock_quantity || 0) < 10);
        const lowStockAlert = document.getElementById('lowStockAlert');
        if (lowStockAlert) lowStockAlert.textContent = lowStockProducts.length;

        if (totalStock) {
            const stock = products.reduce((sum, p) => sum + (p.stock_quantity || 0), 0);
            totalStock.textContent = stock.toLocaleString();
        }

        renderProducts(products);
        if (catalogueContainer) renderCatalogue(products);
    } catch (err) {
        console.error("Erreur chargement produits:", err);
    }
}

function renderProducts(products) {
    const productsList = document.getElementById('productsList');
    if (!productsList) return;

    if (products.length === 0) {
        productsList.innerHTML = `
            <div class="col-12 text-center text-muted py-5">
                <i class="fas fa-box-open fa-3x mb-3 text-secondary"></i>
                <p class="mb-0">Aucun produit trouvé</p>
                <small>Essayez un autre mot-clé ou ajoutez un produit.</small>
            </div>`;
        return;
    }

    productsList.innerHTML = products.map(product => `
        <div class="col-md-4 col-lg-3 mb-4">
            <div class="admin-product-card h-100 shadow-sm border-0 rounded-4 overflow-hidden bg-white hover-shadow transition">
                <div class="position-relative">
                    <img src="${getImageUrl(product.image_url)}" 
                        class="card-img-top" alt="${product.name}" style="height: 180px; object-fit: cover; border-bottom: 1px solid #f0f0f0;">
                    <span class="position-absolute top-0 end-0 m-2 badge bg-success shadow-sm">${product.price.toLocaleString()} FCFA/kg</span>
                </div>
                <div class="p-3">
                    <h6 class="mb-1 fw-bold text-dark">${product.name}</h6>
                    <p class="text-muted small mb-3 text-truncate-2" style="height: 40px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                        ${product.description || 'Pas de description'}
                    </p>
                    <div class="d-flex justify-content-between align-items-center small text-muted mb-3">
                        <span><i class="fas fa-warehouse me-1"></i>Stock: <strong class="${product.stock_quantity < 10 ? 'text-danger fw-bold' : ''}">${product.stock_quantity || 0}kg</strong></span>
                        ${product.stock_quantity < 10 ? '<span class="badge bg-danger-subtle text-danger border-danger border small">Bas</span>' : ''}
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-warning btn-sm flex-fill rounded-3 shadow-sm" onclick="editProduct(${product.id})">
                            <i class="fas fa-edit me-1"></i>Éditer
                        </button>
                        <button class="btn btn-outline-danger btn-sm rounded-pill" onclick="deleteProduct(${product.id})">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function renderCatalogue(products) {
    const catalogueContainer = document.getElementById('products-container');
    if (!catalogueContainer) return;

    // Header check
    const h2 = catalogueContainer.querySelector('h2');
    catalogueContainer.innerHTML = '';
    if (h2) catalogueContainer.appendChild(h2);

    const row = document.createElement('div');
    row.className = 'row g-4';
    products.forEach(product => {
        row.innerHTML += `
            <div class="col-6 col-md-4 col-lg-3">
                <div class="card h-100 product-card border-0 shadow-sm overflow-hidden" onclick="window.location.href='produit-details.html?id=${product.id}'">
                    <div class="position-relative">
                        <img src="${getImageUrl(product.image_url)}" 
                             class="card-img-top" alt="${product.name}" style="height: 200px; object-fit: cover;">
                        <span class="position-absolute top-0 end-0 m-2 badge bg-success shadow-sm">${product.price.toLocaleString()} FCFA/kg</span>
                    </div>
                    <div class="card-body p-3">
                        <h6 class="card-title fw-bold mb-1">${product.name}</h6>
                        <small class="text-muted d-block mb-3 text-truncate">${product.description || 'Produit local de qualité 🌿'}</small>
                        <div class="d-flex gap-2 mt-auto">
                            <button class="btn btn-success btn-sm flex-fill rounded-pill shadow-sm" onclick="event.stopPropagation(); addToCart(${product.id})">
                                <i class="fas fa-shopping-basket me-1"></i>Acheter
                            </button>
                            <button class="btn btn-outline-success btn-sm rounded-circle shadow-sm" style="width: 32px; height: 32px; padding: 0;" onclick="event.stopPropagation(); whatsappOrder('${product.name}', ${product.price})" title="Commander via WhatsApp">
                                <i class="fab fa-whatsapp"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>`;
    });
    catalogueContainer.appendChild(row);
}

function filterProducts() {
    const query = document.getElementById('productSearch').value.toLowerCase();
    const filtered = currentProducts.filter(p =>
        p.name.toLowerCase().includes(query) ||
        (p.description && p.description.toLowerCase().includes(query))
    );
    renderProducts(filtered);
}

function showAddProductForm() {
    const form = document.getElementById('productForm');
    if (!form) return;
    form.reset();
    document.getElementById('productId').value = '';
    const imageUrlInput = document.getElementById('productImageUrl');
    if (imageUrlInput) imageUrlInput.value = '';
    document.getElementById('productFormTitle').textContent = 'Nouveau Produit';

    const title = document.getElementById('productFormTitle');
    if (title) title.innerHTML = '<i class="fas fa-plus-circle me-2 text-success"></i>Nouveau Produit';

    const cancelBtn = document.getElementById('cancelEditBtn');
    if (cancelBtn) cancelBtn.classList.add('d-none');
}

function addToCart(productId) {
    cart[productId] = (cart[productId] || 0) + 1;
    updateOrderSummary();
    showToast('Produit ajouté au panier !', 'success', 2000);
}

async function loadProductDetails() {
    const container = document.getElementById('product-details-container');
    if (!container) return;

    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');

    if (!productId) {
        container.innerHTML = '<div class="col-12 text-center py-5"><h3>Produit non trouvé</h3><a href="catalogue.html" class="btn btn-success mt-3">Retour au catalogue</a></div>';
        return;
    }

    try {
        const product = await apiCall(`/products/${productId}`, 'GET');

        container.innerHTML = `
            <div class="col-lg-6 mb-4 mb-lg-0">
                <div class="product-image-wrapper rounded-4 overflow-hidden shadow-sm">
                    <img src="${getImageUrl(product.image_url)}" 
                         class="img-fluid w-100" alt="${product.name}" style="min-height: 400px; object-fit: cover;">
                </div>
            </div>
            <div class="col-lg-6">
                <div class="ps-lg-4">
                    <span class="badge bg-success-subtle text-success border border-success mb-3 px-3 py-2 rounded-pill">Produit Local</span>
                    <h1 class="display-5 fw-bold text-dark mb-3">${product.name}</h1>
                    <h3 class="text-success fw-bold mb-4">${product.price.toLocaleString()} FCFA <small class="text-muted fs-6">/ kg</small></h3>
                    
                    <div class="mb-4">
                        <h5 class="fw-bold mb-2">Description</h5>
                        <p class="text-muted lead mb-0">${product.description || 'Description non disponible pour ce produit.'}</p>
                    </div>

                    <div class="mb-4">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fas fa-warehouse text-success me-2"></i>
                            <span class="fw-bold">Stock disponible:</span>
                            <span class="ms-2 ${product.stock_quantity < 10 ? 'text-danger' : 'text-success'}">${product.stock_quantity} kg</span>
                        </div>
                    </div>

                    <div class="d-grid gap-2 d-md-flex mt-5">
                        <button class="btn btn-success btn-lg px-5 py-3 rounded-pill shadow-sm flex-fill" onclick="addToCart(${product.id})">
                            <i class="fas fa-shopping-basket me-2"></i>AJOUTER AU PANIER
                        </button>
                        <button class="btn btn-outline-success btn-lg px-4 py-3 rounded-pill shadow-sm" onclick="whatsappOrder('${product.name}', ${product.price})">
                            <i class="fab fa-whatsapp me-2"></i>COMMANDER VIA WHATSAPP
                        </button>
                    </div>
                </div>
            </div>`;
    } catch (err) {
        console.error("Erreur chargement détails produit:", err);
        container.innerHTML = '<div class="col-12 text-center py-5"><h3 class="text-danger">Erreur lors du chargement</h3><p>' + err.message + '</p></div>';
    }
}

// ==========================================
// Gestion Commandes & Livraison
// ==========================================

async function loadPendingOrders() {
    const container = document.getElementById('pendingOrdersValidation');
    if (!container) return;

    try {
        const orders = await apiCall('/orders/pending', 'GET');
        currentPendingOrders = orders;

        if (orders.length === 0) {
            container.innerHTML = '<div class="text-muted text-center py-4">Aucune commande en attente d\'attribution</div>';
            return;
        }

        container.innerHTML = `<div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead>
                    <tr>
                        <th>Commande</th>
                        <th>Client</th>
                        <th>Adresse</th>
                        <th>Paiement</th>
                        <th>Total</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${orders.map(order => {
            const paymentHtml = order.paid ?
                `<span class="badge bg-success">Payé${order.payment_method ? ' (' + order.payment_method + ')' : ''}</span>` :
                `<span class="badge bg-warning text-dark">Non payé</span>`;
            return `
                        <tr>
                            <td><strong>${order.order_number}</strong></td>
                            <td>${order.client_name}</td>
                            <td>${order.delivery_address}</td>
                            <td>${paymentHtml}</td>
                            <td>${order.total_price.toLocaleString()} FCFA</td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="openAssignModal(${order.id})">
                                    <i class="fas fa-eye me-1"></i>Détails & Action
                                </button>
                            </td>
                        </tr>
                    `}).join('')}
                </tbody>
            </table>
        </div>`;
    } catch (err) {
        container.innerHTML = `<div class="text-danger text-center">Erreur: ${err.message}</div>`;
    }
}

async function openAssignModal(orderId) {
    const order = currentPendingOrders.find(o => o.id === orderId);
    if (!order) return;

    let modalEl = document.getElementById('assignModal');
    if (!modalEl) {
        modalEl = document.createElement('div');
        modalEl.id = 'assignModal';
        modalEl.className = 'modal fade';
        document.body.appendChild(modalEl);
    }

    // Build Items List
    let itemsHtml = '<ul class="list-group list-group-flush mb-3">';
    order.items.forEach(item => {
        const product = currentProducts.find(p => p.id === item.product_id);
        const productName = product ? product.name : `Produit #${item.product_id}`;
        itemsHtml += `
            <li class="list-group-item d-flex justify-content-between">
                <span>${productName} (x${item.quantity})</span>
                <span>${(item.unit_price * item.quantity).toLocaleString()} FCFA</span>
            </li>`;
    });
    itemsHtml += '</ul>';

    // payment info html
    const paymentInfoHtml = order.paid ?
        `<p><strong>Paiement:</strong> <span class="badge bg-success">Payé</span> ${order.payment_method || ''}</p>` :
        `<p><strong>Paiement:</strong> <span class="badge bg-warning text-dark">Non payé</span></p>`;

    modalEl.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-light">
                    <h5 class="modal-title">Gestion Commande ${order.order_number}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Informations Client</h6>
                            <p><strong>Nom:</strong> ${order.client_name}<br>
                            <strong>Téléphone:</strong> ${order.phone || 'N/A'}<br>
                            <strong>Adresse:</strong> ${order.delivery_address}</p>
                            ${paymentInfoHtml}
                        </div>
                        <div class="col-md-6 text-end">
                            <h6>Total Commande</h6>
                            <h3 class="text-success fw-bold">${order.total_price.toLocaleString()} FCFA</h3>
                            <small class="text-muted">${new Date(order.created_at).toLocaleString()}</small>
                        </div>
                    </div>
                    <hr>
                    <h6>Détails du Panier</h6>
                    ${itemsHtml}
                    
                    <hr>
                    <div class="bg-light p-3 rounded">
                        <label class="form-label fw-bold">Assigner à un Livreur:</label>
                        <select id="livreurSelect" class="form-select mb-2">
                             <option value="">Chargement...</option>
                        </select>
                        <small class="text-muted">Sélectionnez un livreur pour valider la commande.</small>
                    </div>
                </div>
                <div class="modal-footer justify-content-between">
                    <button type="button" class="btn btn-outline-danger" onclick="rejectOrder(${order.id})">
                        <i class="fas fa-times me-1"></i>Refuser la Commande
                    </button>
                    <div>
                        <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Annuler</button>
                        <button type="button" class="btn btn-success" id="confirmAssignBtn">
                            <i class="fas fa-check me-1"></i>Valider & Assigner
                        </button>
                    </div>
                </div>
            </div>
        </div>`;

    const modal = new bootstrap.Modal(modalEl);
    modal.show();

    // Fetch Livreurs
    try {
        const users = await apiCall('/users/', 'GET');
        const livreurs = users.filter(u => u.role === 'livreur' && u.is_approved);
        const select = document.getElementById('livreurSelect');

        if (livreurs.length === 0) {
            select.innerHTML = '<option value="">Aucun livreur disponible</option>';
        } else {
            select.innerHTML = '<option value="">Choisir un livreur...</option>' +
                livreurs.map(l => `<option value="${l.id}">${l.username}</option>`).join('');
        }
    } catch (err) {
        console.error("Error fetching livreurs", err);
    }

    // Handle Assign
    document.getElementById('confirmAssignBtn').onclick = async () => {
        const livreurId = document.getElementById('livreurSelect').value;
        if (!livreurId) {
            showToast('Veuillez sélectionner un livreur', 'warning');
            return;
        }

        try {
            await apiCall(`/orders/${orderId}/assign?livreur_id=${livreurId}`, 'PATCH');
            showToast('Commande assignée avec succès', 'success');
            modal.hide();
            loadPendingOrders();
            // Update stats logic here if needed (stats logic assumes on-load refresh)
        } catch (err) {
            showToast(err.message, 'error');
        }
    };
}

async function rejectOrder(orderId) {
    if (!await showConfirmModal('Refuser Commande', 'Êtes-vous sûr de vouloir REFUSER cette commande ? Elle ne sera pas traitée.', 'Refuser', 'danger')) return;

    try {
        // Assuming we have an endpoint to update status directly or we use existing updateOrderStatus logic if accessible
        // Backend text says: update_order_status generic.
        // We need to check if we can call it.
        // Endpoint: PATCH /orders/{id}/status?status=Refusée
        // ENUM is 'Refusée' (with accents).
        // Let's rely on apiCall
        await apiCall(`/orders/${orderId}/status`, 'PATCH', { status: 'Refusée' });

        showToast('Commande refusée', 'info');
        // Close modal if open? rejectOrder is called from modal.
        const modalEl = document.getElementById('assignModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        loadPendingOrders();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function confirmAssignment() {
    const orderId = document.getElementById('assignOrderId').value;
    const livreurId = document.getElementById('livreurSelect').value;

    if (!livreurId) {
        showToast('Veuillez sélectionner un livreur', 'warning');
        return;
    }

    try {
        await apiCall(`/orders/${orderId}/assign?livreur_id=${livreurId}`, 'PATCH');
        showToast('Commande assignée avec succès', 'success');

        const modalEl = document.getElementById('assignModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();

        loadPendingOrders();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function refreshLivreurDeliveries() {
    const container = document.getElementById('deliveriesContainer');
    if (!container) return;

    try {
        const orders = await apiCall('/orders/', 'GET');
        const deliveries = orders.filter(o =>
            ['Validée - En préparation', 'En transit', 'Prêt pour livraison'].includes(o.status)
        );

        // Update stats
        const countPending = document.getElementById('countPending');
        const countInTransit = document.getElementById('countInTransit');
        const countToday = document.getElementById('countToday');

        if (countPending) countPending.textContent = deliveries.filter(o => o.status !== 'En transit').length;
        if (countInTransit) countInTransit.textContent = deliveries.filter(o => o.status === 'En transit').length;

        if (countToday) {
            const today = new Date().toISOString().split('T')[0];
            countToday.textContent = orders.filter(o => o.created_at.startsWith(today)).length;
        }

        const emptyState = document.getElementById('emptyDeliveries');

        if (deliveries.length === 0) {
            container.classList.add('d-none');
            if (emptyState) emptyState.classList.remove('d-none');
            return;
        }

        if (emptyState) emptyState.classList.add('d-none');
        container.classList.remove('d-none');

        container.innerHTML = deliveries.map(order => `
            <div class="card border-0 shadow-sm delivery-card mb-3 overflow-hidden">
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <h6 class="fw-bold mb-1">Commande #${order.id}</h6>
                            <small class="text-muted"><i class="far fa-clock me-1"></i>${new Date(order.created_at).toLocaleString()}</small>
                        </div>
                        <span class="badge ${getLivreurStatusBadgeClass(order.status)} status-badge rounded-pill shadow-sm">
                            ${order.status}
                        </span>
                    </div>
                    
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <div class="d-flex align-items-center">
                                <div class="bg-primary bg-opacity-10 text-primary rounded-circle p-2 me-3">
                                    <i class="fas fa-user small"></i>
                                </div>
                                <div>
                                    <p class="small text-muted mb-0">Client</p>
                                    <p class="fw-bold mb-0">${order.client_name || 'Client'}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="d-flex align-items-center">
                                <div class="bg-danger bg-opacity-10 text-danger rounded-circle p-2 me-3">
                                    <i class="fas fa-map-marker-alt small"></i>
                                </div>
                                <div>
                                    <p class="small text-muted mb-0">Destination</p>
                                    <p class="fw-bold mb-0">${order.delivery_address || 'Lomé, Togo'}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bg-light p-3 rounded-3 mb-4">
                        <p class="small fw-bold mb-2">Contenu :</p>
                        <div class="small text-muted">
                            ${order.items?.map(i => `${i.quantity}x ${i.product_name}`).join(', ') || 'Détails non disponibles'}
                        </div>
                    </div>

                    <div class="d-flex gap-2">
                        <button class="btn btn-success flex-grow-1 py-2 fw-bold" onclick="openLivreurStatusModal(${order.id}, '${order.status}')">
                            <i class="fas fa-edit me-2"></i>Changer Statut
                        </button>
                        <a href="https://wa.me/${order.phone || '22871145609'}" target="_blank" class="btn btn-outline-primary px-3" title="Contacter le client">
                            <i class="fab fa-whatsapp"></i>
                        </a>
                    </div>
                </div>
            </div>
        `).join('');

    } catch (err) {
        console.error(err);
        showToast("Erreur de chargement des livraisons", "error");
    }
}

function getLivreurStatusBadgeClass(status) {
    switch (status) {
        case 'En transit': return 'bg-warning text-dark';
        case 'Livré': return 'bg-success';
        case 'Validée - En préparation': return 'bg-info text-white';
        case 'Prêt pour livraison': return 'bg-primary text-white';
        default: return 'bg-secondary';
    }
}

function openLivreurStatusModal(orderId, currentStatus) {
    const activeOrderInput = document.getElementById('activeOrderId');
    if (!activeOrderInput) return;

    activeOrderInput.value = orderId;
    const noteInput = document.getElementById('deliveryNote');
    if (noteInput) noteInput.value = '';

    const deliveredCheck = document.getElementById('statusDelivered');
    const transitCheck = document.getElementById('statusTransit');

    if (currentStatus === 'En transit' || currentStatus === 'Prêt pour livraison') {
        if (deliveredCheck) deliveredCheck.checked = true;
    } else {
        if (transitCheck) transitCheck.checked = true;
    }

    const modalEl = document.getElementById('statusModal');
    if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
}

function optimizeLivreurRoute() {
    showToast("Optimisation de l'itinéraire en cours...", "info");
    setTimeout(() => {
        showToast("Itinéraire optimisé pour vos destinations !", "success");
        refreshLivreurDeliveries();
    }, 1500);
}

async function updateOrderStatus(orderId, newStatus) {
    if (!await showConfirmModal('Mettre à jour Statut', `Confirmer le changement de statut à "${newStatus}" ?`, 'Valider', 'primary')) return;

    try {
        await apiCall(`/orders/${orderId}/status`, 'PATCH', { status: newStatus });
        showToast('Statut mis à jour !', 'success');
        refreshLivreurDeliveries();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copié !', 'success');
    });
}


function changeQuantity(productId, delta) {
    const qtyElement = document.getElementById('qty-' + productId);
    if (qtyElement) {
        let currentQty = cart[productId] || 0;
        currentQty = Math.max(0, currentQty + delta);
        cart[productId] = currentQty;
        qtyElement.textContent = currentQty;
        updateOrderSummary();
    }
}

function updateOrderSummary() {
    const orderItems = document.getElementById('order-items');
    const totalPriceElement = document.getElementById('total-price');
    const orderBtn = document.getElementById('orderBtn');

    if (!orderItems || !totalPriceElement || !orderBtn) return;

    let total = 0;
    let itemsHtml = '';
    let hasItems = false;

    Object.keys(cart).forEach(productId => {
        const qty = cart[productId];
        if (qty > 0) {
            const product = currentProducts.find(p => p.id == productId);
            if (product) {
                const subtotal = qty * product.price;
                total += subtotal;
                hasItems = true;
                itemsHtml += `
                    <div class="d-flex justify-content-between mb-2 p-2 bg-light rounded">
                        <span>${product.name} (x${qty})</span>
                        <span class="fw-bold">${subtotal.toLocaleString()} FCFA</span>
                    </div>`;
            }
        }
    });

    if (!hasItems) {
        orderItems.innerHTML = '<p class="text-muted text-center">Aucun produit sélectionné</p>';
    } else {
        orderItems.innerHTML = itemsHtml;
    }

    totalPriceElement.textContent = total.toLocaleString() + ' FCFA';

    updateOrderBtnState();
}

function updateOrderBtnState() {
    const orderBtn = document.getElementById('orderBtn');
    if (!orderBtn) return;
    const hasItems = Object.keys(cart).some(pid => cart[pid] > 0);
    const pm = document.getElementById('paymentMethod');
    const pmVal = pm ? pm.value : '';
    orderBtn.disabled = !(hasItems && pmVal);
}

function initOrderForm() {
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        // Pré-remplir les informations du client si connecté
        const token = sessionStorage.getItem('token');
        if (token) {
            apiCall('/users/me', 'GET')
                .then(user => {
                    const nomInput = document.getElementById('nom');
                    const telInput = document.getElementById('telephone');
                    if (nomInput && (!nomInput.value || nomInput.value === '')) {
                        nomInput.value = `${user.first_name || ''} ${user.last_name || ''}`.trim();
                    }
                    if (telInput && (!telInput.value || telInput.value === '')) {
                        telInput.value = user.phone || '';
                    }
                })
                .catch(err => console.error("Erreur pré-remplissage formulaire commande:", err));
        }

        // payment selection listener
        const pmSelect = document.getElementById('paymentMethod');
        const paymentInfo = document.createElement('div');
        paymentInfo.id = 'paymentInfo';
        paymentInfo.className = 'mb-3 text-success fw-bold';
        paymentInfo.style.display = 'none';
        if (pmSelect && pmSelect.parentNode) {
            pmSelect.parentNode.insertBefore(paymentInfo, pmSelect.nextSibling);
            pmSelect.addEventListener('change', () => {
                const total = parseInt(document.getElementById('total-price').textContent.replace(/[^0-9]/g, ''));
                if (pmSelect.value) {
                    paymentInfo.textContent = `Montant total : ${total.toLocaleString()} FCFA`;
                    paymentInfo.style.display = 'block';
                } else {
                    paymentInfo.style.display = 'none';
                }
                updateOrderBtnState();
            });
        }

        orderForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const submitBtn = orderForm.querySelector('button[type="submit"]');

            // Vérifier si l'utilisateur est connecté
            const token = sessionStorage.getItem('token');
            if (!token) {
                if (await showConfirmModal('Connexion Requise', 'Vous devez être connecté pour passer une commande. Voulez-vous aller à la page de connexion ?', 'Se connecter', 'primary')) {
                    window.location.href = 'manioc_agri/authentification.html';
                }
                return;
            }

            setButtonLoading(submitBtn, true);

            const items = [];
            Object.keys(cart).forEach(pid => {
                if (cart[pid] > 0) {
                    const p = currentProducts.find(prod => prod.id == pid);
                    items.push({
                        product_id: parseInt(pid),
                        quantity: cart[pid],
                        unit_price: p.price
                    });
                }
            });

            const paymentMethodSelect = document.getElementById('paymentMethod');
            const paymentMethod = paymentMethodSelect ? paymentMethodSelect.value : null;

            // Paid is false for mobile payments until webhook confirmation
            const isMobilePayment = (paymentMethod === 'FLOOZ' || paymentMethod === 'TMONEY');
            const isPaid = (paymentMethod && !isMobilePayment);

            const orderData = {
                order_number: 'CMD-' + Date.now(),
                client_name: document.getElementById('nom').value,
                phone: document.getElementById('telephone').value,
                delivery_address: document.getElementById('localisation').value,
                total_price: parseInt(document.getElementById('total-price').textContent.replace(/[^0-9]/g, '')),
                payment_method: paymentMethod || null,
                paid: isPaid,
                items: items
            };

            try {
                const result = await apiCall('/orders/', 'POST', orderData);

                if (isMobilePayment) {
                    showToast(`Commande ${result.order_number} créée. Initiation du paiement...`, 'info');
                    try {
                        const payRes = await apiCall('/payments/initiate', 'POST', {
                            order_id: result.id,
                            phone_number: orderData.phone,
                            network: paymentMethod
                        });

                        if (payRes.status === 'success') {
                            await showSuccessModal('Paiement Initié',
                                `Merci ! Un message de confirmation USSD a été envoyé au ${orderData.phone}. <br><br>
                                 <b>Veuillez valider la transaction sur votre téléphone</b> pour confirmer votre commande. <br>
                                 Votre numéro de commande est : <strong>${result.order_number}</strong>`);
                        }
                    } catch (payErr) {
                        console.error("PayGate Error:", payErr);
                        showToast(`Erreur d'initiation du paiement : ${payErr.message}`, 'error');
                        // L'ordre est quand même créé, on peut suggérer un autre moyen
                    }
                } else {
                    showToast(`Commande ${result.order_number} enregistrée !`, 'success');
                    await showSuccessModal('Commande Confirmée', `Votre commande ${result.order_number} a été bien enregistrée. Nous vous contacterons sous peu.`);
                }

                orderForm.reset();
                cart = {};
                if (typeof loadProducts === 'function') loadProducts();
                updateOrderSummary();
            } catch (err) {
                showToast(err.message, 'error');
            } finally {
                setButtonLoading(submitBtn, false);
            }
        });
    }
}

// ==========================================
// Commandes et Profil (Client)
// ==========================================

async function initClientProfile() {
    const form = document.getElementById('updateProfileForm');
    if (!form) return;

    // Load initial data for modal
    try {
        const user = await apiCall('/users/me', 'GET');
        if (user) {
            const fname = document.getElementById('profileFirstName');
            const lname = document.getElementById('profileLastName');
            const phone = document.getElementById('profilePhone');

            if (fname) fname.value = user.first_name || '';
            if (lname) lname.value = user.last_name || '';
            if (phone) phone.value = user.phone || '';
        }
    } catch (err) {
        console.error("Erreur chargement profil client:", err);
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        const btn = document.getElementById('saveProfileBtn');
        setButtonLoading(btn, true);

        const data = {
            first_name: document.getElementById('profileFirstName').value,
            last_name: document.getElementById('profileLastName').value,
            phone: document.getElementById('profilePhone').value
        };

        const password = document.getElementById('profilePassword').value;
        if (password) {
            data.password = password;
        }

        try {
            const updatedUser = await apiCall('/users/me', 'PATCH', data);
            showToast('Profil mis à jour avec succès', 'success');

            // Update UI
            const nameDisplay = document.getElementById('clientNameDisplay');
            if (nameDisplay) {
                nameDisplay.textContent = `${updatedUser.first_name || ''} ${updatedUser.last_name || ''}`;
            }

            // Close modal
            const modalEl = document.getElementById('updateProfileModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();

            document.getElementById('profilePassword').value = '';
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setButtonLoading(btn, false);
        }
    });
}

async function loadClientOrders() {
    const ordersList = document.getElementById('ordersList');
    if (!ordersList) return;

    try {
        // Obtenir le profil pour le nom
        const user = await apiCall('/users/me', 'GET');
        const nameDisplay = document.getElementById('clientNameDisplay');
        if (nameDisplay && user) {
            nameDisplay.textContent = `${user.first_name} ${user.last_name}`;
        }

        const orders = await apiCall('/orders/', 'GET');

        if (orders.length === 0) {
            ordersList.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">Vous n\'avez pas encore de commandes.</td></tr>';
        } else {
            ordersList.innerHTML = orders.map(order => {
                const paymentBadge = order.paid ? `<span class="badge bg-success">Payé</span>` : `<span class="badge bg-warning text-dark">Non payé</span>`;
                return `
                <tr>
                    <td>
                        <span class="fw-bold text-dark">${order.order_number}</span>
                    </td>
                    <td>${new Date(order.created_at).toLocaleDateString('fr-FR')}</td>
                    <td>${order.delivery_address || 'Lomé'}</td>
                    <td>${paymentBadge}</td>
                    <td>
                        <span class="badge bg-${statusColor(order.status)}">${order.status}</span>
                    </td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary" onclick="showTracking('${order.order_number}')">
                            <i class="fas fa-eye me-1"></i> Suivre
                        </button>
                    </td>
                </tr>
            `}).join('');
        }

        // Update stats counters
        const total = orders.length;
        const pending = orders.filter(o => o.status.includes('attente') || o.status.includes('Validée')).length;
        const delivered = orders.filter(o => o.status === 'Livré').length;

        animateValue("totalOrders", 0, total, 1000);
        animateValue("pendingOrders", 0, pending, 1000);
        animateValue("deliveredOrders", 0, delivered, 1000);

    } catch (err) {
        console.error("Erreur chargement commandes client:", err);
        ordersList.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Erreur de chargement</td></tr>';
    }
}


function statusColor(status) {
    if (status.includes('attente')) return 'secondary';
    if (status.includes('Validée')) return 'info';
    if (status.includes('transit')) return 'primary';
    if (status.includes('Livré')) return 'success';
    if (status.includes('Refusée')) return 'danger';
    return 'secondary';
}

window.showTracking = async function (orderNumber) {
    const trackingDetails = document.getElementById('trackingDetails');
    if (!trackingDetails) return;

    try {
        const order = await apiCall(`/orders/track/${orderNumber}`, 'GET', null, false);

        let html = `<h6 class="fw-bold text-success mb-3">${order.order_number}</h6>`;
        html += `<div class="mb-3">
                    <strong>Statut:</strong> <span class="badge bg-${statusColor(order.status)}">${order.status}</span>
                 </div>`;
        html += `<p class="mb-1"><small class="text-muted">Client:</small> <strong>${order.client_name}</strong></p>`;
        html += `<p class="mb-1"><small class="text-muted">Adresse:</small> <strong>${order.delivery_address}</strong></p>`;

        if (order.livreur_id) {
            html += `<p class="mt-3 text-info"><i class="fas fa-motorcycle me-2"></i>Votre livreur est en route!</p>`;
        }

        trackingDetails.innerHTML = html;

        const modalEl = document.getElementById('trackingModal');
        if (modalEl) {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }
    } catch (err) {
        console.error("Tracking Error:", err);
        showToast('Erreur de suivi: ' + err.message, 'error');
    }
}



function initLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function (e) {
            e.preventDefault();
            sessionStorage.clear();
            showToast('Déconnexion réussie!', 'success');
            setTimeout(() => {
                const rootPath = window.location.pathname.includes('manioc_agri/') ? '../' : '';
                window.location.href = rootPath + 'index.html';
            }, 500);
        });
    }
}

// ==========================================
// Initialisation Globale
// ==========================================

// ==========================================
// Auth Guard – page-level security
// ==========================================
const PAGE_ROLES = {
    'admin.html': ['admin'],
    'gestionnaire.html': ['gestionnaire', 'admin'],
    'producteur.html': ['producteur', 'admin'],
    'agent_terrain.html': ['agent', 'admin'],
    'client.html': ['client', 'admin'],
    'livreur.html': ['livreur', 'admin'],
};

const ROLE_HOME = {
    'admin': '/manioc_agri/admin.html',
    'gestionnaire': '/manioc_agri/gestionnaire.html',
    'producteur': '/manioc_agri/producteur.html',
    'agent': '/manioc_agri/agent_terrain.html',
    'client': '/manioc_agri/client.html',
    'livreur': '/manioc_agri/livreur.html',
};

function checkAuth() {
    const path = window.location.pathname;
    const AUTH_PAGE = '/manioc_agri/authentification.html';

    // Determine which page we are on
    const currentPage = Object.keys(PAGE_ROLES).find(p => path.endsWith(p));
    if (!currentPage) return; // Public pages (index, catalogue, etc.) – no check needed

    const token = sessionStorage.getItem('token');
    const userRole = sessionStorage.getItem('userRole');

    // 1. Not logged in → redirect to login
    if (!token || !userRole) {
        sessionStorage.setItem('redirectAfterLogin', window.location.href);
        window.location.replace(AUTH_PAGE);
        return;
    }

    // 2. Wrong role → redirect to the user's own dashboard
    const allowed = PAGE_ROLES[currentPage];
    if (!allowed.includes(userRole)) {
        const home = ROLE_HOME[userRole] || '/';
        window.location.replace(home);
    }
}

function init() {
    // Security: enforce authentication and role-based access
    checkAuth();

    if (typeof initOrderForm === 'function') initOrderForm();
    if (typeof initLogout === 'function') initLogout();

    // Initialisation du date picker s'il existe
    const dateLivraison = document.getElementById('dateLivraison');
    if (dateLivraison) {
        const today = new Date().toISOString().split('T')[0];
        dateLivraison.setAttribute('min', today);
    }

    const path = window.location.pathname;

    // Admin
    if (path.includes('admin.html')) {
        loadPendingRegistrations();
        loadUsers();
        loadProducts();
        initProductForm();
        loadPendingOrders();
        loadOrderStats();
    }

    // Gestionnaire
    if (path.includes('gestionnaire.html')) {
        loadProducts();
        loadPendingOrders();
        loadPendingRegistrations();
        loadUsers();
    }

    // Producteur et Catalogue
    if (path.includes('producteur.html')) {
        loadProducts();
        initProductForm();
        initAgricultureManagement();
    }

    if (path.includes('catalogue.html')) {
        loadProducts();
    }

    if (path.includes('produit-details.html')) {
        loadProductDetails();
    }

    // Client
    if (path.includes('client.html')) {
        loadClientOrders();
        initClientProfile();
    }

    if (path.includes('livreur.html')) {
        refreshLivreurDeliveries();
    }

    if (path.includes('agent_terrain.html')) {
        initAgricultureManagement();
    }
}

// ==========================================
// Dashboard Analytics & Stats
// ==========================================

async function loadOrderStats() {
    try {
        const orders = await apiCall('/orders/', 'GET');

        const stats = {
            total: orders.length,
            pending: orders.filter(o => o.status === 'En attente de validation' || o.status === 'Validée').length,
            delivered: orders.filter(o => o.status === 'Livré').length,
            rejected: orders.filter(o => o.status === 'Refusée').length
        };

        // Update with animation
        animateValue("totalOrders", 0, stats.total, 1000);
        animateValue("pendingOrdersStat", 0, stats.pending, 1000);
        animateValue("deliveredOrdersStat", 0, stats.delivered, 1000);
        animateValue("rejectedOrdersStat", 0, stats.rejected, 1000);

        // Initialize Chart
        initOrderChart(orders);

    } catch (err) {
        console.error("Erreur stats commandes:", err);
    }
}

function initOrderChart(orders) {
    const ctx = document.getElementById('orderChart');
    if (!ctx) return;

    const labels = [];
    const data = [];
    for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dateStr = d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
        labels.push(dateStr);

        const count = orders.filter(o => {
            const oDate = new Date(o.created_at);
            return oDate.toDateString() === d.toDateString();
        }).length;
        data.push(count);
    }

    const existingChart = Chart.getChart("orderChart");
    if (existingChart) existingChart.destroy();

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Commandes',
                data: data,
                borderColor: '#198754',
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#198754'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// ==========================================
// Gestion Agricole (Champs & Cultures)
// ==========================================

function initAgricultureManagement() {
    const fieldForm = document.getElementById('fieldForm');
    const cropForm = document.getElementById('cropForm');

    if (fieldForm) {
        fieldForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                name: document.getElementById('fieldName').value,
                location_name: document.getElementById('fieldLocationName').value,
                area_size_hectares: parseFloat(document.getElementById('fieldArea').value)
            };
            try {
                await apiCall('/fields', 'POST', data);
                showToast("Nouveau champ enregistré !", "success");
                fieldForm.reset();
                loadFields();
            } catch (err) {
                console.error("Erreur champ:", err);
                showToast("Échec de l'enregistrement du champ.", "danger");
            }
        });
    }

    if (cropForm) {
        cropForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                field_id: parseInt(document.getElementById('cropFieldId').value),
                crop_type: document.getElementById('cropType').value,
                area_occupied_hectares: parseFloat(document.getElementById('cropArea').value),
                planting_date: document.getElementById('cropPlantingDate').value
            };
            try {
                await apiCall('/crops', 'POST', data);
                showToast("Culture démarrée !", "success");
                cropForm.reset();
                loadFields(); // Recharger pour voir les mises à jour
            } catch (err) {
                console.error("Erreur culture:", err);
                showToast("Échec du démarrage de la culture.", "danger");
            }
        });
    }

    loadFields();
}

async function loadFields() {
    const container = document.getElementById('fieldsListContainer');
    const fieldSelect = document.getElementById('cropFieldId');
    if (!container) return;

    try {
        const fields = await apiCall('/fields', 'GET');

        // Update Select
        if (fieldSelect) {
            fieldSelect.innerHTML = '<option value="">Sélectionnez un champ...</option>';
            fields.forEach(f => {
                const opt = document.createElement('option');
                opt.value = f.id;
                opt.textContent = f.name;
                fieldSelect.appendChild(opt);
            });
        }

        if (fields.length === 0) {
            container.innerHTML = `
                <div class="card border-0 shadow-sm rounded-4 p-5 text-center">
                    <div class="text-muted mb-3"><i class="fas fa-map-marked-alt fa-3x"></i></div>
                    <h5>Aucun champ enregistré</h5>
                    <p class="text-muted mb-0">Commencez par ajouter votre première parcelle de terre.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        fields.forEach(f => {
            const card = document.createElement('div');
            card.className = "card border-0 shadow-sm rounded-4 mb-4 overflow-hidden reveal";
            card.innerHTML = `
                <div class="row g-0">
                    <div class="col-md-8 p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div>
                                <h5 class="fw-bold mb-1">${f.name}</h5>
                                <p class="text-muted small mb-0"><i class="fas fa-map-marker-alt me-1"></i>${f.location_name}</p>
                            </div>
                            <span class="badge bg-success-subtle text-success border border-success-subtle rounded-pill">${f.area_size_hectares} ha</span>
                        </div>
                        <div id="crops-${f.id}">
                            <div class="spinner-border spinner-border-sm text-success" role="status"></div>
                        </div>
                    </div>
                    <div class="col-md-4 bg-light border-start d-flex align-items-center justify-content-center p-3" id="weather-${f.id}">
                        <div class="text-center">
                            <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                            <div class="small text-muted mt-2">Météo...</div>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(card);

            // Load detail data for this field
            loadFieldCrops(f.id);
            loadFieldWeather(f.id);
        });

    } catch (err) {
        console.error("Erreur chargement champs:", err);
        container.innerHTML = '<div class="alert alert-danger">Erreur lors de la récupération des données.</div>';
    }
}

async function loadFieldCrops(fieldId) {
    const list = document.getElementById(`crops-${fieldId}`);
    if (!list) return;

    try {
        const crops = await apiCall(`/crops/by-field/${fieldId}`, 'GET');
        if (crops.length === 0) {
            list.innerHTML = '<p class="small text-muted italic mb-0">Aucune culture active</p>';
            return;
        }

        list.innerHTML = crops.map(c => `
            <div class="d-flex align-items-center mb-2">
                <div class="bg-success rounded-circle me-2" style="width: 8px; height: 8px;"></div>
                <div class="flex-grow-1 small">
                    <span class="fw-bold text-dark">${c.crop_type}</span> 
                    <span class="text-muted"> (${c.area_occupied_hectares} ha) - Planté le ${new Date(c.planting_date).toLocaleDateString()}</span>
                </div>
                <span class="badge ${c.status === 'harvested' ? 'bg-secondary' : 'bg-primary'} rounded-pill" style="font-size: 0.65rem;">${c.status}</span>
            </div>
        `).join('');

    } catch (err) {
        list.innerHTML = '<span class="text-danger small">Erreur cultures</span>';
    }
}

async function loadFieldWeather(fieldId) {
    const container = document.getElementById(`weather-${fieldId}`);
    if (!container) return;

    try {
        const w = await apiCall(`/weather/${fieldId}`, 'GET');
        container.innerHTML = `
            <div class="text-center">
                <img src="https://openweathermap.org/img/wn/${w.weather[0].icon}@2x.png" width="60" alt="météo">
                <div class="h4 fw-bold mb-0">${Math.round(w.main.temp)}°C</div>
                <div class="text-capitalize small text-muted">${w.weather[0].description}</div>
                <div class="mt-2 small text-primary"><i class="fas fa-tint me-1"></i>${w.main.humidity}% Humidité</div>
                ${w.mock ? '<div class="badge bg-warning-subtle text-warning mt-1" style="font-size: 0.6rem;">Demo</div>' : ''}
            </div>
        `;
    } catch (err) {
        container.innerHTML = '<div class="text-muted small">Météo indisponible</div>';
    }
}

// ==========================================
// WhatsApp Contact Button
// ==========================================

function initWhatsAppButton() {
    // Si le bouton existe déjà dans le HTML statique, ne pas en créer un second
    if (document.getElementById('whatsapp-btn')) return;

    const phoneNumber = '22871145609';
    const message = encodeURIComponent('Bonjour ! Je souhaite avoir plus d\'informations sur ManiocAgri.');
    const whatsappUrl = `https://wa.me/${phoneNumber}?text=${message}`;

    const link = document.createElement('a');
    link.id = 'whatsapp-btn';
    link.href = whatsappUrl;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.setAttribute('aria-label', 'Contacter via WhatsApp');
    link.title = 'Contactez-nous sur WhatsApp';
    link.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="30" height="30" fill="white">
            <path d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222
                0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27
                h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6
                c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7
                c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5
                49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5
                0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18
                -5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2
                -12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3
                1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3
                -12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9
                -5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4
                2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9
                10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4
                -1.3-2.5-5-3.9-10.5-6.6z"/>
        </svg>
    `;
    document.body.appendChild(link);
}

async function loadDemandForecast() {
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;

    try {
        const data = await apiCall('/ai/forecast', 'GET');
        if (!data.forecast || data.forecast.length === 0) {
            ctx.parentElement.innerHTML = `<div class="text-center py-4 text-muted">${data.msg || 'Données insuffisantes'}</div>`;
            return;
        }

        const labels = data.forecast.map(f => {
            const d = new Date(f.date);
            return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
        });
        const values = data.forecast.map(f => f.predicted_orders);

        // Destroy existing chart if any
        if (window.myForecastChart) {
            window.myForecastChart.destroy();
        }

        window.myForecastChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Commandes Prévues',
                    data: values,
                    backgroundColor: 'rgba(251, 191, 36, 0.6)',
                    borderColor: '#f59e0b',
                    borderWidth: 1,
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });

    } catch (err) {
        console.error("Erreur prédiction:", err);
    }
}

// ==========================================
// Smart Routing Logic
// ==========================================

async function optimizeDeliveries() {
    showToast("Optimisation des tournées en cours...", "info");
    // Mock for demo if no backend coordination yet
    setTimeout(() => {
        showToast("Tournée optimisée ! Ordre de livraison mis à jour.", "success");
    }, 1500);
}


// ==========================================
// Contact Form to WhatsApp
// ==========================================

function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    if (!contactForm) return;

    contactForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const name = this.querySelector('input[type="text"]').value.trim();
        const email = this.querySelector('input[type="email"]').value.trim();
        const message = this.querySelector('textarea').value.trim();

        if (!name || !message) {
            showToast('Veuillez remplir au moins votre nom et votre message.', 'warning');
            return;
        }

        const phoneNumber = '22871145609';
        const fullMessage = encodeURIComponent(
            `*Nouveau message de contact*\n\n` +
            `*Nom:* ${name}\n` +
            `*Email:* ${email || 'Non renseigné'}\n\n` +
            `*Message:* ${message}`
        );

        const whatsappUrl = `https://wa.me/${phoneNumber}?text=${fullMessage}`;

        showToast('Redirection vers WhatsApp...', 'info');
        setTimeout(() => {
            window.open(whatsappUrl, '_blank');
        }, 1000);
    });
}


function whatsappOrder(productName, price) {
    const phoneNumber = '22871145609';
    const message = encodeURIComponent(`Bonjour ManiocAgri ! Je souhaite commander le produit suivant :\n\n- *${productName}*\n- *Prix:* ${price.toLocaleString()} FCFA/kg\n\nMerci de me donner la marche à suivre.`);
    window.open(`https://wa.me/${phoneNumber}?text=${message}`, '_blank');
}


document.addEventListener('DOMContentLoaded', () => {
    initWhatsAppButton(); // Charger le bouton en priorité
    initContactForm();    // Service d'envoi WhatsApp
    initChatWidget();     // Widget de chat IA
    try { init(); } catch (e) { console.error('init() error:', e); }
});

// ==========================================
// Widget Chat IA Flottant
// ==========================================

function initChatWidget() {
    const fab = document.getElementById('chat-fab');
    const panel = document.getElementById('chat-panel');
    const closeBtn = document.getElementById('chat-close-btn');
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const messages = document.getElementById('chat-messages');

    if (!fab || !panel) return; // Widget non présent sur cette page

    let isChatOpen = false;

    // Toggle du panneau
    function toggleChat() {
        isChatOpen = !isChatOpen;
        if (isChatOpen) {
            panel.classList.remove('hidden');
            // Re-trigger animation
            panel.style.animation = 'none';
            panel.offsetHeight; // Force reflow
            panel.style.animation = '';
            // Supprimer le badge de notification
            const badge = fab.querySelector('.chat-badge');
            if (badge) badge.style.display = 'none';
            // Focus sur l'input
            setTimeout(() => input && input.focus(), 300);
        } else {
            panel.classList.add('hidden');
        }
    }

    fab.addEventListener('click', toggleChat);
    if (closeBtn) closeBtn.addEventListener('click', toggleChat);

    // Envoi via touche Entrée
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Envoi via bouton
    if (sendBtn) sendBtn.addEventListener('click', sendMessage);

    // Ajouter une bulle de message
    function appendMessage(text, type) {
        const bubble = document.createElement('div');
        bubble.className = `msg-bubble ${type}`;
        bubble.textContent = text;
        messages.appendChild(bubble);
        messages.scrollTop = messages.scrollHeight;
        return bubble;
    }

    // Afficher l'indicateur de frappe
    function showTyping() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;
        messages.appendChild(indicator);
        messages.scrollTop = messages.scrollHeight;
    }

    function hideTyping() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    // Envoyer un message à l'API
    async function sendMessage() {
        if (!input) return;
        const text = input.value.trim();
        if (!text) return;

        // Afficher le message utilisateur
        appendMessage(text, 'user');
        input.value = '';
        input.disabled = true;
        if (sendBtn) sendBtn.disabled = true;

        // Afficher l'animation de frappe
        showTyping();

        try {
            const response = await fetch('/api/v1/ai/chat-public', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text })
            });

            hideTyping();

            if (!response.ok) {
                throw new Error('Erreur réseau');
            }

            const data = await response.json();
            appendMessage(data.response || 'Désolé, je n\'ai pas pu répondre.', 'bot');
        } catch (err) {
            hideTyping();
            appendMessage('⚠️ Service temporairement indisponible. Contactez-nous sur WhatsApp !', 'bot');
            console.error('Chat error:', err);
        } finally {
            input.disabled = false;
            if (sendBtn) sendBtn.disabled = false;
            input.focus();
        }
    }
}

// ==========================================
// UX Enhancements: Scroll Animations & Navbar
// ==========================================
document.addEventListener('DOMContentLoaded', function () {
    // 1. Dynamic Navbar
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
        // Trigger once on load
        if (window.scrollY > 50) navbar.classList.add('navbar-scrolled');
    }

    // 2. Reveal Animations on Scroll
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target); // Optional: animate only once
            }
        });
    }, observerOptions);

    document.querySelectorAll('.reveal').forEach((el) => {
        observer.observe(el);
    });
});
