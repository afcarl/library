library
=========

The module most commonly used here is **SonicScrewdriver.py**; I import it in lots of other code as "utils."

If you're working with HathiTrust pairtree folder structure, you may be interested in the functions clean_pairtree, dirty_pairtree, and pairtreepath.

**pairtreepath** converts a HathiTrust volume ID into a path. It accepts two arguments, the volume ID and a "root path." It also returns two results, the path and a "postfix."

Here's a usage example:

    In [10]: import SonicScrewdriver as utils

    In [11]: path, postfix = utils.pairtreepath('uiuo.ark:/13960/t4bp06k8v', 'my_corpus/')

    In [12]: path
    Out[12]: 'my_corpus/uiuo/pairtree_root/ar/k+/=1/39/60/=t/4b/p0/6k/8v/'

    In [13]: postfix
    Out[13]: 'ark+=13960=t4bp06k8v'

    In [14]: path + postfix + '/' + postfix + '.zip'
    Out[14]: 'my_corpus/uiuo/pairtree_root/ar/k+/=1/39/60/=t/4b/p0/6k/8v/ark+=13960=t4bp06k8v/ark+=13960=t4bp06k8v.zip'

The last line here is probably the path to uiuo.ark:/13960/t4bp06k8v in your folder structure.

March 17, 2017
--------------

**tokenizer.py** is an old deprecated module

**tokenizetexts.py** is the updated version

Sat Aug 26, 2017
----------------

**parsefeaturejsons.py** converts HathiTrust extracted feature files into feature .tsvs that I use for predictive modeling. Probably only interests you if you want to replicate my particular workflow.
