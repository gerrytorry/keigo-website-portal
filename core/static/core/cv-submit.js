/* One confirmed checkbox -> one authenticated request. Native POST remains a fallback. */
'use strict';
(() => {
  const form = document.querySelector('#cv-submit-form');
  if (!form) return;
  const button = form.querySelector('button[type=submit]');
  const confirmation = form.querySelector('[name=confirm]');
  const feedback = document.querySelector('#submission-feedback');
  let busy = false, submitted = false;
  const update = () => { button.disabled = busy || submitted || !confirmation.checked || form.dataset.complete !== 'true'; };
  const link = (label, href) => {
    const a = document.createElement('a'); a.textContent = label; a.href = href;
    feedback.append(document.createTextNode(' '), a);
  };
  const show = (message, isError) => {
    feedback.hidden = false;
    feedback.setAttribute('role', isError ? 'alert' : 'status');
    feedback.textContent = message;
    feedback.focus();
  };
  confirmation.addEventListener('change', update);
  update();
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || submitted) return;
    if (!confirmation.checked || !form.reportValidity()) {
      show('Centang pernyataan bahwa data CV sudah diperiksa.', true); return;
    }
    if (form.dataset.complete !== 'true') {
      show('CV belum lengkap. Periksa daftar data yang perlu dilengkapi di atas.', true); return;
    }
    busy = true; update(); form.setAttribute('aria-busy', 'true');
    button.textContent = 'Mengajukan CV...';
    feedback.hidden = false; feedback.textContent = 'Mengirim dan menyimpan pengajuan ke LPK...';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const response = await fetch(form.action, {
        method: 'POST', body: new FormData(form), credentials: 'same-origin',
        headers: {'Accept': 'application/json', 'X-Requested-With': 'cv-submit'},
        signal: controller.signal
      });
      if (!response.headers.get('content-type')?.includes('application/json')) {
        show(response.redirected ? 'Sesi berakhir. Masuk kembali untuk mengajukan CV.' : 'Server belum dapat mengonfirmasi pengajuan. Periksa status sebelum mencoba lagi.', true);
        link('Masuk kembali', '/masuk/'); link('Periksa dashboard', '/student/'); return;
      }
      const result = await response.json();
      if (!response.ok || result.ok !== true) {
        show(result.error || 'Pengajuan belum berhasil. Silakan coba lagi.', true);
        if (result.missing?.length) {
          const list = document.createElement('ul');
          result.missing.forEach(item => {
            const li = document.createElement('li'), a = document.createElement('a');
            a.textContent = item.label; a.href = item.url; li.append(a); list.append(li);
          });
          feedback.append(list);
        }
        if (result.code === 'authentication') link('Masuk kembali', '/masuk/');
        if (result.code === 'csrf' || result.code === 'conflict') link('Muat ulang tinjauan', form.action);
        link('Periksa dashboard', '/student/'); return;
      }
      submitted = true; confirmation.disabled = true;
      const when = new Intl.DateTimeFormat('id-ID', {dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Jakarta'}).format(new Date(result.submitted_at));
      show('CV berhasil diajukan ke LPK. Terkirim pada: ' + when + ' WIB · CV versi ' + result.version + '. Tunggu pemeriksaan admin.', false);
      link('Lihat status di dashboard →', '/student/');
    } catch (_) {
      show('Koneksi terputus atau respons belum diterima. Status pengajuan belum dapat dipastikan. Periksa dashboard sebelum mencoba lagi; data CV tetap tersimpan.', true);
      link('Periksa dashboard', '/student/');
    } finally {
      clearTimeout(timeout); busy = false; form.setAttribute('aria-busy','false');
      button.textContent = submitted ? 'CV berhasil diajukan' : 'Ajukan CV ke LPK →';
      update();
    }
  });
})();
