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
    // Get DOM elements
    const m2 = document.querySelector('.m2');
    const textarea = document.querySelector('.code-textarea');

    if (!m2 || !textarea) {
        console.error('Required elements not found');
        return;
    }

    m2.addEventListener('click', async function () {
        // Get the input value
        const input = textarea.value.trim();
        
        if (!input) {
            alert('Vui lòng nhập lệnh!');
            return;
        }

        // SQL command handling
        if (input.toLowerCase().startsWith('/sql')) {
            // Handle SQL commands
            const sqlQuery = input.substring(4).trim();
            
            if (!sqlQuery) {
                alert('Vui lòng nhập câu lệnh SQL sau /sql!');
                return;
            }

            try {
                const res = await fetch('/exec-sql', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sql: sqlQuery })
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
            return;
        }

        // Admin command handling
        if (input.toLowerCase().startsWith('/admin')) {
            const adminCommand = input.substring(7).trim().toLowerCase();
            
            // Logout command
            if (adminCommand === 'log out' || adminCommand === 'logout') {
                try {
                    const res = await fetch('/logout', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    if (res.ok) {
                        window.location.href = '/login';
                    } else {
                        alert('Không thể đăng xuất!');
                    }
                } catch (err) {
                    alert('Lỗi kết nối server!');
                }
                return;
            }
            
            // Crawl command
            if (adminCommand.startsWith('crawl')) {
                const crawlParam = adminCommand.substring(6).trim();
                
                if (crawlParam.length !== 3) {
                    alert('Tham số sau "crawl" phải là một từ có đúng 3 ký tự!');
                    return;
                }

                // Create modal first with loading message
                const processContent = createProcessModal(`Crawling data for ${crawlParam}`, 'Starting crawl process...\n');
                
                try {
                    console.log('Sending crawl request for:', crawlParam);
                    const res = await fetch('/admin-crawl', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command: `crawl ${crawlParam}` })
                    });
                    
                    const data = await res.json();
                    console.log('Crawl response:', data);
                    
                    if (res.ok) {
                        processContent.textContent += data.output || 'No output provided';
                        processContent.textContent += '\n\nCrawling completed successfully!';
                    } else {
                        processContent.textContent += `\nError: ${data.error || 'Unknown error occurred'}`;
                    }
                } catch (err) {
                    console.error('Crawl fetch error:', err);
                    processContent.textContent += `\nConnection error: ${err.message}`;
                }
                return;
            }

            // Clean command
            if (adminCommand.startsWith('clean')) {
                const cleanParam = adminCommand.substring(6).trim();
                if (cleanParam.length !== 3) {
                    showNotification('Tham số sau "clean" phải là một từ có đúng 3 ký tự!', 'error');
                    return;
                }
                showLoader('Đang xử lý clean dữ liệu...');
                try {
                    const res = await fetch('/admin-clean', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command: `clean ${cleanParam}` })
                    });
                    hideLoader();
                    if (res.ok) {
                        showNotification('Clean thành công và lưu vào folder.', 'success');
                    } else {
                        const data = await res.json();
                        showNotification('Không thể thực hiện clean! ' + (data.error || ''), 'error');
                    }
                } catch (err) {
                    hideLoader();
                    showNotification('Lỗi kết nối server!', 'error');
                }
                return;
            }
            

            if (adminCommand.startsWith("download folder")) {
                let macp = adminCommand.substring("download folder".length).trim();
                if (!macp || macp.length !== 3) {
                    showNotification('Vui lòng nhập đúng mã cp (3 ký tự) sau "download folder"', 'error');
                    return;
                }
                showLoader('Đang chuẩn bị file zip...');
                try {
                    const res = await fetch('/api/download-csv-folder', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ macp })
                    });
                    hideLoader();
                    if (res.ok) {
                        const blob = await res.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${macp}_csv_files.zip`;
                        document.body.appendChild(a);
                        a.click();
                        setTimeout(() => {
                            window.URL.revokeObjectURL(url);
                            a.remove();
                        }, 1000);
                        showNotification('Đã tải về file zip!', 'success');
                    } else {
                        const data = await res.json();
                        showNotification('Không thể tải về! ' + (data.error || ''), 'error');
                    }
                } catch (err) {
                    hideLoader();
                    showNotification('Lỗi kết nối server!', 'error');
                }
                return;
            }
            
            // Hiển thị gợi ý nếu gõ /admin suggest
            if (input.trim().toLowerCase() === '/admin suggest') {
                // Find the textarea element
                const textarea = document.querySelector('.code-textarea');
                if (!textarea) {
                    console.error('code-textarea element not found');
                    return;
                }
                // Set the suggestion text directly in the textarea, below the command
                textarea.value = `/admin suggest
---các lệnh admin---
/sql +  sql query __thực hiện query từ csdl
/admin + crawl + {ssmã cổ phiếu} : crawl dữ liệu của báo cáo tài chính theo mã cổ phiếu
/admin + clean + {mã cổ phiếu}: làm sạch data, sắp xếp những data cần thiết 
/admin + download folder +{mã cổ phiếu}: tải về thư mục data sử dụng làm báo cáo. 
/admin + log out: để đăng xuất tài khoản của admin 
/admin + suggest: để hiển thị các gợi ý 
--------end---------              `;
                // Move cursor to end for editing
                textarea.focus();
                textarea.setSelectionRange(textarea.value.length, textarea.value.length);
                return;
            }


            // No valid admin command found
            alert('Lệnh admin không hợp lệ!');
            return;
        }

        // If we get here, no valid command was found
        alert('Lệnh không hợp lệ! Hãy dùng /sql hoặc /admin');
    });
});

// theo dõi quá trình crawl 
function createProcessModal(title, processOutput) {
    // Xóa modal cũ nếu có
    const oldModal = document.getElementById('process-modal-overlay');
    if (oldModal) oldModal.remove();

    // Tạo overlay
    const overlay = document.createElement('div');
    overlay.id = 'process-modal-overlay';
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
    modal.style.background = '#000';
    modal.style.color = '#33FF33';
    modal.style.width = '70vw';
    modal.style.maxHeight = '70vh';
    modal.style.overflow = 'auto';
    modal.style.borderRadius = '10px';
    modal.style.boxShadow = '0 2px 16px rgba(0,0,0,0.3)';
    modal.style.padding = '24px';
    modal.style.fontFamily = 'monospace';
    modal.style.position = 'relative';

    // Header
    const header = document.createElement('div');
    header.style.borderBottom = '1px solid #33FF33';
    header.style.paddingBottom = '10px';
    header.style.marginBottom = '15px';
    header.style.fontSize = '18px';
    header.textContent = title;
    modal.appendChild(header);

    // Content
    const content = document.createElement('pre');
    content.style.margin = 0;
    content.style.whiteSpace = 'pre-wrap';
    content.textContent = processOutput;
    modal.appendChild(content);
    
    // Close button
    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'Close';
    closeBtn.style.marginTop = '15px';
    closeBtn.style.background = '#333';
    closeBtn.style.color = '#fff';
    closeBtn.style.border = '1px solid #33FF33';
    closeBtn.style.padding = '8px 16px';
    closeBtn.style.borderRadius = '4px';
    closeBtn.style.cursor = 'pointer';
    closeBtn.onclick = () => overlay.remove();
    modal.appendChild(closeBtn);

    // Đóng modal khi click ngoài
    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) overlay.remove();
    });

    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    return content; // Return the content element for potential updates
}


// xử lý hiển thị cho clean data 
function showNotification(message, type = 'info') {
    // Xóa notification cũ nếu có
    const old = document.getElementById('custom-notification');
    if (old) old.remove();

    const notif = document.createElement('div');
    notif.id = 'custom-notification';
    notif.style.position = 'fixed';
    notif.style.top = '30px';
    notif.style.right = '30px';
    notif.style.zIndex = 10000;
    notif.style.padding = '18px 32px';
    notif.style.borderRadius = '8px';
    notif.style.background = type === 'success' ? '#4caf50' : (type === 'error' ? '#f44336' : '#2196f3');
    notif.style.color = '#fff';
    notif.style.fontSize = '16px';
    notif.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
    notif.textContent = message;
    document.body.appendChild(notif);
    setTimeout(() => notif.remove(), 3500);
}

// xử lý đang xử lý 
function showLoader(message = "Đang xử lý...") {
    // Xóa loader cũ nếu có
    const old = document.getElementById('custom-loader');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'custom-loader';
    overlay.style.position = 'fixed';
    overlay.style.top = 0;
    overlay.style.left = 0;
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.background = 'rgba(0,0,0,0.3)';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.zIndex = 10001;

    const box = document.createElement('div');
    box.style.background = '#fff';
    box.style.padding = '32px 48px';
    box.style.borderRadius = '12px';
    box.style.display = 'flex';
    box.style.flexDirection = 'column';
    box.style.alignItems = 'center';

    // Loader spinner
    const spinner = document.createElement('div');
    spinner.style.border = '6px solid #eee';
    spinner.style.borderTop = '6px solid #2196f3';
    spinner.style.borderRadius = '50%';
    spinner.style.width = '48px';
    spinner.style.height = '48px';
    spinner.style.animation = 'spin 1s linear infinite';
    box.appendChild(spinner);

    // Keyframes for spinner
    const style = document.createElement('style');
    style.innerHTML = `@keyframes spin { 100% { transform: rotate(360deg); } }`;
    document.head.appendChild(style);

    // Message
    const msg = document.createElement('div');
    msg.style.marginTop = '18px';
    msg.style.fontSize = '18px';
    msg.style.color = '#333';
    msg.textContent = message;
    box.appendChild(msg);

    overlay.appendChild(box);
    document.body.appendChild(overlay);
}

function hideLoader() {
    const old = document.getElementById('custom-loader');
    if (old) old.remove();
}





