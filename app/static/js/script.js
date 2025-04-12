// 알림 메시지 자동 숨김
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 3000);
    });
});

// 삭제 버튼 확인
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn-outline-danger')) {
        if (!confirm('정말 삭제하시겠습니까?')) {
            e.preventDefault();
        }
    }
}); 