from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client, get_tracker_conf
from django.conf import settings


class FDFSStorage(Storage):
    '''自定义文件存储类'''

    def __init__(self, conf_path=None, nginx_url = None):

        if conf_path is None:
            conf_path = settings.FASTDFS_CONF
        if nginx_url is None:
            nginx_url = settings.NGINX_URL

        self.conf_path = conf_path
        self.nginx_url = nginx_url


    def _open(self, name, mode='rb'):
        '''打开文件时调用'''
        pass

    def _save(self, name, content, max_length=None):
        '''保存文件时调用'''
        # name: 上传文件名
        # content： File类的一个对象，包含上传文件内容

        conf = get_tracker_conf(self.conf_path)
        client = Fdfs_client(conf)

        ret = client.upload_by_buffer(content.read())

        '''
        @return dict {
            'Group name'      : group_name,
            'Remote file_id'  : remote_file_id,
            'Status'          : 'Upload successed.',
            'Local file name' : '',
            'Uploaded size'   : upload_size,
            'Storage IP'      : storage_ip
        } if success else None

        '''
        if ret.get('Status') != 'Upload successed.':
            raise Exception('上传失败')
        else:
            file_id = ret.get('Remote file_id')
            # debug：file_id 是字节型数据，需要转换成str
        return file_id.decode()

    def exists(self, name):
        '''判断文件名是否可用, 相对django系统而言，与fastdfs无关'''
        '''故直接返回false，表示可用'''
        return False

    def url(self, name):
        '''返回访问记录的URL'''
        return self.nginx_url + name