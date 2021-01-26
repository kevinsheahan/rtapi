#!/usr/bin/env python

import rtapi_con as rt
import object_for_test as tobj


def test_AssignChassisSlot():
    # Add chassis and server to DB
    rt.rtapi.AddObject(tobj.test_chassis['name'], tobj.test_chassis['typeid'], tobj.test_chassis['asset'],
                       tobj.test_chassis['label'])
    rt.rtapi.AddObject(tobj.test_chassis_child['name'], tobj.test_chassis_child['typeid'],
                       tobj.test_chassis_child['asset'], tobj.test_chassis_child['label'])

    assert rt.rtapi.AssignChassisSlot(tobj.test_chassis['name'], "A1", tobj.test_chassis_child['name']) is None


def test_AssignCHassisSlot():
    chassis_id = rt.rtapi.GetObjectId(tobj.test_chassis['name']) 
    chassis_child_id = rt.rtapi.GetObjectId(tobj.test_chassis_child['name'])

    assert rt.rtapi.GetAllServerChassisId()[-1][0] == chassis_id
    assert rt.rtapi.DeleteObject(chassis_id) is None
    assert rt.rtapi.DeleteObject(chassis_child_id) is None
