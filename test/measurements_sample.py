import datetime
from c8y_app import CumulocityApi
from c8y_model import Count, Meters, Value, Device, Measurement

run_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')

c8y = CumulocityApi()

# create a device and obtain ID
d = Device(c8y, type='DemoClient')
d.add_fragment('c8y_DemoClient')
d.store()
device_id = c8y.inventory.get_all(fragment='c8y_DemoClient')[0].id

m1 = Measurement(c8y, type='c8y_DemoMeasurement', source=device_id)
# simple custom fragments can be added directly, special sub structures can
# be added using standard dictionaries
m1.add_fragment('c8y_CustomFragment',
                user=c8y.username, message='Demo Measurement',
                special={'doc': {'k1': 1, 'k2': 2}})
# typical measurement fragment values can be added using the convenience classes
m1.add_fragment('c8y_DemoMeasurement', Iterations=Count(-1),
                L=Meters(12.4), X=Value(42, unit='x'))
# when stored without defined time, the current time will be used automatically
m1.store()

# subsequent measurements of the same kind
for i in range(0, 5):
    # fragments can be accessed using simple dot notification up to any depth
    # this works for assignments as well
    m1.c8y_CustomFragment.special.doc.k1 = 12
    m1.c8y_DemoMeasurement.Iterations.value = i
    # the time will be updated every time
    m1.store()

# querying the database
for m in c8y.measurements.select(type='c8y_DemoMeasurement', after=run_at, reverse=True):
    v = m.c8y_DemoMeasurement.Iterations.value
    u = m.c8y_DemoMeasurement.Iterations.unit
    t = m.time
    print(f"Got measurement at {t}: {v} {u}")
    # a measurement retrieved like this can be deleted directly
    m.delete()

# cleanup assets
# d.delete() does not work, because it is a new object without ID and no connection set
c8y.inventory.delete(device_id)


