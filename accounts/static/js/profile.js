/**
 * Profile photo preview and removal interactions
 */
document.addEventListener('DOMContentLoaded', function () {
  const input       = document.querySelector('input[type="file"][name="photo"]');
  const preview     = document.getElementById('avatar-preview');
  const removeBtn   = document.getElementById('avatar-remove');
  const clearBox    = document.getElementById('photo-clear');

  if (!input || !preview) return;

  const placeholder = preview.dataset.placeholder;

  // Live preview on file select
  input.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) return;

    if (file.size > 2 * 1024 * 1024) {
      alert('Photo must be under 2 MB.');
      this.value = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src = e.target.result;
      if (clearBox) clearBox.checked = false;
      if (removeBtn) removeBtn.style.display = 'inline';
    };
    reader.readAsDataURL(file);
  });

  // Remove — revert to placeholder and flag for deletion
  if (removeBtn) {
    removeBtn.addEventListener('click', function () {
      preview.src = placeholder;
      input.value = '';
      if (clearBox) clearBox.checked = true;
      this.style.display = 'none';
    });
  }
});
