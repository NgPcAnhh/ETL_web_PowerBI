function showAccessDenied(message) {
    let warningDiv = document.getElementById('access-warning');
    if (!warningDiv) {
        warningDiv = document.createElement('div');
        warningDiv.id = 'access-warning';
        warningDiv.style.position = 'fixed';
        warningDiv.style.top = '40px';
        warningDiv.style.left = '50%';
        warningDiv.style.transform = 'translateX(-50%)';
        warningDiv.style.background = '#e53935';
        warningDiv.style.color = '#fff';
        warningDiv.style.fontWeight = 'bold';
        warningDiv.style.textAlign = 'center';
        warningDiv.style.padding = '16px 32px';
        warningDiv.style.borderRadius = '8px';
        warningDiv.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
        warningDiv.style.zIndex = '9999';
        document.body.appendChild(warningDiv);
    }
    warningDiv.textContent = message;
    warningDiv.style.display = 'block';
    setTimeout(() => {
        warningDiv.style.display = 'none';
    }, 3000);
}

document.addEventListener('DOMContentLoaded', async function() {
    // Gọi API lấy thông tin user
    const res = await fetch('/api/userinfo', { credentials: 'same-origin' });
    if (!res.ok) return;
    const data = await res.json();

    // Xử lý idusers thành dạng xxxx xxxx xxxx xxxx
    function pad4(num) {
        return num.toString().padStart(4, '0');
    }
    function random4() {
        return Math.floor(1000 + Math.random() * 9000).toString();
    }
    const idStr = `${random4()} ${random4()} ${random4()} ${pad4(data.idusers)}`;

    // Xử lý status
    let statusText = 'non-vip';
    if (data.status === 0) statusText = 'pro investor';
    else if (data.status === 1) statusText = 'pro max investor';

    // Đẩy dữ liệu lên giao diện
    document.querySelector('.number').textContent = idStr;
    document.querySelector('.name').textContent = data.username;
    document.querySelector('.valid_thru').textContent = statusText;
    document.querySelector('.date_8264').textContent = '1 2 / 2 6';

    // Lưu status lại để dùng cho sự kiện click
    window.userStatus = data.status;
});

// Xử lý sự kiện cho các card
document.querySelector('.card.red').addEventListener('click', function(e) {
    if (window.userStatus === 1) {
        window.location.href = '/premiumreport';
    } else {
        showAccessDenied('Bạn không có quyền truy cập báo cáo cơ bản! Vui lòng mua gói để truy cập');
    }
});

document.querySelector('.card.blue').addEventListener('click', function(e) {
    if (window.userStatus === 0 || window.userStatus === 1) {
        window.location.href = '/freereport';
    } else {
        showAccessDenied('Bạn không có quyền truy cập báo cáo nâng cao! Vui lòng mua gói để truy cập');
    }
});

document.querySelector('.card.green').addEventListener('click', function(e) {
    window.location.href = '/purchase';
});
