/* ===========================================================
   Lab Inventory Management Tool – Main JavaScript
   Handles Lock/Unlock toggle via AJAX
   =========================================================== */

/**
 * Toggle the lock status of an inventory item.
 * Called when the user clicks the 🔒 / 🔓 button.
 */
async function toggleLock(button) {
    const cupboardId = button.dataset.cupboardId;
    const itemId     = button.dataset.itemId;
    const isLocked   = button.dataset.locked === 'true';

    const action = isLocked ? 'BORROW (unlock)' : 'RETURN (lock)';

    if (!confirm(`Are you sure you want to ${action} this item?`)) {
        return;
    }

    // Show spinner while processing
    button.disabled = true;
    const originalHTML = button.innerHTML;
    button.innerHTML =
        '<span class="spinner-border spinner-border-sm"></span>';

    try {
        const response = await fetch('/api/toggle-lock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cupboard_id: parseInt(cupboardId, 10),
                item_id: itemId,
            }),
        });

        const data = await response.json();

        if (data.success) {
            // Show success toast
            const toastType =
                data.action === 'locked' ? 'success' : 'warning';
            showToast('Success', data.message, toastType);

            if (!data.email_sent) {
                showToast(
                    'Email Notice',
                    'Email could not be sent. Check SMTP configuration.',
                    'warning',
                );
            }

            // Reload after a short delay so the user sees the toast
            setTimeout(() => location.reload(), 1200);
        } else {
            showToast('Error', data.message, 'danger');
            button.disabled = false;
            button.innerHTML = originalHTML;
        }
    } catch (err) {
        showToast('Error', 'Something went wrong. Please try again.', 'danger');
        button.disabled = false;
        button.innerHTML = originalHTML;
    }
}

/**
 * Display a Bootstrap toast notification.
 */
function showToast(title, message, type) {
    const toastEl = document.getElementById('notificationToast');
    if (!toastEl) return;

    document.getElementById('toastTitle').textContent   = title;
    document.getElementById('toastMessage').textContent = message;

    // Apply border colour
    toastEl.className = 'toast border-' + (type || 'primary');

    const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
    toast.show();
}
