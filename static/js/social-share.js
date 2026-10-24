document.querySelectorAll('[data-copy-share]').forEach((button) => {
  button.addEventListener('click', async () => {
    const status = document.querySelector('.share-feedback');
    const shareUrl = button.dataset.copyUrl;
    try {
      await navigator.clipboard.writeText(shareUrl);
    } catch (error) {
      const temporary = document.createElement('textarea');
      temporary.value = shareUrl;
      temporary.setAttribute('readonly', '');
      temporary.style.position = 'fixed';
      temporary.style.opacity = '0';
      document.body.appendChild(temporary);
      temporary.select();
      const copied = document.execCommand('copy');
      temporary.remove();
      if (!copied) {
        status.textContent = 'Không thể sao chép tự động. Hãy sao chép địa chỉ trang trên trình duyệt.';
        return;
      }
    }
    status.textContent = 'Đã sao chép liên kết sản phẩm.';
  });
});
