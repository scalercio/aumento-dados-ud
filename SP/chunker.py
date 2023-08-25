# encoding: utf-8

"""
Created by Gözde Gül Şahin
20.05.2018
Read UD treebanks into a data structure suitable to cropping and flipping
"""

__author__ = 'Gözde Gül Şahin'

import itertools
import random
from collections import deque

def perm(num):
    if num == 1:
        return 1
    else:
        return num * perm(num - 1)

class chunk:
    def __init__(self, min_inds, max_inds, type=u"root"):

        if min_inds[0] <= max_inds[0]:
            self.minind = min_inds[0]
            self.mindepind = min_inds[1]
            self.maxind = max_inds[0]
            self.maxdepind = max_inds[1]
        else:
            self.minind = max_inds[0]
            self.mindepind = max_inds[1]
            self.maxind = min_inds[0]
            self.maxdepind = min_inds[1]

        self.type = type
        self.size = self.maxind-self.minind+1
        self.min = self.minind
        self.max = self.maxind

    def min(self):
        return self.minind

class chunker:
    def __init__(self, asent, aloi = [u"MODIFIER",u"OBJECT",u"SUBJECT"], \
                                pl = u"PREDICATE", \
                         multilabs = [u"DERIV", u"MWE"]):
        self.sent = asent
        # label of interest
        self.loi = aloi
        # label for the predicate
        self.pl = pl
        self.multilabs = multilabs

    def _is_of_type(self, drel, rellst):

        for rel in rellst:
            if drel.startswith(rel):
                return True
        return False

    # Root span (can be derived or mwe - they shouldn't be separated)
    def _get_rootchunk(self):
        """
        Return the span of the root (starting index, ending index)
        Usually root is only one token, but sometimes compound words
        e.g., söz veriyorum, yardım edeceğim...
        :return: root chunk
        """
        rtok = None
        #print(' '.join(self.sent.tokenWords))
        for tok in self.sent.tokens:
            #print(tok.index)
            #print(tok.word)
            #print(tok.deprel)
            if (tok.depid in self.sent.deptree):
                for tok2 in self.sent.deptree[tok.depid]:
                    if (tok2.deprel==self.pl) and (int(tok2.head) > int(tok2.depid)) and ('PronType=Rel' not in tok2.feat):
                        rtok = tok
                        break
                if rtok:
                    break

        # if there is a advcl
        if rtok != None:
            maxind = rtok.index
            minind = rtok.index

            maxdepind = rtok.depid
            mindepind = rtok.depid

            children = self.sent.deptree[rtok.depid] if rtok.depid in self.sent.deptree else None
            if (children != None):
                for ch in children:
                    if self._is_of_type(ch.deprel, self.multilabs):
                        maxind = ch.index
                        maxdepind = ch.depid

            return chunk([minind, mindepind], [maxind,maxdepind], type=rtok.deprel)
        else:
            return None

    def _get_xcomp_f_chunk(self, mindepind):
        """
        Return the span of the root (starting index, ending index)
        Usually root is only one token, but sometimes compound words
        e.g., söz veriyorum, yardım edeceğim...
        :return: root chunk
        """
        rtok = None
        #print(' '.join(self.sent.tokenWords))
        for tok in self.sent.tokens:
            if (tok.depid == mindepind):
                head = tok.head
                break
        for tok in self.sent.tokens:
            if (tok.depid == head):
                rtok = tok
                break

        if rtok != None:
            maxind = rtok.index
            minind = rtok.index

            maxdepind = rtok.depid
            mindepind = rtok.depid

            return chunk([minind, mindepind], [maxind,maxdepind], type=rtok.deprel)
        else:
            return None
    
    def _get_xcomp_b_chunk(self, f_xcomp_depind):
        """
        Return the span of the root (starting index, ending index)
        Usually root is only one token, but sometimes compound words
        e.g., söz veriyorum, yardım edeceğim...
        :return: root chunk
        """
        rtok = None
        for child in self.sent.deptree[f_xcomp_depind]:
            # if it is connected with an interesting relation
            if child.deprel!='xcomp':       
                # do a breadth first search
                minnode, maxnode = self._bfs_subtree(child)
                return chunk([minnode.index, minnode.depid],[maxnode.index, maxnode.depid],type=child.deprel)

        return None
    
    def _bfs_subtree(self, node):
        queue = deque([node])
        minNode = node
        maxNode = node
        while len(queue)>0:
            # pop one element
            curNode = queue.popleft()
            # check if min or max
            if curNode.index < minNode.index and curNode.word != ".":
                minNode = curNode
            if curNode.index > maxNode.index and curNode.word != ".":
                maxNode = curNode
            # add its children (if any)
            if curNode.depid in self.sent.deptree:
                for ch in self.sent.deptree[curNode.depid]:
                    queue.append(ch)
        return minNode, maxNode


    def sanity_check(self,chunks):
        sortedchunks = sorted(chunks,key=chunk.min)
        if len(sortedchunks)>1:
            bndry = sortedchunks[0].max
            for j in range(1,len(sortedchunks)):
                if bndry<sortedchunks[j].min:
                    bndry = sortedchunks[j].max
                else:
                    return False
        return True

    def get_all_chunks(self):
        """
        Get all interesting subtrees with breadth first search
        We only get subtrees linked via LOI (label of interest)
        :return: flexible chunks
        """
        root_ch = self._get_rootchunk()
        # subtrees/chunks to be filled
        chunks = []
        main_chunk = False
        advcl = True
        # if there is a 'root' and it has some children
        if (root_ch!=None):
            # they will be dependent on the minimum index of the root span
            rind = root_ch.mindepind if root_ch.mindepind in self.sent.deptree else root_ch.maxdepind
            # Sometimes it is just a small sentence so there is no child
            if rind not in self.sent.deptree:
                return chunks
            for child in self.sent.deptree[rind]:
                # if it is connected with an interesting relation
                if self._is_of_type(child.deprel,self.loi):
                    if child.word == '.' or child.word == ':' or child.word == '!' or child.word == '?':
                        break
                    if (child.word == '"' or child.word == ';') and (int(child.depid) > int(child.head)):
                        break
                    if child.deprel == 'obl' and ('PronType=Rel' in child.feat):
                        continue
                    elif child.deprel in [ self.pl, 'conj'] and (int(child.depid) > int(child.head)):
                        break
                    #if child.deprel == self.pl and not advcl:
                    #    continue
                    #elif child.deprel == self.pl:
                    #    advcl =  False
                    if child.deprel =='conj' and self.sent.tokens[int(root_ch.min)-1].pos=='VERB':
                        continue        
                    
                    # do a breadth first search
                    minnode, maxnode = self._bfs_subtree(child)                   
                    if (int(maxnode.index) > int(root_ch.max)) and not main_chunk:
                        chunks.append(root_ch)
                        chunks.append(chunk([minnode.index, minnode.depid],[maxnode.index, maxnode.depid],type=child.deprel))
                        main_chunk = True
                    else:
                        chunks.append(chunk([minnode.index, minnode.depid],[maxnode.index, maxnode.depid],type=child.deprel))
            # and finally append root chunk
            #chunks.append(root_ch)
            
            if not main_chunk:
                chunks.append(root_ch)
            if root_ch.type=='xcomp':
                father_chunk = False
                xcomp_father_ch = self._get_xcomp_f_chunk(root_ch.mindepind)
                for i in range(len(chunks)):
                    if chunks[i].max < xcomp_father_ch.max:
                        continue
                    else:
                        chunks.insert(i, xcomp_father_ch)
                        father_chunk = True
                        break
                if not father_chunk:
                    chunks.append(xcomp_father_ch)
                
                brother_chunk = False
                xcomp_brother_ch = self._get_xcomp_b_chunk(xcomp_father_ch.mindepind)
                if xcomp_brother_ch != None:
                    for i in range(len(chunks)):
                        if chunks[i].max < xcomp_brother_ch.max:
                            continue
                        else:
                            chunks.insert(i, xcomp_brother_ch)
                            brother_chunk = True
                            break
                if not brother_chunk and (xcomp_brother_ch != None):
                    chunks.append(xcomp_brother_ch)
        if self.sanity_check(chunks):
            chunks = sorted(chunks, key=chunk.min)
            return chunks
        else:
            return []