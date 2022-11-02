
from unittest import TestCase
from unittest.case import TestCase
from unittest import main
from requests import HTTPError, Response, request

from FileStorageConnector import FileConnector, Metadata


class EmptyStorageTest(TestCase):
    """Тестирование при пустом наполнении сервера"""

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.fsc = FileConnector('http://127.0.0.1:9876')

    def setUp(self) -> None:
        result = self.fsc.get_without_params()['content']
        for elem in result:
            self.fsc.delete_by_id(elem['id'])

    def tearDown(self) -> None:
        result = self.fsc.get_without_params()['content']
        for elem in result:
            self.fsc.delete_by_id(elem['id'])

    def test_get_without_params(self):
        result = self.fsc.get_without_params()
        content, code = result['content'], result['status-code']
        self.assertEqual({
            "content": [],
            "status-code": 200
        }, result)

    def test_upload_without_params(self):
        result = self.fsc.upload()
        self.assertEqual(201, (result['status-code']))
        self.assertEqual(result['content']['id'], result['content']['name'])

    def test_upload_with_all_params(self):
        file = open('fooh.txt', mode='r+b').read()
        result = self.fsc.upload(file, Metadata(id='yuf5d', name='all_params_file.txt', tag='puc-puc'))
        self.assertEqual('yuf5d', result['content']['id'])
        self.assertEqual('all_params_file.txt', result['content']['name'])
        self.assertEqual('puc-puc', result['content']['tag'])
        self.assertEqual(result['content']['size'], self.fsc.get_by_id('yuf5d')[0]['size'])

    def test_upload_without_name(self):
        result = self.fsc.upload(meta=Metadata(id='fooh89', tag='puc-puc'))
        self.assertEqual('fooh89',  result['content']['name'])
        self.assertEqual('puc-puc', result['content']['tag'])

    def test_upload_jpeg(self):
        file = open('british_shorthair.jpg', mode='rb').read()
        result = self.fsc.upload(file, Metadata(id='dfd5gdg', name='cat.jpeg'))
        self.assertEqual('cat.jpeg', result['content']['name'])
        self.assertEqual('image/jpeg', result['content']['mimeType'])
        self.assertEqual(result['content']['size'], self.fsc.get_by_id('dfd5gdg')[0]['size'])

    def test_upload_audio_mp3(self):
        file = open('sample-3s.mp3', mode='rb').read()
        result = self.fsc.upload(file, Metadata(id='d4555g', name='sample.mp3'))
        self.assertEqual('sample.mp3', result['content']['name'])
        self.assertEqual('audio/mpeg', result['content']['mimeType'])
        self.assertEqual(result['content']['size'], self.fsc.get_by_id('d4555g')[0]['size'])

    def test_get_without_params(self):
        result = self.fsc.get_by_params(dict())
        self.assertEqual({
            "content": [],
            "status-code": 200
        }, result)

    def test_get_with_params(self):
        result = self.fsc.get_by_params(dict(id='fdf4h5fh', name='guga', tag='image/jpeg'))
        self.assertEqual({
            "content": [],
            "status-code": 200
        }, result)

    def test_get_with_empty_params(self):
        result = self.fsc.get_by_params(dict(id='', name='', tag=''))
        self.assertEqual({
            'content': [],
            'status-code': 200
        }, result)

    def test_upload_with_empty_params(self):
        result = self.fsc.upload(meta=Metadata(id='', name='', tag=''))
        self.assertEqual(201, result['status-code'])
        self.assertEqual(result['content']['id'], result['content']['name'])

    def test_get_with_unexepted_params(self):
        result = self.fsc.get_by_params(dict(mum='fd', meh='cats', puh='2020'))
        self.assertEqual({
            'content': [],
            'status-code': 200
        },result)


class BD_with_one_file(TestCase):

    """"
    {
    "id": "2febe",
    "name": "british_shorthair",
    "tag": "pic",
    "size": 19,
    "mimeType": "text/plain",

        }
    """

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.fsc = FileConnector('http://127.0.0.1:9876')


    def setUp(self) :
        self.fsc.upload('It`s my fluffy cat!', Metadata(id='2febe', name='british_shorthair', tag='pic'))

    def tearDown(self) -> None:
        result = self.fsc.get_without_params()['content']
        for elem in result:
            self.fsc.delete_by_id(elem['id'])

    def test_get_file(self):
        result = self.fsc.get_by_params(dict(id='2febe', name='british_shorthair'))
        self.assertEqual(200, result['status-code'])
        self.assertEqual(19, result['content'][0]['size'])
        self.assertEqual('british_shorthair', result['content'][0]['name'])

    def test_get_by_name(self):
        result = self.fsc.get_by_params(dict(name='british_shorthair'))
        self.assertEqual('2febe', result['content'][0]['id'])
        self.assertEqual('british_shorthair', result['content'][0]['name'])
        self.assertEqual('pic', result['content'][0]['tag'])
        self.assertEqual(200, result['status-code'])

    def test_upload_with_equal_id(self):
        ''' Имя и тег изменяются на новые в имеющемся файле'''

        result = self.fsc.upload(meta=Metadata(id='2febe', name='new_cat', tag='puc-puc'))
        self.assertEqual(201, result['status-code'])
        self.assertEqual('new_cat', result['content']['name'])
        self.assertEqual('puc-puc', result['content']['tag'])
        self.assertEqual('2febe', result['content']['id'])

    def test_download_file(self):
        result = self.fsc.download_by_params(dict(id='2febe', name='british_shorthair'))
        self.assertEqual({
            'content': 'It`s my fluffy cat!',
            'status-code': 200},
            result)

    def test_download_without_params(self):
        with self.assertRaises(HTTPError) as error:
            self.fsc.download_without_params()
        exception = error.exception
        self.assertEqual(400, exception.response.status_code)
        self.assertEqual("отсутствуют условия", exception.response.content.decode('utf-8'))

    def test_delete_without_params(self):
        with self.assertRaises(HTTPError) as error:
            self.fsc.delete_without_params()
        exception = error.exception
        self.assertEqual(400, exception.response.status_code)
        self.assertEqual("отсутствуют условия", exception.response.content.decode('utf-8'))

    def test_get_with_unexepted_params_and_id(self):
        result = self.fsc.get_by_params(dict(mum='fd', meh='cats', id='2febe', puh='2020'))
        self.assertEqual(200, result['status-code'])
        self.assertEqual('2febe', result['content'][0]['id'])
        self.assertEqual('british_shorthair', result['content'][0]['name'])
        self.assertEqual('pic', result['content'][0]['tag'])

    def test_delete_by_params(self):
        result = self.fsc.delete_by_params(dict(id='2febe', name='british_shorthair'))
        self.assertEqual({
            'content': '1 files deleted',
            'status-code': 200
        }, result)


class Full_DB(TestCase):

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.fsc = FileConnector('http://127.0.0.1:9876')

    def setUp(self):
        self.fsc.upload('It is my cat!', Metadata(id='1', name='cat.txt', tag='file_1'))
        self.fsc.upload('I have a dog too!', Metadata(id='2fdgdf52', name='dog.txt', tag='file_2'))
        self.fsc.upload('My name is Anton Orlov', Metadata(id='3', name='person.txt', tag='file_3'))
        self.fsc.upload('I like animals', Metadata(id='fdg44d0g0', name='like.txt', tag='file_4'))
        self.fsc.upload('New tag', Metadata(id='5', name='test-test', tag='file_3'))
        self.fsc.upload('I like my job', Metadata(id='6', name='like.txt', tag='file_6'))

    def test_file_by_name(self):
        result = self.fsc.get_by_params(dict(name='like.txt'))
        self.assertEqual(200, result['status-code'])
        self.assertEqual('6', result['content'][0]['id'])
        self.assertEqual('fdg44d0g0', result['content'][1]['id'])

    def test_with_2id(self):
        result = self.fsc.get_by_params(dict(id=['1', '3']))
        self.assertEqual(200, result['status-code'])
        self.assertEqual('1', result['content'][0]['id'])

    def test_with_2id_and_name(self):
        result = self.fsc.get_by_params(dict(id=['1', '3'], name='person.txt'))
        self.assertEqual(200, result['status-code'])
        self.assertEqual('3', result['content'][0]['id'])
        self.assertEqual('person.txt', result['content'][0]['name'])

    def test_with_2name(self):
        result = self.fsc.get_by_params(dict(name=['cat.txt', 'dog.txt']))
        self.assertEqual(200, result['status-code'])
        self.assertEqual('cat.txt', result['content'][0]['name'])

    def test_download_by_id(self):
        with self.assertRaises(HTTPError) as error:
            self.fsc.download_by_params(dict())
        exception = error.exception
        self.assertEqual(400, exception.response.status_code)
        self.assertEqual("отсутствуют условия", exception.response.content.decode('utf-8'))

    def test_get_with_tag(self):
        result = self.fsc.get_by_params(dict(tag=['file_1', 'file_4']))
        self.assertEqual(200, result['status-code'])
        self.assertEqual('file_1', result['content'][0]['tag'])

    def test_delete_2id(self):
        result = self.fsc.delete_by_params(dict(id=['1', '3']))
        self.assertEqual({
            'content': '2 files deleted',
            'status-code': 200
        }, result)

    def test_delete_equal_name(self):
        result = self.fsc.delete_by_params(dict(name='like.txt'))
        self.assertEqual({
            'content': '2 files deleted',
            'status-code': 200
        }, result)

    def test_delete_with_tag(self):
        result = self.fsc.delete_by_params(dict(name='like.txt', tag='file_6'))
        self.assertEqual({
            'content': '1 files deleted',
            'status-code': 200
        }, result)

    def test_get_with_params(self):
        result = self.fsc.get_by_params(dict(id='1', name='person.txt'))
        self.assertEqual({
            'content': [],
            'status-code': 200
        }, result)
        self.assertEqual(self.fsc.get_by_params(dict(id='1'))['content'][0]['name'], 'cat.txt')

    def test_get_by_tag(self):
        result = self.fsc.get_by_params(dict(tag=['file_3', 'file_6']))
        self.assertEqual('person.txt', result['content'][0]['name'])
        self.assertEqual('test-test', result['content'][1]['name'])
        self.assertEqual('like.txt', result['content'][2]['name'])

    def test_upload_change_file(self):
        result = self.fsc.upload('There is new file', Metadata(id='3'))
        self.assertEqual('There is new file', self.fsc.download_by_params(dict(id='3'))['content'])

    def test_change_type_file(self):
        file = open('british_shorthair.jpg', mode='rb').read()
        result = self.fsc.upload(file, Metadata(id='1', name='british_shorthair.jpg'))
        self.assertEqual(self.fsc.get_by_params(dict(id='1'))['content'][0]['mimeType'], 'image/jpeg')

    def test_get_with_size(self):
        result = self.fsc.get_by_params(dict(size='22'))
        self.assertEqual(200, result['status-code'])
        self.assertEqual('person.txt', result['content'][0]['name'])

    def test_download_by_name(self):
        with self.assertRaises(HTTPError) as error:
            self.fsc.download_by_params(dict(name='like.txt'))
        exception = error.exception
        self.assertEqual(400, exception.response.status_code)
        self.assertEqual("отсутствуют условия", exception.response.content.decode('utf-8'))

    def test_delete_with_bad_params(self):
        result = self.fsc.delete_by_params(dict(id='1', name='gunea_pig'))
        self.assertEqual({
            'content': '0 files deleted',
            'status-code': 200
        }, result)


class Endpoint_Not_Exist(TestCase):

    url = 'http://127.0.0.1:9876/puc'

    def test_get(self):
        response = request(method='get', url=self.url)
        self.assertEqual(response.raw.reason, "Not Implemented")
        self.assertEqual(response.status_code, 501)

    def test_post(self):
        response = request(method='post', url=self.url)
        self.assertEqual(response.raw.reason, "Not Implemented")
        self.assertEqual(response.status_code, 501)

    def test_delete(self):
        response = request(method='delete', url=self.url)
        self.assertEqual(response.raw.reason, "Not Implemented")
        self.assertEqual(response.status_code, 501)


if __name__ == '__main__':
    main()
