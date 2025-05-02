function createModalTable(data) {
    // Xóa modal cũ nếu có
    const oldModal = document.getElementById('sql-modal-overlay');
    if (oldModal) oldModal.remove();

    // Tạo overlay
    const overlay = document.createElement('div');
    overlay.id = 'sql-modal-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = 0;
    overlay.style.left = 0;
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.background = 'rgba(0,0,0,0.5)';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.zIndex = 9999;

    // Tạo modal
    const modal = document.createElement('div');
    modal.style.background = '#fff';
    modal.style.width = '70vw';
    modal.style.maxHeight = '70vh';
    modal.style.overflow = 'auto';
    modal.style.borderRadius = '10px';
    modal.style.boxShadow = '0 2px 16px rgba(0,0,0,0.3)';
    modal.style.padding = '24px';
    modal.style.position = 'relative';

    // Nếu không có dữ liệu
    if (!Array.isArray(data) || data.length === 0) {
        modal.innerHTML = '<p>Không có dữ liệu trả về.</p>';
    } else {
        // Tạo bảng
        const table = document.createElement('table');
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.marginBottom = '8px';

        // Header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        Object.keys(data[0]).forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            th.style.border = '1px solid #ccc';
            th.style.padding = '8px';
            th.style.background = '#f5f5f5';
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Body
        const tbody = document.createElement('tbody');
        data.forEach(row => {
            const tr = document.createElement('tr');
            Object.values(row).forEach(val => {
                const td = document.createElement('td');
                td.textContent = val;
                td.style.border = '1px solid #ccc';
                td.style.padding = '8px';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        modal.appendChild(table);
    }

    // Đóng modal khi click ngoài
    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) overlay.remove();
    });

    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

document.addEventListener('DOMContentLoaded', function () {
    const m2 = document.querySelector('.m2');
    const textarea = document.querySelector('.code-textarea');

    m2.addEventListener('click', async function () {
        const sql = textarea.value.trim();
        if (!sql) {
            alert('Vui lòng nhập câu lệnh SQL!');
            return;
        }
        try {
            const res = await fetch('/exec-sql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sql })
            });
            const data = await res.json();
            if (res.ok && data.result) {
                createModalTable(data.result);
            } else {
                alert('Lỗi: ' + (data.error || 'Câu lệnh SQL không hợp lệ!'));
            }
        } catch (err) {
            alert('Lỗi kết nối server!');
        }
    });
});