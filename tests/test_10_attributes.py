#!/usr/bin/env python

import rtapi_con as rt
from tests import object_for_test

test_object = object_for_test.attribute_object
test_dict_value = None
test_chapter = 'kernels'
test_object_id = 7341


def test_GetAttributeIdByName():
    assert isinstance(rt.rtapi.GetAttributeIdByName('HW type'), int) is True


def test_GetAttributeId():
    assert isinstance(rt.rtapi.GetAttributeId('HW type'), int) is True


def test_GetDictionaryChapterId():
    chapter_id = rt.rtapi.GetDictionaryChapterId('Yes/No')
    assert isinstance(chapter_id, int) is True


def test_IntertDictionaryValue():
    chapter_id = rt.rtapi.GetDictionaryChapterId('server models')
    assert rt.rtapi.InsertDictionaryValue(chapter_id, 'testmodel') is None


def test_GetDictionaryIdByValue():
    global test_dict_value
    test_dict_value = rt.rtapi.GetDictionaryIdByValue('testmodel')
    assert isinstance(test_dict_value, int) is True


def test_GetDictionaryValueById():
    assert rt.rtapi.GetDictionaryValueById(test_dict_value) == 'testmodel'


def test_DeleteDictionaryValue():
    assert rt.rtapi.DeleteDictionaryValue('testmodel') is None


def test_InsertDictionaryChapter():
    assert rt.rtapi.InsertDictionaryChapter(test_chapter) is None


def test_DeleteDictionaryChapter():
    assert rt.rtapi.DeleteDictionaryChapter(test_chapter) is None


def test_InsertAttribute():
    att_id = rt.rtapi.GetAttributeId("HW type")
    hw_id = rt.rtapi.GetDictionaryId('testmodel')
    test_object_id = rt.rtapi.AddObject(test_object["name"], test_object["typeid"],
                                        test_object["asset"], test_object["label"])
    assert rt.rtapi.InsertAttribute(test_object_id, 4, att_id, "NULL", hw_id, 'TESTNAME') is None
    assert rt.rtapi.DeleteObject(test_object_id) is None
