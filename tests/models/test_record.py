from mock import patch

from pycloudflare.models import Record, User
from tests.models import FakedServiceTestCase


class TestCreateRecord(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')
        self.record = self.zone.create_record(
            'bar.example.com', 'A', '127.0.0.1')

    def test_returns_record_object(self):
        self.assertIsInstance(self.record, Record)

    def test_has_id_attribute(self):
        self.assertIsInstance(self.record.id, basestring)

    def test_has_type_attribute(self):
        self.assertEqual(self.record.type, 'A')

    def test_has_name_attribute(self):
        self.assertEqual(self.record.name, 'bar.example.com')

    def test_has_content_attribute(self):
        self.assertEqual(self.record.content, '127.0.0.1')

    def test_has_proxiable_attribute(self):
        self.assertEqual(self.record.proxiable, True)

    def test_has_proxied_attribute(self):
        self.assertEqual(self.record.proxied, False)

    def test_has_ttl_attribute(self):
        self.assertEqual(self.record.ttl, 1)

    def test_has_locked_attribute(self):
        self.assertEqual(self.record.locked, False)

    def test_has_data_attribute(self):
        self.assertEqual(self.record.data, {})

    def test_invalidates_zone_records(self):
        self.assertNotIn('baz.example.com', self.zone.records)
        self.zone.create_record('baz.example.com', 'A', '127.0.0.1')
        self.assertIn('baz.example.com', self.zone.records)
        self.zone.create_record('baz.example.com', 'A', '127.0.0.2')
        self.assertEqual(len(self.zone.records['baz.example.com']), 2)


class TestCreateMXRecord(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')

    def test_fails_without_priority(self):
        with self.assertRaises(Exception):
            self.zone.create_record('bar.example.com', 'MX', 'mail.net')

    def test_successeds_with_priority(self):
        record = self.zone.create_record('bar.example.com', 'MX', 'mail.net',
                                         priority=10)
        self.assertEqual(record.priority, 10)


class TestDeleteRecord(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')
        self.record = self.zone.records['example.com'][0]

    def test_can_delete(self):
        self.record.delete()
        self.assertEqual(self.zone.records, {})


class TestUpdateRecord(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')
        self.record = self.zone.records['example.com'][0]

    def test_updates_on_set(self):
        self.record.proxied = True
        self.assertEqual(self.record.proxied, True)

    def test_updates_record_on_set(self):
        with patch.object(self.record.service, 'update_dns_record'):
            self.record.proxied = True
            self.record.service.update_dns_record.assert_called_with(
                self.zone.id, self.record.id, {'proxied': True})

    def test_invalidates_zone_records_on_rename(self):
        self.assertNotIn('quux.example.com', self.zone.records)
        self.record.name = 'quux.example.com'
        self.assertIn('quux.example.com', self.zone.records)
