#!/usr/bin/python
#
#   RTAPI
#   Racktables API is simple python module providing some methods
#   for monipulation with racktables objects.
#
#   This utility is released under GPL v2
#
#   Server Audit utility for Racktables Datacenter management project.
#   Copyright (C) 2012  Robert Vojcik (robert@vojcik.net)
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street,
#   Fifth Floor, Boston, MA  02110-1301, USA.

"""
Racktables-API (rtapi_bk) is simple python
module for manipulation with objects
in racktables database.

It allows you to interact with database for
exporting, migration or automation purposes.

For proper function, some methods
need ipaddress module (https://pypi.org/project/ipaddress/)

More information about Racktables project can be
found on https://www.racktables.org/
"""
__author__ = "Robert Vojcik (robert@vojcik.net)"
__version__ = "0.3.1"
__copyright__ = "OpenSource"
__license__ = "GPLv2"

__all__ = ["RTObject"]


import re
import ipaddress
from datetime import datetime
from datetime import timedelta


class RTObject:
    """
    Main class which create rtapi_bk object.
    You could create multiple rtapi_bk objects each
    for different database and interact between them.

    This Class needs only one parameter and it's
    database object.
    """

    # Init method
    def __init__(self, dbobject):
        """Initialize Object"""
        # Open configuration file
        self.db = dbobject
        self.dbresult = self.db.cursor()

    # DATABASE methods
    def db_query_one(self, sql, params):
        """
        SQL query function, return one row.
        Require sql query as parameter
        """
        self.dbresult.execute(sql, params)
        return self.dbresult.fetchone()

    def db_query_all(self, sql, params):
        """
        SQL query function, return all rows.
        Require sql query as parameter
        """
        self.dbresult.execute(sql, params)
        return self.dbresult.fetchall()

    def db_insert(self, sql, params):
        """SQL insert/update function. Require sql query as parameter"""
        self.dbresult.execute(sql, params)
        self.db.commit()

    def db_fetch_lastid(self):
        """SQL function which return ID of last inserted row."""
        return self.dbresult.lastrowid

    def ListObjects(self, data='sum'):
        """
        List all objects from database
        You can specify data sum or list to get summary or list of objects
        In list you get array of id,name,asset_no,objtype_id
        """
        if data == 'list':
            sql = """SELECT id,name,asset_no,objtype_id FROM Object"""
            return self.db_query_all(sql, None)
        else:
            sql = """SELECT count(name) FROM Object"""
            return "Found " + str(self.db_query_one(sql, None)[0]) + " objects in database"

    def ListObjectsByType(self, object_tid):
        """
        Get list of objects based on object type ID
        """
        sql = """"SELECT id,name,asset_no,label,comment,has_problems from Object WHERE objtype_id = %s"""
        return self.db_query_all(sql, (object_tid,))

    # Object methotds
    def ObjectExistST(self, service_tag):
        """Check if object exist in database based on asset_no"""
        sql = """SELECT name FROM Object WHERE asset_no = %s"""
        if self.db_query_one(sql, (service_tag,)) is None:
            return False
        else:
            return True

    def ObjectExistName(self, name):
        """Check if object exist in database based on name"""
        sql = """select id from Object where name = %s"""
        if self.db_query_one(sql, (name,)) is None:
            return False
        else:
            return True

    def ObjectExistSTName(self, name, asset_no):
        """Check if object exist in database based on name"""
        sql = """SELECT id FROM Object WHERE name = %s AND asset_no = %s"""
        if self.db_query_one(sql, (name, asset_no)) is None:
            return False
        else:
            return True

    def AddObject(self, name, server_type_id, asset_no, label):
        """Add new object to racktables"""
        sql = """INSERT INTO Object (name, objtype_id, asset_no, label) VALUES (%s, %s, %s, %s)"""
        # params = (name.encode('utf-8'), server_type_id, asset_no.encode('utf-8'), label.encode('utf-8'))
        params = (name, server_type_id, asset_no, label)
        self.db_insert(sql, params)
        return self.db_fetch_lastid()

    def DeleteObject(self, objid):
        """Add new object to racktables"""
        sql = """DELETE FROM Object WHERE id = %s"""
        self.db_insert(sql, (objid,))

    def UpdateObjectLabel(self, object_id, label):
        """Update label on object"""
        sql = """UPDATE Object SET label = %s where id = %s"""
        params = (label, object_id)
        self.db_insert(sql, params)

    def UpdateObjectComment(self, object_id, comment):
        """Update comment on object"""
        sql = """UPDATE Object SET comment = %s where id = %s"""
        params = (comment, object_id)
        self.db_insert(sql, params)

    def UpdateObjectName(self, object_id, name):
        """Update name on object"""
        sql = """UPDATE Object SET name = %s where id = %s"""
        params = (name, object_id)
        self.db_insert(sql, params)

    def GetObjectName(self, object_id):
        """Translate Object ID to Object Name"""
        # Get interface id
        sql = """SELECT name FROM Object WHERE id = %s"""
        result = self.db_query_one(sql, (object_id,))
        if result is not None:
            object_name = result[0]
        else:
            object_name = None

        return object_name

    def GetObjectNameByAsset(self, service_tag):
        """Translate Object AssetTag to Object Name"""
        # Get interface id
        sql = """SELECT name FROM Object WHERE asset_no = %s"""
        result = self.db_query_one(sql, (service_tag,))
        if result is not None:
            object_name = result[0]
        else:
            object_name = None

        return object_name

    def GetObjectIdByAsset(self, service_tag):
        """Get Object ID by Asset Tag"""

        sql = """SELECT id FROM Object WHERE asset_no = %s"""
        result = self.db_query_one(sql, (service_tag,))
        if result is not None:
            object_id = result[0]
        else:
            object_id = None

        return object_id

    def GetObjectLabel(self, object_id):
        """Get object label"""
        # Get interface id
        sql = """SELECT label FROM Object WHERE id = %s"""
        result = self.db_query_one(sql, (object_id,))
        if result is not None:
            object_label = result[0]
        else:
            object_label = None

        return object_label

    def GetObjectComment(self, object_id):
        """Get object comment"""
        # Get interface id
        sql = """SELECT comment FROM Object WHERE id = %s"""
        result = self.db_query_one(sql, (object_id,))
        if result is not None:
            object_comment = result[0]
        else:
            object_comment = None

        return object_comment

    def GetObjectTags(self, object_id):
        """Get object tags"""
        sql = """SELECT t1.tag as parent_tag, t2.tag as tag FROM TagTree as t1 RIGHT JOIN TagTree as t2 ON t1.id = t2.parent_id WHERE t2.id IN (SELECT tag_id FROM TagStorage JOIN Object ON TagStorage.entity_id = Object.id WHERE TagStorage.entity_realm='object' and Object.id = %s)"""
        result = self.db_query_all(sql, (object_id,))

        return result

    def GetObjectsByTag(self, tag_name):
        """Get Array of objects from Racktables database by Tag name"""

        sql = """SELECT t1.name, \
               t1.id \
               FROM Object AS t1 \
               JOIN \
               TagStorage AS t2 \
               ON t1.id = t2.entity_id \
               JOIN \
               TagTree AS t3 \
               ON t2.tag_id = t3.id \
               WHERE t3.tag = %s"""

        return self.db_query_all(sql, (tag_name,))

    def GetObjectId(self, name):
        """Translate Object name to object id"""
        # Get interface id
        sql = """SELECT id FROM Object WHERE name = %s"""
        result = self.db_query_one(sql, (name,))
        if result is not None:
            object_id = result[0]
        else:
            object_id = None

        return object_id

    def ListDockerContainersOfHost(self, docker_host):
        """List all Docker containers of specified host"""
        sql = """SELECT name FROM IPv4Address WHERE comment = "Docker host: %s"""""
        return self.db_query_all(sql, (docker_host,))

    def AddDockerContainer(self, container_ip, container_name, docker_host):
        """Add new Docker container to racktables"""
        self.InsertIPv4Log(container_ip, "Name set to " + container_name + ", comment set to Docker host: " + docker_host + "")
        sql = """INSERT INTO IPv4Address (ip,name,comment,reserved) VALUES (INET_ATON(%s),%s,'Docker host: %s','yes')"""
        params = (container_ip, container_name, docker_host)
        self.db_insert(sql, params)

    def RemoveDockerContainerFromHost(self, container_name, docker_host):
        """Remove Docker container from racktables"""
        sql = """SELECT INET_NTOA(ip) FROM IPv4Address WHERE comment = 'Docker host: %s' AND name = %s"""
        for ip in self.db_query_all(sql, (docker_host, container_name)):
                sql = """SELECT IFNULL(DATEDIFF(NOW(), MAX(date)), 0) FROM IPv4Log WHERE ip = INET_ATON(%s)"""
                if self.db_query_one(sql, (ip[0],)) >= 1:
                    self.InsertIPv4Log(ip[0], "Name " + container_name + " removed, comment Docker host: " + docker_host + " removed")
                    sql = """DELETE FROM IPv4Address WHERE ip = INET_ATON(%s)"""
                    self.db_insert(sql, (ip[0]))

    def UpdateDockerContainerName(self, ip, name):
        """Update Docker container name"""
        self.InsertIPv4Log(ip, "Name set to " + name + "")
        sql = """UPDATE IPv4Address SET name = %s WHERE ip = INET_ATON(%s)"""
        self.db_insert(sql, (name, ip))

    def UpdateDockerContainerHost(self, ip, host):
        """Update Docker container host"""
        self.InsertIPv4Log(ip, "Comment set to Docker host: " + host + "")
        sql = """UPDATE IPv4Address SET comment = 'Docker host: %s' WHERE ip = INET_ATON(%s)"""
        self.db_insert(sql, (host, ip))

    def GetDockerContainerName(self, ip):
        """Get Docker container name"""
        # Get interface id
        sql = """SELECT name FROM IPv4Address WHERE ip = INET_ATON(%s)"""
        result = self.db_query_one(sql, (ip,))
        if result is not None:
            ip_name = result[0]
        else:
            ip_name = None
        return ip_name

    def GetDockerContainerHost(self, ip):
        """Get Docker container host"""
        # Get interface id
        sql = """SELECT comment FROM IPv4Address WHERE ip = INET_ATON(%s)"""
        result = self.db_query_one(sql, (ip,))
        host = None
        if result is not None:
            m = re.match("^Docker host: (.*)$", result[0])
            if m:
                host = m.group(1)
        return host

    # Logging
    def InsertLog(self, object_id, message):
        """Attach log message to specific object"""
        sql = """INSERT INTO ObjectLog (object_id,user,date,content) VALUES (%s,'script',now(),%s)"""
        self.db_insert(sql, (int(object_id), message))

    def InsertIPv4Log(self, ip, message):
        """Attach log message to IPv4"""
        sql = """INSERT INTO IPv4Log (ip,user,date,message) VALUES (INET_ATON(%s),'script',now(),%s)"""
        self.db_insert(sql, (ip, message))

    # Attrubute methods
    def CreateAttribute(self, attr_type, attr_name):
        """ Create new attribute in Racktables. Require attr_type (string, dict, uint) and attr_name """
        sql = """SELECT id FROM Attribute WHERE name = %s"""

        result = self.db_query_one(sql, (attr_name,))
        if result is not None:
            getted_id = result[0]
        else:
            getted_id = None

        if getted_id == None:
            sql = """INSERT INTO Attribute (type, name) VALUES (%s, %s)"""
            self.db_insert(sql, (attr_type, attr_name))

    def MapAttribute(self, objtype_id, attr_id, chapter_id='NULL', sticky='no'):
        """ Map attribute to object type """

        if chapter_id != 'NULL':
            chap_search = "chapter_id = %s AND " % (int(chapter_id))
        else:
            chap_search = ""

        sql = """SELECT objtype_id FROM AttributeMap WHERE objtype_id = %s AND attr_id = %s AND %s sticky = %s"""

        result = self.db_query_one(sql, ( objtype_id, attr_id, chap_search, sticky ))
        if result is not None:
            getted_id = result[0]
        else:
            getted_id = None

        if getted_id == None:
            sql = """INSERT INTO AttributeMap (objtype_id, attr_id, chapter_id, sticky) VALUES (%s, %s, %s, %s)"""
            params = (objtype_id, attr_id, str(chapter_id), sticky)
            self.db_insert(sql, params)

    def InsertAttribute(self, object_id, object_tid, attr_id, string_value, uint_value, name=None):
        """Add or Update object attribute.
        Require 6 arguments: object_id, object_tid, attr_id, string_value, uint_value, name"""

        # Check if attribute exist
        sql = """SELECT string_value,uint_value FROM AttributeValue WHERE object_id = %s AND object_tid = %s AND attr_id = %s"""
        result = self.db_query_one(sql, (object_id, object_tid, attr_id))

        if result is not None:
            # Check if attribute value is same and determine attribute type
            old_string_value = result[0]
            old_uint_value = result[1]
            same_flag = "no"
            attribute_type = "None"

            if old_string_value is not None:
                attribute_type = "string"
                if old_string_value == string_value:
                    same_flag = "yes"
            elif old_uint_value is not None:
                attribute_type = "uint"
                if old_uint_value == uint_value:
                    same_flag = "yes"

            # If exist, update value
            if same_flag == "no":
                params = None
                if attribute_type == "string":
                    sql = """UPDATE AttributeValue SET string_value = %s WHERE object_id = %s AND attr_id = %s AND object_tid = %s"""
                    params = (string_value, object_id, attr_id, object_tid)
                if attribute_type == "uint":
                    sql = """UPDATE AttributeValue SET uint_value = %s WHERE object_id = %s AND attr_id = %s AND object_tid = %s"""
                    params = (uint_value, object_id, attr_id, object_tid)
                self.db_insert(sql, params)

        else:
            # Attribute not exist, insert new
            if string_value == "NULL":
                sql = """INSERT INTO AttributeValue (object_id,object_tid,attr_id,uint_value) VALUES (%s,%s,%s,%s)"""
                params = (object_id, object_tid, attr_id, uint_value)
            else:
                sql = """INSERT INTO AttributeValue (object_id,object_tid,attr_id,string_value) VALUES (%s,%s,%s,%s)"""
                params = (object_id, object_tid, attr_id, string_value)
            self.db_insert(sql, params)

    def GetAttributeId(self, searchstring):
        """Search racktables database and get attribud id based on search string as argument"""
        sql = "SELECT id FROM Attribute WHERE name LIKE '%" + searchstring + "%'"

        result = self.db_query_one(sql, None)

        if result is not None:
            getted_id = result[0]
        else:
            getted_id = None

        return getted_id

    def GetAttributeIdByName(self, attr_name):
        """Get the ID of an attribute by its EXACT name"""
        sql = """SELECT id FROM Attribute WHERE name = %s"""

        result = self.db_query_one(sql, (attr_name,))

        if result is not None:
            getted_id = result[0]
        else:
            getted_id = None

        return getted_id

    def GetAttributeValue(self, object_id, attr_id):
        """Search racktables database and get attribute values"""
        sql = """SELECT string_value,uint_value,float_value FROM AttributeValue WHERE object_id = %s AND attr_id = %s"""

        result = self.db_query_one(sql, (object_id, attr_id))

        if result is not None:
            output = [result[0], result[1], result[2]]
        else:
            output = None

        return output

    # Interfaces methods
    def GetInterfaceList(self, object_id):
        """
        Get list of object interfaces ids and names
        Return array of touples id, name, type
        """
        sql = """SELECT id, name, type FROM Port where object_id = %s"""
        return self.db_query_all(sql, (object_id,))

    def GetInterfaceName(self, object_id, interface_id):
        """Find name of specified interface. Required object_id and interface_id argument"""
        # Get interface name
        sql = """SELECT name FROM Port WHERE object_id = %s AND id = %s"""
        result = self.db_query_one(sql, (object_id, interface_id))
        if result is not None:
            port_name = result[0]
        else:
            port_name = None

        return port_name

    def GetInterfaceId(self, object_id, interface):
        """Find id of specified interface"""
        # Get interface id
        sql = """SELECT id,name FROM Port WHERE object_id = %s AND name = %s"""
        result = self.db_query_one(sql, (object_id, interface))
        if result is not None:
            port_id = result[0]
        else:
            port_id = None

        return port_id

    def UpdateNetworkInterface(self, object_id, interface):
        """Add network interfece to object if not exist"""

        sql = """SELECT id,name FROM Port WHERE object_id = %s AND name = %s"""

        result = self.db_query_one(sql, (object_id, interface))
        if result is None:

            sql = """INSERT INTO Port (object_id,name,iif_id,type) VALUES (%s,%s,1,24)"""
            self.db_insert(sql, (object_id, interface))
            port_id = self.db_fetch_lastid()

        else:
            port_id = result[0]

        return port_id

    def GetPortDeviceNameById(self, port_id):
        """Get Device name and Port Name by port ID, return dictionary device_name, port_name"""

        sql = """SELECT Port.name as port_name, Object.name as obj_name FROM Port INNER JOIN Object ON Port.object_id = Object.id WHERE Port.id = %s;"""
        result = self.db_query_one(sql, (port_id,))

        if result is None:
            return result
        else:
            port_name = result[0]
            device_name = result[1]
            return {'device_name': device_name, 'port_name': port_name}

    def GetDictionaryId(self, searchstring, chapter_id=None):
        """
        Search racktables dictionary using searchstring and return id of dictionary element
        It is possible to specify chapter_id for more specific search
        """
        if not chapter_id:
            sql = "SELECT dict_key FROM Dictionary WHERE dict_value LIKE '%%%s%%'" % (searchstring)
        else:
            sql = "SELECT dict_key FROM Dictionary WHERE chapter_id = %d AND dict_value LIKE '%%%s%%'" % (int(chapter_id), searchstring)


        result = self.db_query_one(sql, None)
        if result is not None:
            getted_id = result[0]
        else:
            getted_id = None

        return getted_id

    def GetDictionaryChapterId(self, value):
        """Search racktables dictionary chapter using exact value and return id of dictionary chapter"""
        sql = """SELECT id FROM Chapter WHERE name = %s"""

        result = self.db_query_one(sql, (value,))
        if result is not None:
            getted_id = result[0]
        else:
            getted_id = None

        return getted_id

    def GetDictionaryIdByValue(self, dict_value, chapter_id=None):
        """
        Get the ID of a dictionary entry by its EXACT value
        Is it possible to specify chapter_id for more specific search.
        """
        if not chapter_id:
            sql = """SELECT dict_key FROM Dictionary WHERE dict_value = %s"""
            params = (dict_value,)
        else:
            sql = """SELECT dict_key FROM Dictionary WHERE dict_value = %s AND chapter_id = %s"""
            params = (dict_value, int(chapter_id))

        result = self.db_query_one(sql, params)
        if result is not None:
            getted_id = result[0]
        else:
            getted_id = None

        return getted_id

    def GetDictionaryValueById(self, dict_key):
        """Get value from Dictionary by ID reference"""
        sql = """SELECT dict_value FROM Dictionary WHERE dict_key = %s """

        result = self.db_query_one(sql, (dict_key,))
        if result is not None:
            getted_id = result[0]
        else:
            getted_id = None

        return getted_id

    def InsertDictionaryChapter(self, value, sticky='no'):
        """ Insert new dictionary chapter """
        sql = """INSERT INTO Chapter (sticky, name) VALUES (%s, %s)"""
        self.db_insert(sql, (sticky, value))

    def DeleteDictionaryChapter(self, value, sticky='no'):
        sql = """DELETE FROM Chapter WHERE name = %s"""
        self.db_insert(sql, (value,))

    def InsertDictionaryValue(self, dict_id, value):
        """Insert value into dictionary identified by dict_id"""
        sql = """INSERT INTO Dictionary (chapter_id,dict_value) VALUES (%s, %s)"""
        self.db_insert(sql, (dict_id, value))

    def DeleteDictionaryValue(self, value):
        sql = """DELETE FROM Dictionary  WHERE dict_value = %s"""
        self.db_insert(sql, (value, ))

    # Attribute methods
    def QueryTypedAttributeValue(self, object_id, attr_id, attr_type):
        sql = """SELECT %s FROM AttributeValue WHERE object_id = %s AND attr_id = %s"""
        res = self.db_query_one(sql, (attr_type, object_id, attr_id))

        if(res is None):
            return None
        else:
            return res[0]

    def InsertOrUpdateStringAttribute(self, object_id, objtype_id, attr_id, new_value):
        old_value = self.QueryTypedAttributeValue(object_id, attr_id, 'string_value')
        if old_value is None:
            # INSERT
            return """INSERT INTO AttributeValue (object_id,object_tid,attr_id,string_value) VALUES (%s,%s,%s,%s)"""
        else:
            # UPDATE
            return """UPDATE AttributeValue SET string_value = %s WHERE object_id = %s AND attr_id = %s AND object_tid = %s"""

    def InsertOrUpdateUintAttribute(self, object_id, objtype_id, attr_id, new_value):
        old_value = self.QueryTypedAttributeValue(object_id, attr_id, 'uint_value')
        if old_value is None:
            # INSERT
            return """INSERT INTO AttributeValue (object_id,object_tid,attr_id,uint_value) VALUES (%s,%s,%s,%s)"""
        elif old_value != new_value:
            # UPDATE
            return """UPDATE AttributeValue SET uint_value = %s WHERE object_id = %s AND attr_id = %s AND object_tid = %s"""

    def InsertOrUpdateFloatAttribute(self, object_id, objtype_id, attr_id, new_value):
        old_value = self.QueryTypedAttributeValue(object_id, attr_id, 'float_value')
        if old_value is None:
            # INSERT
            return """INSERT INTO AttributeValue (object_id,object_tid,attr_id,float_value) VALUES (%s,%s,%s,%f)"""
        elif old_value != new_value:
            # UPDATE
            return """UPDATE AttributeValue SET float_value = %f WHERE object_id = %s AND attr_id = %s AND object_tid = %s"""

    def InsertOrUpdateDateAttribute(self, object_id, objtype_id, attr_id, new_value):
        dt = datetime.strptime(new_value, "%Y-%m-%s")
        return self.InsertOrUpdateUintAttribute(object_id, objtype_id, attr_id, (dt - datetime(1970, 1, 1)) / timedelta(seconds=1))

    def InsertOrUpdateAttribute_FunctionDispatcher(self, attr_type):
        InsertOrUpdateAttribute_TypeFunctions = {
            'uint': self.InsertOrUpdateUintAttribute,
            'dict': self.InsertOrUpdateUintAttribute,
            'float': self.InsertOrUpdateFloatAttribute,
            'string': self.InsertOrUpdateStringAttribute,
            'date': self.InsertOrUpdateDateAttribute
        }
        return InsertOrUpdateAttribute_TypeFunctions.get(attr_type)

    def InsertOrUpdateAttribute(self, object_id, attr_id, new_value):
        # Get the object type
        sql = """SELECT objtype_id FROM Object WHERE id = %s"""
        result = self.db_query_one(sql, (object_id,))

        if(result is not None):
            objtype_id = result[0]
        else:
            # Object not found in database - return None since we can not update an attribute on a non-existing object
            return None

        # Get the attribute type
        sql = """SELECT type FROM Attribute WHERE id = %s"""
        result = self.db_query_one(sql, (attr_id,))

        if(result is not None):
            attr_type = result[0]
        else:
            # Attribute with given ID does not exist - return None since the requested attribute does not exist
            return None

        # Get the correct function for this attribute type
        func = self.InsertOrUpdateAttribute_FunctionDispatcher(attr_type)

        # Get the SQL statement for Insert/Update
        sql = func(object_id, objtype_id, attr_id, new_value)

        # If there is nothing to update (eg. old_value == new_value)
        # then the InsertOrUpdateAttribute_TypeFunction returns None and there is no SQL statement to execute
        if sql is not None:
            # TODO check action needed
            self.db_insert(sql, (object_id, objtype_id, attr_id, new_value))

    def GetObjectAttributes(self, object_id):
        """Get list of Object attributes"""

        sql = """SELECT ob.id,
               ob.name AS routerName,
               ob.label,
               a.name AS attrName,
               a.type,
               d.dict_value,
               av.* FROM Object as ob
               JOIN AttributeValue AS av ON (ob.id=av.object_id)
               JOIN Attribute AS a ON (av.attr_id=a.id)
               LEFT JOIN Dictionary AS d ON (d.dict_key=av.uint_value)
               WHERE ob.id = %s ORDER BY a.name"""

        return self.db_query_all(sql, (object_id,))

    def CleanUnusedInterfaces(self, object_id, interface_list):
        """Remove unused old interfaces"""
        sql = """SELECT id, name FROM Port WHERE object_id = %s"""
        result = self.db_query_all(sql, (object_id,))

        # Copy interface list becouse we need to change it
        interfaces = interface_list[:]
        # Add drac to interface list
        interfaces.append("drac")

        if result is not None:
            for row in result:
                if row[1] not in interfaces:
                    # Remove IPv4 allocation
                    sql = "DELETE FROM IPv4Allocation WHERE object_id = %s AND name = %s"
                    self.db_insert(sql, (object_id, row[1]))
                    self.InsertLog(object_id, "Removed IPv4 ips for %s" % row[1])
                    # Remove IPv6 allocation
                    sql = "DELETE FROM IPv6Allocation WHERE object_id = %s AND name = %s"
                    self.db_insert(sql, (object_id, row[1]))
                    self.InsertLog(object_id, "Removed IPv6 ips for %s" % row[1])
                    # Remove port links
                    sql = "DELETE FROM Link WHERE porta = %s OR portb = %s"
                    self.db_insert(sql, (row[0], row[0]))
                    self.InsertLog(object_id, "Remove port links %s" % row[1])
                    # Remove port
                    sql = "DELETE FROM Port WHERE object_id = %s AND name = %s"
                    self.db_insert(sql, (object_id, row[1]))
                    self.InsertLog(object_id, "Removed interface %s" % row[1])

    def CleanVirtuals(self, object_id, virtual_servers):
        """Clean dead virtuals from hypervisor. virtual_servers is list of active virtual servers on hypervisor (object_id)"""

        sql = """SELECT child_entity_id FROM EntityLink WHERE parent_entity_id = %s"""

        result = self.db_query_all(sql, (object_id,))
        delete_virtual_id = []

        if result is not None:
            old_virtuals_ids = result
            new_virtuals_ids = []
            # Translate names into ids
            for new_virt in virtual_servers:
                new_id = self.GetObjectId(new_virt)
                if new_id is not None:
                    new_virtuals_ids.append(new_id)

            for old_id in old_virtuals_ids:
                try:
                    new_virtuals_ids.index(old_id[0])
                except ValueError:
                    delete_virtual_id.append(old_id[0])
        if len(delete_virtual_id) != 0:
            for virt_id in delete_virtual_id:

                sql = "DELETE FROM EntityLink WHERE parent_entity_id = %s AND child_entity_id = %s"
                self.db_insert(sql, (object_id, virt_id))
                virt_name = self.GetObjectName(virt_id)
                logstring = "Removed virtual %s" % virt_name
                self.InsertLog(object_id, logstring)


    def LinkVirtualHypervisor(self, object_id, virtual_id):
        """Assign virtual server to correct hypervisor"""
        sql = """SELECT child_entity_id FROM EntityLink WHERE parent_entity_id = %s AND child_entity_id = %s"""
        result = self.db_query_one(sql, (object_id, virtual_id))

        if result is None:
            sql = """INSERT INTO EntityLink (parent_entity_type, parent_entity_id, child_entity_type, child_entity_id) VALUES ('object',%s,'object',%s)"""
            self.db_insert(sql, (object_id, virtual_id))
            text = "Linked virtual %s with hypervisor" % self.GetObjectName(virtual_id)
            self.InsertLog(object_id, text)

    def AssignChassisSlot(self, chassis_name, slot_number, server_name):
        """Assign server objects to server chassis"""
        chassis_id = self.GetObjectId(chassis_name)
        server_id = self.GetObjectId(server_name)
        slot_attribute_id = self.GetAttributeId("Slot number")

        sql = """SELECT string_value FROM AttributeValue WHERE object_id = %s AND object_tid = 4 AND attr_id = %s"""
        result = self.db_query_one(sql, (server_id, slot_attribute_id))

        if result is not None:
            # Try to update Value, if no success Insert new value
            sql = """UPDATE AttributeValue SET string_value = %s WHERE object_id = %s AND object_tid = 4 AND attr_id = %s"""
            params = (slot_number, server_id, slot_attribute_id)
            self.db_insert(sql, params)
        else:
            # Assign slot number to server
            sql = """INSERT INTO AttributeValue (object_id, object_tid, attr_id, string_value) VALUES ( %s, 4, %s, %s)"""
            params = (server_id, slot_attribute_id, slot_number)
            self.db_insert(sql, params)

        # Assign server to chassis
        # Check if it's connected
        sql = """SELECT parent_entity_id FROM EntityLink WHERE child_entity_type = 'object' AND child_entity_id = %s"""
        result = self.db_query_one(sql, (server_id,))

        if result is not None:
            # Object is connected to someone
            if result[0] != chassis_id:
                # Connected to differend chassis/chassis
                sql = """UPDATE EntityLink SET parent_entity_id = %s WHERE child_entity_id = %s AND child_entity_type = 'object' AND parent_entity_id = %s"""
                params = (chassis_id, server_id, result[0])
                self.db_insert(sql, params)

                old_object_name = self.GetObjectName(result[0])
                self.InsertLog(result[0], "Unlinked server %s" % (server_name))
                self.InsertLog(server_id, "Unlinked from Blade Chassis %s" % (old_object_name))
                self.InsertLog(chassis_id, "Linked with server %s" % (server_name))
                self.InsertLog(server_id, "Linked with Blade Chassis %s" % (chassis_name))

        else:
            # Object is not connected
            sql = """INSERT INTO EntityLink (parent_entity_type, parent_entity_id, child_entity_type, child_entity_id) VALUES ('object', %s, 'object', %s)"""
            params = (chassis_id, server_id)
            self.db_insert(sql, params)
            self.InsertLog(chassis_id, "Linked with server %s" % (server_name))
            self.InsertLog(server_id, "Linked with Blade Chassis %s" % (chassis_name))

    def GetAllServerChassisId(self):
        """Get list of all server chassis IDs"""
        sql = """SELECT id FROM Object WHERE objtype_id = 1502"""
        return self.db_query_all(sql, None)

    #
    # Networks methots
    #
    def GetIpv4Networks(self):
        """Get All IPV4 Networks"""
        sql = """SELECT id, INET_NTOA(ip), mask, name FROM IPv4Network"""

        return self.db_query_all(sql, None)

    def GetIpv6Networks(self):
        """Get All IPV6 Networks"""
        sql = """SELECT id, HEX(ip), mask, name FROM IPv6Network"""

        return self.db_query_all(sql, None)

    def GetIpv4Allocations(self):
        """Get IPv4 Allocations for specific network"""
        sql = """SELECT INET_NTOA(ip), object_id, name AS int_name, Null AS name, Null AS comment from IPv4Allocation UNION SELECT INET_NTOA(ip), Null AS object_id, Null AS int_name, name, comment FROM IPv4Address"""

        return self.db_query_all(sql, None)

    def GetIpv6Allocations(self):
        """Get IPv6 Allocations for specific network"""
        sql = """SELECT HEX(ip), object_id, name AS int_name, Null AS name, Null AS comment from IPv6Allocation UNION SELECT HEX(ip), Null AS object_id, Null AS int_name, name, comment FROM IPv6Address"""

        return self.db_query_all(sql, None)

    def SetIPComment(self, comment, ip):
        """ Set comment for IP address """
        sql = """SELECT comment FROM IPv4Address WHERE INET_NTOA(ip) = %s"""
        result = self.db_query_one(sql, (ip,))

        if result is not None:
            sql = "UPDATE IPv4Address SET comment = %s WHERE INET_NTOA(ip) = %s"
            params = (comment, ip)
        else:
            sql = "INSERT INTO IPv4Address (ip, comment) VALUES (INET_ATON(%s), %s)"
            params = (ip, comment)

        self.db_insert(sql, params)

    def SetIPName(self, name, ip):
        """ Set name for IP address """
        sql = """SELECT name FROM IPv4Address WHERE INET_NTOA(ip) = %s"""
        result = self.db_query_one(sql, (ip,))

        if result is not None:
            sql = """UPDATE IPv4Address SET name = %s WHERE INET_NTOA(ip) = %s"""
            params = (name, ip)
        else:
            sql = """INSERT INTO IPv4Address (ip, name) VALUES (INET_ATON(%s), %s)"""
            params = (ip, name)

        self.db_insert(sql, params)

    def FindIPFromComment(self, comment, network_name):
        """Find IP address based on comment"""
        # Get Network information
        sql = """SELECT ip,mask from IPv4Network WHERE name = %s"""
        result = self.db_query_one(sql, (network_name,))

        if result is not None:
            ip_int = result[0]
            ip_mask = result[1]
            ip_int_max = (2 ** (32 - ip_mask)) + ip_int

            sql = """SELECT INET_NTOA(ip) FROM IPv4Address WHERE ip >= %s AND ip <= %s and comment = %s"""

            result = self.db_query_all(sql, (ip_int, ip_int_max, comment))
            if result is not None:
                return "\n".join(str(x[0]) + "/" + str(ip_mask) for x in result)
            else:
                return False

        else:
            return False

    def SetIP6Comment(self, comment, ip):
        """ Set comment for IPv6 address """

        # Create address object using ipaddr
        addr6 = ipaddress.IPv6Address(ip)
        # Create IPv6 format for Mysql
        db_ip6_format = "".join(str(x) for x in addr6.exploded.split(':')).upper()

        sql = """SELECT comment FROM IPv6Address WHERE HEX(ip) = %s"""
        result = self.db_query_one(sql,(db_ip6_format))

        if result is not None:
            sql = """UPDATE IPv6Address SET comment = %s WHERE HEX(ip) = %s"""
            params = (comment, db_ip6_format)
        else:
            sql = """INSERT INTO IPv6Address (ip, comment) VALUES (UNHEX(%s), %s)"""
            params = (db_ip6_format, comment)

        self.db_insert(sql, params)

    def FindIPv6FromComment(self, comment, network_name):
        """Find IP address based on comment"""
        sql = """SELECT HEX(ip),mask,hex(last_ip) from IPv6Network WHERE name = %s"""
        result = self.db_query_one(sql, (network_name,))

        if result is not None:
            ip = result[0]
            ip_mask = result[1]
            ip_max = result[2]

            sql = """select HEX(ip) from IPv6Address where ip between UNHEX(%s) AND UNHEX(%s) AND comment = %s;"""

            result = self.db_query_all(sql, (ip, ip_max, comment))
            if result is not None:
                return "\n".join(str(re.sub(r'(.{4})(?=.)', r'\1:', x[0]).lower()) + "/" + str(ip_mask) for x in result)
            else:
                return False

        else:
            return False

    def CleanIPAddresses(self, object_id, ip_addresses, device):
        """Clean unused ip from object. ip addresses is list of IP addresses configured on device (device) on host (object_id)"""

        sql = """SELECT INET_NTOA(ip) FROM IPv4Allocation WHERE object_id = %s AND name = %s"""

        result = self.db_query_all(sql, (object_id, device))
        delete_ips = []

        if result is not None:
            old_ips = result

            for old_ip in old_ips:
                try:
                    ip_addresses.index(old_ip[0])
                except ValueError:
                    delete_ips.append(old_ip[0])
        if len(delete_ips) != 0:
            for ip in delete_ips:
                sql = """DELETE FROM IPv4Allocation WHERE ip = INET_ATON(%s) AND object_id = %s AND name = %s"""
                self.db_insert(sql, (ip, object_id, device))
                logstring = "Removed IP %s from %s" % (ip, device)
                self.InsertLog(object_id, logstring)

    def CleanIPv6Addresses(self, object_id, ip_addresses, device):
        """Clean unused ipv6 from object. ip_addresses mus be list of active IP addresses on device (device) on host (object_id)"""

        sql = """SELECT HEX(ip) FROM IPv6Allocation WHERE object_id = %s AND name = %s"""
        result = self.db_query_all(sql, (object_id, device))
        delete_ips = []

        if result is not None:
            old_ips = result
            new_ip6_ips = []

            # We must prepare ipv6 addresses into same format for compare
            for new_ip in ip_addresses:
                converted = ipaddress.IPv6Address(new_ip).exploded.lower()
                new_ip6_ips.append(converted)

            for old_ip_hex in old_ips:
                try:
                    # First we must construct IP from HEX
                    tmp = re.sub("(.{4})", "\\1:", old_ip_hex[0], re.DOTALL)
                    # Remove last : and lower string
                    old_ip = tmp[:len(tmp) - 1].lower()

                    new_ip6_ips.index(old_ip)

                except ValueError:
                    delete_ips.append(old_ip)

        if len(delete_ips) != 0:
            for ip in delete_ips:
                db_ip6_format = "".join(str(x) for x in ip.split(':'))
                sql = """DELETE FROM IPv6Allocation WHERE ip = UNHEX(%s) AND object_id = %s AND name = %s"""
                params = (db_ip6_format, object_id, device)
                self.db_insert(sql, params)
                logstring = "Removed IP %s from %s" % (ip, device)
                self.InsertLog(object_id, logstring)
    
    def CheckIfIp4IPExists(self, ip):
        """Check if ipv4 record exist in database"""
        sql = """select ip from IPv4Address where ip = INET_ATON(%s)"""
        if self.db_query_one(sql, (ip,)) is None:
            sql = """select ip from IPv4Allocation where ip = INET_ATON(%s)"""
            if self.db_query_one(sql, (ip,)) is None:
                return False
            else:
                return True
        else:
            return True

    def LinkNetworkInterface(self, object_id, interface, switch_name, interface_switch):
        """Link two devices togetger"""
        # Get interface id
        port_id = self.GetInterfaceId(object_id, interface)
        if port_id is not None:
            # Get switch object ID
            switch_object_id = self.GetObjectId(switch_name)
            if switch_object_id is not None:
                switch_port_id = self.GetInterfaceId(switch_object_id, interface_switch)
                if switch_port_id is not None:
                    if switch_port_id > port_id:
                        select_object = 'portb'
                    else:
                        select_object = 'porta'

                    # Check server interface, update or create new link
                    sql = """SELECT %s FROM Link WHERE porta = %s OR portb = %s"""
                    result = self.db_query_one(sql, (select_object, port_id, port_id))
                    if result is None:
                        # Check if switch port is connected to another server
                        sql = """SELECT porta,portb FROM Link WHERE porta = %s OR portb = %s"""
                        result = self.db_query_one(sql, (switch_port_id, switch_port_id))
                        if result is not None:
                            # Get ports id of old link
                            old_link_a, old_link_b = result
                            old_link_a_dict = self.GetPortDeviceNameById(old_link_a)
                            old_link_b_dict = self.GetPortDeviceNameById(old_link_b)

                            # Clean switchport connection
                            sql = "DELETE FROM Link WHERE porta = %s OR portb = %s"
                            params = (switch_port_id, switch_port_id)
                            self.db_insert(sql, params)

                            # Log message to both device
                            text = "Disconnected %s,%s from %s,%s" % (old_link_a_dict['device_name'], old_link_a_dict['port_name'], old_link_b_dict['device_name'], old_link_b_dict['port_name'])
                            self.InsertLog(self.GetObjectId(old_link_a_dict['device_name']), text)
                            self.InsertLog(self.GetObjectId(old_link_b_dict['device_name']), text)

                        # Insert new connection
                        sql = """INSERT INTO Link (porta,portb) VALUES (%s,%s)"""
                        params = (port_id, switch_port_id)
                        self.db_insert(sql, params)
                        resolution = True

                        # Log it to both devices
                        device_dict = self.GetPortDeviceNameById(port_id)
                        switch_dict = self.GetPortDeviceNameById(switch_port_id)
                        text = "New connection %s,%s with %s,%s" % (device_dict['device_name'], device_dict['port_name'], switch_dict['device_name'], switch_dict['port_name'])
                        self.InsertLog(self.GetObjectId(device_dict['device_name']), text)
                        self.InsertLog(self.GetObjectId(switch_dict['device_name']), text)
                    else:
                        # Update old connection
                        old_switch_port_id = result[0]
                        if old_switch_port_id != switch_port_id:
                            # Clean previous link first
                            # Check and clean previous link (port_id)
                            sql = """SELECT porta,portb FROM Link WHERE porta = %s OR portb = %s"""
                            result = self.db_query_one(sql, (port_id, port_id))
                            if result is not None:
                                # Get ports id of old link
                                old_link_a, old_link_b = result
                                old_link_a_dict = self.GetPortDeviceNameById(old_link_a)
                                old_link_b_dict = self.GetPortDeviceNameById(old_link_b)

                                # Clean switchport connection
                                sql = """DELETE FROM Link WHERE porta = %s OR portb = %s"""
                                self.db_insert(sql, (port_id, port_id))

                                # Log message to both device
                                text = "Disconnected %s,%s from %s,%s" % (old_link_a_dict['device_name'], old_link_a_dict['port_name'], old_link_b_dict['device_name'], old_link_b_dict['port_name'])
                                self.InsertLog(self.GetObjectId(old_link_a_dict['device_name']), text)
                                self.InsertLog(self.GetObjectId(old_link_b_dict['device_name']), text)

                            # Insert new connection
                            sql = """INSERT INTO Link (porta,portb) VALUES (%s,%s)"""
                            self.db_insert(sql, (switch_port_id, port_id))

                            # Log all three devices
                            old_switch_dict = self.GetPortDeviceNameById(old_switch_port_id)
                            switch_dict = self.GetPortDeviceNameById(switch_port_id)
                            device_dict = self.GetPortDeviceNameById(port_id)
                            text = "Update connection from %s,%s to %s,%s" % (old_switch_dict['device_name'], old_switch_dict['port_name'], switch_dict['device_name'], switch_dict['port_name'])
                            self.InsertLog(self.GetObjectId(device_dict['device_name']), text)

                            text = "%s,%s changed connection from %s,%s and connected to %s,%s" % (device_dict['device_name'], device_dict['port_name'], old_switch_dict['device_name'], old_switch_dict['port_name'], switch_dict['device_name'], switch_dict['port_name'])
                            self.InsertLog(self.GetObjectId(old_switch_dict['device_name']), text)
                            self.InsertLog(self.GetObjectId(switch_dict['device_name']), text)

                            resolution = True
                        resolution = None

                else:
                    resolution = None
            else:
                resolution = None

        else:
            resolution = None

        return resolution

    def ObjectGetIpv4IPList(self,object_id):
        ''' Get list of IPv4 IP from object '''
        sql = """SELECT INET_NTOA(ip) AS ip from IPv4Allocation where object_id = %s"""
        return self.db_query_all(sql, (object_id,))

    def ObjectGetIpv6IPList(self,object_id):
        ''' Get list of IPv6 IP from object '''
        sql = """SELECT HEX(ip) AS ip from IPv6Allocation where object_id = %s"""
        return self.db_query_all(sql, (object_id,))

    def InterfaceGetIpv4IP(self, object_id, interface):
        """ Get list of IPv4 IP from interface """
        sql = """SELECT INET_NTOA(ip) AS ip from IPv4Allocation where object_id = %s AND name = %s"""
        return self.db_query_all(sql, (object_id, interface))

    def InterfaceGetIpv6IP(self, object_id, interface):
        """ Get list of IPv6 IP from interface """
        sql = """SELECT HEX(ip) AS ip from IPv6Allocation where object_id = %s AND name = %s"""
        return self.db_query_all(sql, (object_id, interface))

    def InterfaceAddIpv4IP(self, object_id, device, ip):
        """Add/Update IPv4 IP on interface"""

        sql = """SELECT INET_NTOA(ip) from IPv4Allocation WHERE object_id = %s AND name = %s"""
        result = self.db_query_all(sql, (object_id, device))

        if result is not None:
            old_ips = result

        is_there = "no"

        for old_ip in old_ips:
            if old_ip[0] == ip:
                is_there = "yes"

        if is_there == "no":
            sql = """SELECT name FROM IPv4Allocation WHERE object_id = %s AND ip = INET_ATON(%s)"""
            result = self.db_query_all(sql, (object_id, ip))

            if result is not None:
                if result != ():
                    sql = """DELETE FROM IPv4Allocation WHERE object_id = %s AND ip = INET_ATON(%s)"""
                    self.db_insert(sql, (object_id, ip))
                    self.InsertLog(object_id, "Removed IP (%s) from interface %s" % (ip, result[0][0]))

            sql = """INSERT INTO IPv4Allocation (object_id,ip,name) VALUES (%s,INET_ATON(%s),%s)"""
            self.db_insert(sql, (object_id, ip, device))
            text = "Added IP %s on %s" % (ip, device)
            self.InsertLog(object_id, text)

    def InterfaceAddIpv6IP(self, object_id, device, ip):
        """Add/Update IPv6 IP on interface"""
        # Create address object using ipaddress
        addr6 = ipaddress.IPv6Address(ip)
        # Create IPv6 format for Mysql
        ip6 = "".join(str(x) for x in addr6.exploded.split(':')).upper()

        sql = """SELECT HEX(ip) FROM IPv6Allocation WHERE object_id = %s AND name = %s"""
        result = self.db_query_all(sql, (object_id, device))

        if result is not None:
            old_ips = result

        is_there = "no"

        for old_ip in old_ips:
            if old_ip[0] == ip6:
                is_there = "yes"

        if is_there == "no":
            sql = """SELECT name FROM IPv6Allocation WHERE object_id = %s AND ip = UNHEX(%s)"""
            result = self.db_query_all(sql, (object_id, ip6))

            if result is not None:
                if result != ():
                    sql = """DELETE FROM IPv6Allocation WHERE object_id = %s AND ip = UNHEX(%s)"""
                    self.db_insert(sql, (object_id, ip6))
                    self.InsertLog(object_id, "Removed IP (%s) from interface %s" % (ip, result[0][0]))

            sql = """INSERT INTO IPv6Allocation (object_id,ip,name) VALUES (%s,UNHEX(%s),%s)"""
            self.db_insert(sql, (object_id, ip6, device))
            text = "Added IPv6 IP %s on %s" % (ip, device)
            self.InsertLog(object_id, text)
