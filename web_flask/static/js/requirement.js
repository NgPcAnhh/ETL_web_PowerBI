document.addEventListener('DOMContentLoaded', function () {
const form = document.querySelector('form.container');
form.addEventListener('submit', async function (event) {
    event.preventDefault();

    // Lấy input
    const inputs = form.querySelectorAll('.input-is');
    const gmail = inputs[0].value;
    const discussion = inputs[1].value;

    // Lấy id từ session (giả sử lưu trong sessionStorage)
    const id = sessionStorage.getItem('id'); // hoặc lấy từ cookie, localStorage tùy bạn lưu ở đâu

    // Lấy thời gian realtime
    const time = new Date().toISOString();

    // Tạo object dữ liệu
    const data = {
    gmail: gmail,
    discussion: discussion,
    time: time
    };

    try {
    const response = await fetch('/api/submit-requirement', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    credentials: 'same-origin' // hoặc 'include'
});

    if (response.ok) {
        alert('Gửi thành công!');
        form.reset();
    } else {
        alert('Có lỗi xảy ra, vui lòng thử lại!');
    }
    } catch (error) {
    alert('Lỗi mạng hoặc backend không phản hồi!');
    }
});
});