"""
The neo4django test suite. Currently, these are rough development-oriented tests,
and need to be expanded to be more robust- say, with legitimate data source
cleaning for setup/teardown, which will be tough.
"""

import datetime

Person = neo4django = gdb = neo4jrestclient = neo_constants = settings = None

def setup():
    global Person, neo4django, gdb, neo4jrestclient, neo_constants, settings

    from neo4django.tests import Person, neo4django, gdb, neo4jrestclient, \
            neo_constants, settings

def teardown():
    gdb.cleandb()
        

def test_save_delete():
    """Basic sanity check for NodeModel save and delete.  """
    from neo4jrestclient.client import NotFoundError

    pete = Person(name='Pete')
    pete.save()
    node_id = pete.id
    pete.delete()
    try:
        gdb.nodes.get(node_id)
    except NotFoundError:
        pass
    else:
        assert False, 'Pete was not properly deleted.'

def test_prop():
    pete = Person(name='Pete')
    assert pete.name == 'Pete'
    pete.save()
    assert pete.name == 'Pete'
    pete.name = 'Peter'
    assert pete.name == 'Peter'
    pete.save()
    assert pete.name == 'Peter'

def test_none_prop():
    """Confirm that `None` and null verification work properly."""
    pete = Person()
    pete.save()
    assert pete.name is None
    
    class NotNullPerson(neo4django.NodeModel):
        class Meta:
            app_label = 'test'
        name = neo4django.StringProperty(null=False)
    try:
        andy = NotNullPerson(name = None)
        andy.save()
    except:
        pass
    else:
        raise AssertionError('Non-nullable field accepted `None` as a value.')

def test_integer():
    def try_int(integer):
        node = Person(name="SandraInt", age=integer)
        node.save()
        assert node.age == integer
        node.delete()

    for i in [0,1,-1,28,neo4django.properties.MAX_INT,neo4django.properties.MIN_INT]:
        try_int(i)
    
def test_date_constructor():
    #TODO
    pass

def test_date_prop():
    #TODO
    pass

def test_datetime_constructor():
    """Confirm `DateTimeProperty`s work from a NodeModel constructor."""
    #TODO cover each part of a datetime
    class DateTimeNode(neo4django.NodeModel):
        datetime = neo4django.DateTimeProperty()

    time = datetime.datetime.now()
    d = DateTimeNode(datetime = time)
    assert d.datetime == time
    d.save()
    assert d.datetime == time

def test_datetime_auto_now():
    from time import sleep
    class BlogNode(neo4django.NodeModel):
        title = neo4django.Property()
        date_modified = neo4django.DateTimeProperty(auto_now = True)
    timediff = .6 #can be this far apart
    ##Confirm the date auto sets on creation
    b = BlogNode(title = 'Snake House')
    b.save()
    time1 = datetime.datetime.now()
    test1, test2 = get_times(time1, b.date_modified)
    print b.date_modified
    assert abs(test1-test2) <= timediff
    ##Confirm the date auto sets when saved and something changes
    sleep(timediff)
    b.title = 'BEEEEEEEES!'
    b.save()
    time2 = datetime.datetime.now()
    test1, test2 = get_times(time2, b.date_modified)
    print b.date_modified
    assert abs(test1-test2) <= timediff
    ##Confirm the date auto sets when saved and nothing changes
    sleep(timediff)
    b.save()
    time3 = datetime.datetime.now()
    test1, test2 = get_times(time3, b.date_modified)
    assert abs(test1-test2) <= timediff

def get_times(t1, t2):
    rv = [t1.second*1.0 + (t1.microsecond/10.0**6), t2.second*1.0 + (t2.microsecond/10.0**6)]
    if t1.minute - t2.minute == 1:
        rv[0] += 60
    elif t2.minute - t1.minute == 1:
        rv[1] += 60
    return rv

def test_datetime_auto_now_add():
    class BlogNode(neo4django.NodeModel):
        title = neo4django.Property()
        date_created = neo4django.DateTimeProperty(auto_now_add = True)
    timediff = .6
    ##Confrim date auto sets upon creation
    time1 = datetime.datetime.now()
    b = BlogNode(title = 'Angry birds attack buildings!')
    b.save()
    test1, test2 = get_times(time1, b.date_created)
    assert abs(test1-test2) <= .6
    time = b.date_created
    ##Confrim the date doesn't change when saved and something changes
    b.title = 'Ape uprising! NYC destroyed!'
    b.save()
    assert b.date_created == time
    ##Confirm the date doesn't change when saved and nothing changes
    b.save()
    assert b.date_created == time

def test_date_auto_now():
    class BlagNode(neo4django.NodeModel):
        title = neo4django.Property()
        date_changed = neo4django.DateProperty(auto_now = True)
    ##Confirm the date auto sets on creation
    b = BlagNode(title = 'Snookie House')
    b.save()
    date1 = datetime.date.today()
    assert b.date_changed == date1
    ##Confirm the date auto sets when saved and something changes
    b.title = 'BEEAAAARRSSSS!'
    b.save()
    date2 = datetime.date.today()
    assert b.date_changed == date2
    ##Confirm the date auto sets when saved and nothing changes
    b.save()
    date3 = datetime.date.today()
    assert b.date_changed == date3

def test_date_auto_now_add():
    class BlegNode(neo4django.NodeModel):
        title = neo4django.Property()
        date_made = neo4django.DateProperty(auto_now_add = True)
    ##Confirm the date auto sets on creation
    b = BlegNode(title = "d")
    b.save()
    date1 = datetime.date.today()
    assert b.date_made == date1
    ##Confirm the date doesn't change when another property changes
    b.title = 'Whoreticulture'
    b.save()
    assert b.date_made == date1
    ##Confrim the date doesn't change when no other property changes
    b.save()
    assert b.date_made == date1

def test_type_nodes():
    """Tests for type node existence and uniqueness."""
    class TestType(neo4django.NodeModel):
        class Meta:
            app_label = 'type_node_test'

    n1 = TestType()
    n1.save()

    class TestType(neo4django.NodeModel):
        class Meta:
            app_label = 'type_node_test'

    n2 = TestType()
    n2.save()

    class SecondTestType(TestType):
        class Meta:
            app_label = 'type_node_test2'

    n3 = SecondTestType()
    n3.save()

    class SecondTestType(TestType):
        class Meta:
            app_label = 'type_node_test2'

    n4 = SecondTestType()
    n4.save()

    test_type_nodes = filter(
        lambda n: (n['app_label'], n['model_name']) == ('type_node_test','TestType'),
        gdb.traverse(types=[neo4jrestclient.Outgoing.get('<<TYPE>>')],
                     stop=neo_constants.STOP_AT_END_OF_GRAPH))
    assert len(test_type_nodes) != 0, 'TestType type node does not exist.'
    assert len(test_type_nodes) <= 1, 'There are multiple TestType type nodes.'

    test_type_nodes = filter(
        lambda n: (n['app_label'], n['model_name']) == ('type_node_test2','SecondTestType'),
        gdb.traverse(types=[neo4jrestclient.Outgoing.get('<<TYPE>>')],
                     stop=neo_constants.STOP_AT_END_OF_GRAPH))

    assert len(test_type_nodes) != 0, 'SecondTestType type node does not exist.'
    assert len(test_type_nodes) <= 1, 'There are multiple SecondTestType type nodes.'

def test_model_inheritance():
    #TODO docstring
    class TypeOPerson(Person):
        class Meta:
            app_label = 'newapp'
        hobby = neo4django.Property()

    jake = TypeOPerson(name='Jake', hobby='kayaking')
    jake.save()
    assert jake.hobby == 'kayaking'
   
def test_nodemodel_independence():
    """Tests that NodeModel subclasses can be created and deleted independently."""

    class TestSubclass(neo4django.NodeModel):
        age = neo4django.IntegerProperty()
    
    n1 = TestSubclass(age = 5)
    n1.save()

    class TestSubclass(neo4django.NodeModel):
        pass
    
    n2 = TestSubclass()

    assert not hasattr(n2, 'age'), "Age should not be defined, as the new class didn't define it."

    n2.save()

    assert not hasattr(n2, 'age'),  "Age should not be defined, as the new class didn't define it."

def test_array_property_validator():
    """Tests that ArrayProperty validates properly."""
    #TODO Make this not suck/add other iterables. -Edd
    class ArrayNode(neo4django.NodeModel):
        vals = neo4django.ArrayProperty()

    n1 = ArrayNode(vals = (1, 2, 3))
    n1.save()
    n2 = ArrayNode(vals = [1, 2, 3])
    n2.save()
    try:
        n3 = ArrayNode(vals = {'1':1, '2':2, '3':3})
        n3.save()
    except:
        pass
    else:
        raise AssertionError('dicts should not work')
    try:
        n4 = ArrayNode(vals = 'hurrr')
        n4.save()
    except:
        pass
    else:
        raise AssertionError('strings should not work')

def test_int_array_property_validator():
    """Tests that IntArrayProperty validates properly."""
    class StrArrayNode(neo4django.NodeModel):
        vals = neo4django.IntArrayProperty()

    n1 = StrArrayNode(vals = (1,2,3))
    n1.save()
    try:
        n2 = StrArrayNode(vals = ('1','2','3'))
        n2.save()
    except:
        pass
    else:
        raise AssertionError('tuples of strs should not work')

def test_str_array_property_validator():
    """Tests that StringArrayProperty validates properly."""
    class StrArrayNode(neo4django.NodeModel):
        vals = neo4django.StringArrayProperty()

    try:
        n2 = StrArrayNode(vals = (1,2,3,))
        n2.save()
    except:
        pass
    else:
        raise AssertionError('tuples of ints should not work')

def test_url_array_property_validator():
    """Tests that StringArrayProperty validates properly."""
    class URLArrayNode(neo4django.NodeModel):
        vals = neo4django.URLArrayProperty()

    n1 = URLArrayNode(vals = ('http://google.com',
                              'https://afsgdfvdfgdf.eu/123/asd',
                              'file://onetwothree.org/qwerty/123456'))
    n1.save()
    try:
        n2 = URLArrayNode(vals = (1,2,3,))
        n2.save()
    except:
        pass
    else:
        raise AssertionError('tuples of ints should not work')
