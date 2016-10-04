#!/usr/bin/env python

import sys
import lxml.etree

ns = {
    'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
    'edm': 'http://docs.oasis-open.org/odata/ns/edm',
}

types = {}
actions = {}

required_types = [
    'ServiceRoot.1.0.0.ServiceRoot',
    'ComputerSystem.1.0.0.ComputerSystem',
]

required_actions = [
    'ComputerSystem.Reset',
]

def qualified_classname_to_python(name):
    return name.replace('.', '_')

class Property(object):
    prop_class = 'odata.ODataProperty'
    collection_class = 'odata.ODataCollectionProperty'

    def __init__(self, name):
        self.name = name
        self.nav = False
        self.collection_type = None
        self.cls = self.prop_class

    def render(self):
        attrs = {}
        if self.nav:
            attrs['nav'] = 'True'
        if self.collection_type:
            cls = self.collection_class
            attrs['type'] = repr(self.collection_type)
        else:
            cls = self.prop_class
        attr_string = ''.join([', %s=%s' % (k, v) for (k, v) in attrs.items() ])
        return "%s('%s'%s)" % (cls, self.name, attr_string)

    @classmethod
    def parse(cls, elem):
        prop = cls(elem.get('Name'))
        t = elem.get('Type')
        if elem.tag == ('{%s}NavigationProperty' % ns['edm']):
            prop.nav = True
        if t.endswith('Collection'):
            prop.collection_type = t
        return prop

class Action(object):
    action_class = 'odata.ODataAction'

    def __init__(self, name):
        self.name = name

    def render(self):
        print 'class %s(%s):' % (
                qualified_classname_to_python(self.name), self.action_class)
        print '\tpass'

    @classmethod
    def parse(cls, namespace, elem):
        action = cls(namespace + '.' + elem.get('Name'))
        return action

class EntityType(object):
    odata_class = 'odata.ODataObject'

    def __init__(self, name):
        self.parent = None
        self.name = name
        self.properties = []
        self.navigation_properties = []
        self.rendered = False

    def merge(self, other):
        if not other:
            return
        assert(other.name == self.name)
        self.properties += other.properties

    def render(self):
        global types
        if self.rendered:
            return
        parent_name = self.odata_class
        if self.parent:
            parent = types.get(self.parent, None)
            if parent is None:
                raise Exception("No such type %s" % self.parent)
            parent.render()
            parent_name = qualified_classname_to_python(self.parent)
        print "class %s(%s):" % (qualified_classname_to_python(self.name),
                parent_name)
        print
        print '\tclass ODataProperties:'
        if not self.properties or self.navigation_properties:
            print '\t\tpass'
        for prop in self.properties:
            print '\t\t%s = %s' % (prop.name.lower(), prop.render())
        for prop in self.navigation_properties:
            print '\t\t%s = %s' % (prop.name.lower(), prop.render())

        print
        print '\tclass Meta:'
        print '\t\ttype = \'%s\'' % (self.name)
        print
        self.rendered = True


    @classmethod
    def parse(cls, namespace, elem):
        et = cls(namespace + '.' + elem.get('Name'))
        et.parent = elem.get('BaseType')
        for prop_elem in elem.xpath('edm:Property', namespaces=ns):
            prop = Property.parse(prop_elem)
            et.properties.append(prop)
        for prop_elem in elem.xpath('edm:NavigationProperty', namespaces=ns):
            prop = Property.parse(prop_elem)
            et.properties.append(prop)
        return et


def handle_dataservice(ds):
    for schema in ds.xpath('edm:Schema', namespaces=ns):
        schema_namespace = schema.get('Namespace')
        for et in schema.xpath('edm:EntityType', namespaces=ns):
            et = EntityType.parse(schema_namespace, et)
#et.merge(types.get(et.name, None))
            types[et.name] = et
        for action in schema.xpath('edm:Action', namespaces=ns):
            action = Action.parse(schema_namespace, action)
            actions[action.name] = action



def process_file(filename):
    tree = lxml.etree.parse(open(filename))
    for ds in tree.xpath('/edmx:Edmx/edmx:DataServices', namespaces=ns):
        handle_dataservice(ds)

def main():

    print 'import odata'
    print

    for arg in sys.argv[1:]:
        process_file(arg)

    for t in required_types:
        types[t].render()
        
    for a in required_actions:
        actions[a].render()

if __name__ == '__main__':
    sys.exit(main())
