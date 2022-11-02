import copy
import sqlite3
from typing import List, Dict, Any


class Data_Base:

    def __init__(self):
        self.connection = sqlite3.connect('storage.db')
        self.cursor = self.connection.cursor()

    def _make_table(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS storage ' \
                              '(id TEXT, name TEXT, tag TEXT,size INTEGER, mimeType TEXT, modificationTime TEXT,  UNIQUE(id))')
        self.connection.commit()

    def save_in_table(self, data: dict):
        self._make_table()
        valuesList = []
        for key in data:
            valuesList.append(data[key])
        valuesList = tuple(valuesList)
        self.cursor.execute(f'INSERT OR IGNORE INTO storage ' \
                 '(id, name, tag, size, mimeType, modificationTime) VALUES(?,?,?,?,?,?)', (valuesList))
        self.connection.commit()

    def loading_by_id(self, id):
        self._make_table()
        request = f'SELECT * FROM storage WHERE id = "{id}"'
        self.cursor.execute(request)
        result = self.cursor.fetchall()
        return self._create_list_of_dict(result)

    def loading_by_params(self, params: dict) -> List[Dict[str, Any]]:
        self._make_table()
        self.cursor.execute(f'SELECT * FROM storage {self._get_where_string(params)} ORDER BY id')
        result = self.cursor.fetchall()
        return self._create_list_of_dict(result)

    def loading_all(self) -> List[Dict[str, Any]]:
        self._make_table()
        self.cursor.execute('SELECT * FROM storage ORDER BY id')
        result = self.cursor.fetchall()
        return self._create_list_of_dict(result)

    def delete(self, params) -> int:
        self._make_table()
        list_data = self.loading_by_params(params)
        self.cursor.execute(f'DELETE from storage {self._get_where_string(params)}')
        self.connection.commit()
        return len(list_data)

    def _create_list_of_dict(self, result_list: list):
        list_of_dict = []
        table_dict = {}
        for elem in result_list:
            table_dict['id'] = elem[0]
            table_dict['name'] = elem[1]
            table_dict['tag'] = elem[2]
            table_dict['size'] = elem[3]
            table_dict['mimeType'] = elem[4]
            table_dict['modificationTime'] = elem[5]
            list_of_dict.append(copy.copy(table_dict))
        return list_of_dict

    def _get_where_string(self, params: dict) -> str:
        data = {}
        for k, v in params.items():
            if k in ['id', 'name', 'tag', 'size', 'mimeType', 'modificationTime']:
                data[k] = v
        request_list = []
        for key, v in data.items():
            values = ", ".join("'" + elem + "'" for elem in v)
            request = key + ' IN(' + values + ')'
            request_list.append(request)
        where_str = ' WHERE ' + ' AND '.join(request_list)
        return where_str

    def update(self, data: dict):
        self._make_table()
        sql_update_query = """
        UPDATE storage
        SET name = ?, tag = ?, size = ?, mimeType = ?, modificationTime = ?
        WHERE id = ?"""
        params = (data['name'],
                  data['tag'],
                  data['size'],
                  data['mimeType'],
                  data['modificationTime'],
                  data['id'])
        self.cursor.execute(sql_update_query, params)
        self.connection.commit()

    def delete_all(self):
        self._make_table()
        self.cursor.execute('DELETE from storage')
        self.connection.commit()




