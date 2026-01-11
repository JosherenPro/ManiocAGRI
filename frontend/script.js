// Scripts pour ManiocAgri - Version Premium avec Toast Notifications

const API_BASE_URL = '/api/v1';

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

function initAuthForm() {
    const authForm = document.getElementById('authForm');
    if (authForm) {
        authForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('errorMessage');
            const submitBtn = authForm.querySelector('button[type="submit"]');

            errorMessage.style.display = 'none';
            setButtonLoading(submitBtn, true);

            const params = new URLSearchParams();
            params.append('username', username);
            params.append('password', password);

            try {
                const data = await apiCall('/auth/login/access-token', 'POST', params, false);
                sessionStorage.setItem('token', data.access_token);

                // Récupérer les infos utilisateur
                const user = await apiCall('/users/me', 'GET');
                sessionStorage.setItem('userRole', user.role);
                sessionStorage.setItem('username', user.username);

                showToast('Connexion réussie! Redirection...', 'success');
                setTimeout(() => {
                    window.location.href = user.role + '.html';
                }, 500);
            } catch (err) {
                errorMessage.textContent = err.message;
                errorMessage.style.display = 'block';
                setButtonLoading(submitBtn, false);
            }
        });
    }
}

function initRegisterForm() {
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const role = document.getElementById('regRole').value;
            const username = document.getElementById('regUsername').value;
            const firstName = document.getElementById('regPrenom').value;
            const lastName = document.getElementById('regNom').value;
            const phone = document.getElementById('regPhone').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            const confirmPassword = document.getElementById('regConfirmPassword').value;
            const errorMessage = document.getElementById('errorMessage');
            const successMessage = document.getElementById('successMessage');
            const submitBtn = registerForm.querySelector('button[type="submit"]');

            errorMessage.style.display = 'none';
            successMessage.style.display = 'none';

            if (password !== confirmPassword) {
                errorMessage.textContent = 'Les mots de passe ne correspondent pas.';
                errorMessage.style.display = 'block';
                return;
            }

            setButtonLoading(submitBtn, true);

            try {
                await apiCall('/auth/signup', 'POST', {
                    username,
                    email,
                    password,
                    role,
                    first_name: firstName,
                    last_name: lastName,
                    phone
                }, false);

                // successMessage.textContent = 'Inscription réussie. ' + (role === 'client' ? 'Connectez-vous dès maintenant.' : 'Un administrateur doit approuver votre compte.');
                // successMessage.style.display = 'block';
                this.reset();
                // showToast('Inscription réussie!', 'success');

                const msg = role === 'client' ?
                    'Votre compte a été créé avec succès ! Connectez-vous dès maintenant pour passer commande.' :
                    'Votre inscription a été enregistrée. Un administrateur validera votre accès très prochainement.';

                await showSuccessModal('Inscription Réussie 🚀', msg);

                // Si client, rediriger vers l'onglet de connexion
                if (role === 'client') {
                    const loginTab = document.getElementById('login-tab');
                    if (loginTab) {
                        new bootstrap.Tab(loginTab).show();
                    }
                }
            } catch (err) {
                errorMessage.textContent = err.message;
                errorMessage.style.display = 'block';
                showToast(err.message, 'error');
            } finally {
                setButtonLoading(submitBtn, false);
            }
        });
    }
}

// ===============================
// New: Order Statistics
// ===============================
async function loadOrderStats() {
    // Only run if stats elements exist
    if (!document.getElementById('totalOrders')) return;

    try {
        const orders = await apiCall('/orders/', 'GET');

        const stats = {
            total: orders.length,
            pending: orders.filter(o => ['En attente de validation', 'Validée - En préparation'].includes(o.status)).length,
            delivered: orders.filter(o => o.status === 'Livré').length,
            rejected: orders.filter(o => o.status === 'Refusée').length
        };

        // Animate numbers
        animateValue('totalOrders', 0, stats.total, 1000);
        animateValue('pendingOrdersStat', 0, stats.pending, 1000);
        animateValue('deliveredOrdersStat', 0, stats.delivered, 1000);
        animateValue('rejectedOrdersStat', 0, stats.rejected, 1000);

    } catch (err) {
        console.error("Failed to load order stats:", err);
    }
}

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
// ==========================================

function initAddUserForm() {
    const addUserForm = document.getElementById('addUserForm');
    if (!addUserForm) return;

    addUserForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const submitBtn = document.getElementById('addUserBtn');
        setButtonLoading(submitBtn, true);

        const userData = {
            username: document.getElementById('newUsername').value,
            email: document.getElementById('newEmail').value,
            password: document.getElementById('newPassword').value,
            role: document.getElementById('newRole').value,
            is_approved: true
        };

        try {
            await apiCall('/users/', 'POST', userData);
            showToast('Utilisateur créé avec succès!', 'success');
            addUserForm.reset();
            loadUsers();
            loadPendingRegistrations();
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setButtonLoading(submitBtn, false);
        }
    });
}

// ==========================================
// Produits (CRUD Admin & Producteur)
// ==========================================

function initProductForm() {
    const productForm = document.getElementById('productForm');
    if (!productForm) return;

    productForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const id = document.getElementById('productId').value;
        const name = document.getElementById('productName').value;
        const price = document.getElementById('productPrice').value;
        const stock = document.getElementById('productStock').value;
        const description = document.getElementById('productDescription').value;
        const submitBtn = document.getElementById('saveProductBtn');
        const nameInput = document.getElementById('productName');
        const nameError = document.getElementById('productNameError');

        // Clear previous errors
        nameInput.classList.remove('is-invalid');
        if (nameError) nameError.textContent = '';

        const data = {
            name: name,
            price: parseFloat(price),
            stock_quantity: parseInt(stock),
            description: description
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

    document.getElementById('productId').value = product.id;
    document.getElementById('productName').value = product.name;
    document.getElementById('productPrice').value = product.price;
    document.getElementById('productStock').value = product.stock_quantity;
    document.getElementById('productDescription').value = product.description || '';
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
    document.getElementById('productId').value = '';
    const title = document.getElementById('productFormTitle');
    if (title) title.innerHTML = '<i class="fas fa-plus-circle me-2 text-success"></i>Ajouter un produit';

    const cancelBtn = document.getElementById('cancelEditBtn');
    if (cancelBtn) cancelBtn.classList.add('d-none');

    document.getElementById('productName').classList.remove('is-invalid');
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
                    <img src="${product.image_url ? '/' + product.image_url : '/static/images/default-product.jpg'}" 
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
            <div class="col-md-4 col-lg-3">
                <div class="card h-100 product-card border-0 shadow-sm overflow-hidden" onclick="window.location.href='produit-details.html?id=${product.id}'">
                    <div class="position-relative">
                        <img src="${product.image_url ? '/' + product.image_url : '/static/images/default-product.jpg'}" 
                             class="card-img-top" alt="${product.name}" style="height: 200px; object-fit: cover;">
                        <span class="position-absolute top-0 end-0 m-2 badge bg-success shadow-sm">${product.price.toLocaleString()} FCFA/kg</span>
                    </div>
                    <div class="card-body p-3">
                        <h6 class="card-title fw-bold mb-1">${product.name}</h6>
                        <small class="text-muted d-block mb-3 text-truncate">${product.description || 'Produit local de qualité 🌿'}</small>
                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <button class="btn btn-success btn-sm w-100 rounded-pill shadow-sm" onclick="event.stopPropagation(); addToCart(${product.id})">
                                <i class="fas fa-shopping-basket me-2"></i>Acheter
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
    document.getElementById('productFormTitle').textContent = 'Nouveau Produit';

    const title = document.getElementById('productFormTitle');
    if (title) title.innerHTML = '<i class="fas fa-plus-circle me-2 text-success"></i>Nouveau Produit';

    const cancelBtn = document.getElementById('cancelEditBtn');
    if (cancelBtn) cancelBtn.classList.add('d-none');
}

// ... existing helper functions (changeQuantity, updateOrderSummary, initOrderForm) ...

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
                        <th>Total</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${orders.map(order => `
                        <tr>
                            <td><strong>${order.order_number}</strong></td>
                            <td>${order.client_name}</td>
                            <td>${order.delivery_address}</td>
                            <td>${order.total_price.toLocaleString()} FCFA</td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="openAssignModal(${order.id})">
                                    <i class="fas fa-eye me-1"></i>Détails & Action
                                </button>
                            </td>
                        </tr>
                    `).join('')}
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
        await apiCall(`/orders/${orderId}/status?status=Refusée`, 'PATCH');

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

async function loadLivreurOrders() {
    const container = document.getElementById('pendingOrders'); // In livreur.html
    if (!container) return;

    try {
        // Livreur calls /orders/ -> returns only assigned orders
        const orders = await apiCall('/orders/', 'GET');

        if (orders.length === 0) {
            container.innerHTML = '<div class="text-muted text-center">Aucune commande assignée.</div>';
            return;
        }

        container.innerHTML = orders.map(order => `
            <div class="card mb-3 border-${statusColor(order.status)}">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <h5 class="card-title">${order.order_number}</h5>
                        <span class="badge bg-${statusColor(order.status)}">${order.status}</span>
                    </div>
                    <div class="row mt-2">
                        <div class="col-md-6">
                            <p class="mb-1"><strong>Client:</strong> ${order.client_name}</p>
                            <p class="mb-1"><strong>Tél:</strong> ${order.phone}</p>
                            <p class="mb-1"><strong>Adresse:</strong> ${order.delivery_address}</p>
                        </div>
                        <div class="col-md-6 text-end">
                             <p class="h4 text-success">${order.total_price.toLocaleString()} FCFA</p>
                             <div class="mt-3 d-flex gap-2 justify-content-end">
                                <button class="btn btn-outline-primary btn-sm" onclick="copyToClipboard('${order.order_number}')">
                                    <i class="fas fa-copy"></i>
                                </button>
                                ${order.status === 'Validée' ? `
                                    <button class="btn btn-primary btn-sm" onclick="updateOrderStatus(${order.id}, 'En transit')">
                                        <i class="fas fa-truck me-1"></i>En route
                                    </button>
                                ` : ''}
                                ${order.status === 'En transit' ? `
                                    <button class="btn btn-success btn-sm" onclick="updateOrderStatus(${order.id}, 'Livré')">
                                        <i class="fas fa-check-circle me-1"></i>Livré
                                    </button>
                                ` : ''}
                             </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

    } catch (err) {
        container.innerHTML = `<div class="text-danger">Erreur: ${err.message}</div>`;
    }
}

async function updateOrderStatus(orderId, newStatus) {
    if (!await showConfirmModal('Mettre à jour Statut', `Confirmer le changement de statut à "${newStatus}" ?`, 'Valider', 'primary')) return;

    try {
        await apiCall(`/orders/${orderId}/status?status=${newStatus}`, 'PATCH');
        showToast('Statut mis à jour !', 'success');
        loadLivreurOrders();
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
        orderBtn.disabled = true;
    } else {
        orderItems.innerHTML = itemsHtml;
        orderBtn.disabled = false;
    }

    totalPriceElement.textContent = total.toLocaleString() + ' FCFA';
}

function initOrderForm() {
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        // Pré-remplir le username si connecté
        const storedUsername = sessionStorage.getItem('username');
        const usernameInput = document.getElementById('username');
        if (storedUsername && usernameInput) {
            usernameInput.value = storedUsername;
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

            const orderData = {
                order_number: 'CMD-' + Date.now(),
                client_name: document.getElementById('nom').value,
                phone: document.getElementById('telephone').value,
                delivery_address: document.getElementById('localisation').value,
                total_price: parseInt(document.getElementById('total-price').textContent.replace(/[^0-9]/g, '')),
                items: items
            };

            try {
                const result = await apiCall('/orders/', 'POST', orderData);
                showToast(`Commande ${result.order_number} enregistrée!`, 'success');
                orderForm.reset();
                cart = {};
                loadProducts(); // Refresh
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
// Commandes (Client)
// ==========================================

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
            ordersList.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">Vous n\'avez pas encore de commandes.</td></tr>';
        } else {
            ordersList.innerHTML = orders.map(order => `
                <tr>
                    <td>
                        <span class="fw-bold text-dark">${order.order_number}</span>
                    </td>
                    <td>${new Date(order.created_at).toLocaleDateString('fr-FR')}</td>
                    <td>${order.delivery_address || 'Lomé'}</td>
                    <td>
                        <span class="badge bg-${statusColor(order.status)}">${order.status}</span>
                    </td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary" onclick="showTracking('${order.order_number}')">
                            <i class="fas fa-eye me-1"></i> Suivre
                        </button>
                    </td>
                </tr>
            `).join('');
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

function init() {
    initAuthForm();
    initRegisterForm();
    initOrderForm();
    initLogout();
    initAddUserForm();

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
    }

    if (path.includes('catalogue.html')) {
        loadProducts();
    }

    // Client
    if (path.includes('client.html')) {
        loadClientOrders();
    }

    // Livreur
    if (path.includes('livreur.html')) {
        loadLivreurOrders();
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
// AI Features: Chat & Forecast
// ==========================================

async function initAIChat() {
    // Create Chatbot Wrapper
    const wrapper = document.createElement('div');
    wrapper.id = 'ai-chat-wrapper';

    // Create Button
    const chatBtn = document.createElement('button');
    chatBtn.id = 'chat-toggle-btn';
    chatBtn.className = 'shadow-lg';
    chatBtn.innerHTML = '<i class="fas fa-robot"></i>';
    // Append button properly
    wrapper.appendChild(chatBtn);

    // Create Chat Window
    const chatWindow = document.createElement('div');
    chatWindow.id = 'ai-chat-window';
    chatWindow.className = 'glass-panel';
    chatWindow.innerHTML = `
        <div class="chat-header">
            <span class="fw-bold"><i class="fas fa-leaf me-2"></i>Assistant ManiocAgri</span>
            <button class="btn btn-sm text-white" onclick="toggleChat()"><i class="fas fa-times"></i></button>
        </div>
        <div class="chat-body" id="chat-messages">
            <div class="chat-bubble bot">Bonjour ! Je suis l'IA ManiocAgri. Comment puis-je vous aider aujourd'hui ?</div>
        </div>
        <div class="typing-indicator" id="chat-typing">L'assistant réfléchit...</div>
        <div class="chat-footer">
            <input type="text" id="chat-input" class="form-control" placeholder="Posez votre question...">
            <button class="btn btn-success" id="send-chat-btn"><i class="fas fa-paper-plane"></i></button>
        </div>
    `;
    wrapper.appendChild(chatWindow);

    document.body.appendChild(wrapper);

    const toggleBtn = document.getElementById('chat-toggle-btn');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-chat-btn');

    toggleBtn.addEventListener('click', toggleChat);

    sendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
}

function toggleChat() {
    const window = document.getElementById('ai-chat-window');
    window.classList.toggle('active');
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');
    const typing = document.getElementById('chat-typing');
    const text = input.value.trim();

    if (!text) return;

    // Add user message
    messages.innerHTML += `<div class="chat-bubble user">${text}</div>`;
    input.value = '';
    messages.scrollTop = messages.scrollHeight;

    // Show typing
    typing.style.display = 'block';

    try {
        const data = await apiCall('/ai/chat', 'POST', { prompt: text });
        typing.style.display = 'none';
        messages.innerHTML += `<div class="chat-bubble bot">${data.response}</div>`;
        messages.scrollTop = messages.scrollHeight;
    } catch (err) {
        typing.style.display = 'none';
        messages.innerHTML += `<div class="chat-bubble bot" style="background: #fff3cd; color: #856404;">😔 Désolé, je ne peux pas répondre pour le moment. Veuillez réessayer dans quelques instants.</div>`;
    }
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


document.addEventListener('DOMContentLoaded', () => {
    init();
    initAIChat();
});
