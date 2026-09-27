from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError
from django.test import Client, TestCase
from django.utils import timezone

from .models import StudentProfile, Education, FamilyMember, CVVersion, AuditEvent, Notification
from .services import submit_cv, review_cv


class SubmissionTests(TestCase):
    url = '/student/cv/tinjau/'
    headers = {'HTTP_ACCEPT': 'application/json', 'HTTP_X_REQUESTED_WITH': 'cv-submit'}

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('submission@example.test', password='Submit-Test-986!')
        cls.other = User.objects.create_user('other-submit@example.test', password='Submit-Test-986!')
        cls.admin = User.objects.create_user('submit-admin@example.test', password='Submit-Test-986!', is_staff=True)
        cls.p = cls.make_profile(cls.owner)
        cls.p2 = cls.make_profile(cls.other)

    @staticmethod
    def make_profile(user):
        p = StudentProfile.objects.create(
            user=user, full_name='Siswa Sintetis Pengajuan', gender='M',
            birth_date=date(2001, 1, 1), birth_place='Brebes', address='Alamat uji',
            phone='081234567890', marital_status='SINGLE', height=170, weight=60,
            smoking=False, alcohol=False, tattoo=False, passport=False,
            study_months=0, japanese_certificate='Tidak ada', strengths='Disiplin',
            weaknesses='Masih belajar', hobbies='Membaca',
        )
        Education.objects.create(student=p, start_date=date(2016, 7, 1), level='SMA', institution='Sekolah Uji')
        FamilyMember.objects.create(student=p, name='Keluarga Uji', relationship='Ayah', age=50, occupation='Usaha')
        return p

    def setUp(self):
        self.client.force_login(self.owner)

    def post(self, **changes):
        payload = {'confirm': 'yes', 'revision': 0}
        payload.update(changes)
        return self.client.post(self.url, payload, **self.headers)

    def assert_no_submission(self):
        self.p.refresh_from_db()
        self.assertEqual(self.p.status, 'DRAFT')
        self.assertIsNone(self.p.submitted_at)
        self.assertIsNone(self.p.submitted_version_id)
        self.assertFalse(self.p.versions.exists())

    def test_a_incomplete_unchecked(self):
        self.p.phone = ''; self.p.save()
        r = self.post(confirm='')
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json()['code'], 'confirmation')
        self.assert_no_submission()

    def test_b_incomplete_checked_exact_links(self):
        self.p.phone = ''; self.p.save()
        self.p.educations.all().delete()
        r = self.post()
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json()['code'], 'incomplete')
        self.assertEqual(r.json()['missing'], [
            {'label': 'Nomor telepon', 'url': '/student/cv/identitas/'},
            {'label': 'Riwayat pendidikan', 'url': '/student/cv/pendidikan/'},
        ])
        self.assertContains(self.client.get(self.url), 'Lengkapi 2 data berikut')
        self.assert_no_submission()

    def test_c_complete_unchecked_rejected_server_side(self):
        self.assertEqual(self.post(confirm='').status_code, 422)
        self.assert_no_submission()

    def test_d_success_real_owner_timestamp_snapshot_audit(self):
        r = self.post()
        self.assertEqual(r.status_code, 200)
        self.p.refresh_from_db()
        self.assertTrue(r.json()['ok'])
        self.assertEqual(self.p.status, 'SUBMITTED')
        self.assertTrue(timezone.is_aware(self.p.submitted_at))
        self.assertEqual(r.json()['submitted_at'], self.p.submitted_at.isoformat())
        self.assertEqual(self.p.submitted_version_id, r.json()['version_id'])
        self.assertEqual(self.p.submitted_version.student_id, self.p.pk)
        self.assertEqual(self.p.submitted_version.data['phone'], '081234567890')
        self.assertEqual(AuditEvent.objects.filter(action='CV_SUBMITTED', actor=self.owner).count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.admin).count(), 1)

    def test_e_duplicate_only_one_submission(self):
        first = self.post()
        self.assertEqual(first.status_code, 200)
        for revision in [0, 1]:
            r = self.post(revision=revision)
            self.assertEqual(r.status_code, 409)
            self.assertEqual(r.json()['code'], 'already_submitted')
        self.assertEqual(self.p.versions.count(), 1)
        self.assertEqual(AuditEvent.objects.filter(action='CV_SUBMITTED').count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.admin).count(), 1)

    def test_l_lost_success_response_then_retry_preserves_identity(self):
        # The server commits; simulate the caller discarding the response.
        self.post()
        self.p.refresh_from_db()
        identity = (self.p.submitted_at, self.p.submitted_version_id, self.p.revision)
        retry = self.post()
        self.assertEqual(retry.status_code, 409)
        self.assertEqual(retry.json()['code'], 'already_submitted')
        self.p.refresh_from_db()
        self.assertEqual((self.p.submitted_at, self.p.submitted_version_id, self.p.revision), identity)
        self.assertEqual(self.p.versions.count(), 1)
        self.assertEqual(AuditEvent.objects.filter(action='CV_SUBMITTED').count(), 1)
        self.assertContains(self.client.get(self.url), 'CV berhasil diajukan ke LPK.')

    def test_f_refresh_reads_persisted_submission(self):
        self.post()
        r = self.client.get(self.url)
        self.assertContains(r, 'CV berhasil diajukan ke LPK.')
        self.assertContains(r, 'CV versi 1')
        self.assertNotContains(r, 'id="cv-submit-form"')
        self.assertContains(self.client.get('/student/'), 'Diajukan:')

    def test_g_logout_login_preserves_submission(self):
        self.post(); self.client.post('/keluar/')
        self.assertTrue(self.client.login(username=self.owner.username, password='Submit-Test-986!'))
        self.assertContains(self.client.get(self.url), 'CV berhasil diajukan ke LPK.')
        self.assertEqual(self.p.versions.count(), 1)

    def test_h_supplied_student_id_cannot_select_another_owner(self):
        r = self.post(student_id=self.p2.pk, status='VERIFIED', submitted_version=self.p2.pk)
        self.assertEqual(r.status_code, 200)
        self.p2.refresh_from_db()
        self.assertEqual(self.p2.status, 'DRAFT')
        self.assertFalse(self.p2.versions.exists())
        with self.assertRaises(PermissionDenied):
            submit_cv(self.p2, self.owner, 0)

    def test_i_guest_and_admin_rejected(self):
        self.client.logout()
        self.assertEqual(self.post().status_code, 401)
        self.client.force_login(self.admin)
        self.assertEqual(self.post().status_code, 403)
        self.assert_no_submission()

    def test_j_admin_sees_same_submission_reference(self):
        self.post()
        self.client.force_login(self.admin)
        self.assertContains(self.client.get('/admin/'), self.p.full_name)
        r = self.client.get(f'/admin/siswa/{self.p.pk}/')
        self.assertContains(r, 'Diajukan:')
        self.assertContains(r, 'CV versi 1')
        self.assertContains(r, 'Diajukan')

    def test_k_database_failure_rolls_back_everything(self):
        with self.assertLogs('core.views', level='ERROR'), patch('core.services.audit', side_effect=DatabaseError('simulated write failure')):
            r = self.post()
        self.assertEqual(r.status_code, 503)
        self.assertFalse(r.json()['ok'])
        self.assertNotIn('simulated', r.content.decode())
        self.assert_no_submission()
        self.assertFalse(Notification.objects.exists())
        self.assertEqual(self.post().status_code, 200)

    def test_unexpected_server_failure_has_no_success(self):
        with self.assertLogs('core.views', level='ERROR'), patch('core.views.submit_cv', side_effect=RuntimeError('private details')):
            r = self.post()
        self.assertEqual(r.status_code, 503)
        self.assertNotIn('private details', r.content.decode())
        self.assert_no_submission()

    def test_csrf_rejected_with_structured_response(self):
        c = Client(enforce_csrf_checks=True); c.force_login(self.owner)
        r = c.post(self.url, {'confirm': 'yes', 'revision': 0}, **self.headers)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.json()['code'], 'csrf')
        self.assert_no_submission()

    def test_stale_and_invalid_revision(self):
        for revision in [100, 'invalid']:
            self.assertEqual(self.post(revision=revision).status_code, 409)
            self.assert_no_submission()

    def test_snapshot_survives_revision_and_resubmission(self):
        self.post(); self.p.refresh_from_db()
        old_id = self.p.submitted_version_id
        old_data = self.p.submitted_version.data
        review_cv(self.p, self.admin, {'revision': self.p.revision, 'status': 'NEEDS_REVISION', 'note': 'Perbarui alamat'})
        self.p.refresh_from_db(); self.p.address = 'Alamat revisi'; self.p.save()
        r = self.post(revision=self.p.revision)
        self.assertEqual(r.status_code, 200)
        self.p.refresh_from_db()
        self.assertNotEqual(self.p.submitted_version_id, old_id)
        self.assertEqual(CVVersion.objects.get(pk=old_id).data, old_data)
        self.assertEqual(self.p.submitted_version.data['address'], 'Alamat revisi')

    def test_native_post_fallback_and_edit_lock(self):
        r = self.client.post(self.url, {'confirm': 'yes', 'revision': 0})
        self.assertRedirects(r, '/student/')
        self.p.refresh_from_db()
        before = self.p.address
        self.client.post('/student/cv/identitas/', {'revision': self.p.revision, 'full_name': self.p.full_name, 'address': 'Should not change'})
        self.p.refresh_from_db()
        self.assertEqual(self.p.address, before)

    def test_legacy_backfill_uses_existing_audit_not_current_time(self):
        import importlib
        from types import SimpleNamespace
        from django.apps import apps
        from django.db import connection
        v = CVVersion.objects.create(student=self.p, number=1, data={'full_name': self.p.full_name}, actor=self.owner)
        event = AuditEvent.objects.create(actor=self.owner, action='CV_SUBMITTED', entity='StudentProfile', entity_id=str(self.p.pk), metadata={'version': 1})
        migration = importlib.import_module('core.migrations.0003_backfill_submission_reference')
        migration.backfill(apps, SimpleNamespace(connection=connection))
        self.p.refresh_from_db(); self.p2.refresh_from_db()
        self.assertEqual(self.p.submitted_at, event.created_at)
        self.assertEqual(self.p.submitted_version_id, v.pk)
        self.assertIsNone(self.p2.submitted_at)
