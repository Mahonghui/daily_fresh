'''定义索引类'''

from .models import GoodsSKU
from haystack import indexes


class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):

    # use_template 指定根据表中哪些字段建立索引，说明文件存在文件中
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return GoodsSKU

    # 建立索引数据
    def index_queryset(self, using=None):
        return self.get_model().objects.all()