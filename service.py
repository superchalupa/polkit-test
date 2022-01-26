import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
class HelloWorld(dbus.service.Object):
    def __init__(self, conn=None, object_path=None, bus_name=None):
        dbus.service.Object.__init__(self, conn, object_path, bus_name)
       
    @dbus.service.method(dbus_interface="com.example.HelloWorldInterface", in_signature="s", out_signature="s", sender_keyword="sender", connection_keyword="conn")
    def SayHello(self, name, sender=None, conn=None):
        return "Hello " + name

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    name = dbus.service.BusName("com.example.HelloWorld", bus)
    helloworld = HelloWorld(bus, "/HelloWorld")
    mainloop = GLib.MainLoop()
    mainloop.run()


def _check_polkit_privilege(self, sender, conn, privilege):
    # Get Peer PID
    if self.dbus_info is None:
        # Get DBus Interface and get info thru that
        self.dbus_info = dbus.Interface(conn.get_object("org.freedesktop.DBus",
                                                        "/org/freedesktop/DBus/Bus", False),
                                        "org.freedesktop.DBus")
    pid = self.dbus_info.GetConnectionUnixProcessID(sender)
 
    # Query polkit
    if self.polkit is None:
        self.polkit = dbus.Interface(dbus.SystemBus().get_object(
        "org.freedesktop.PolicyKit1",
        "/org/freedesktop/PolicyKit1/Authority", False),
                                     "org.freedesktop.PolicyKit1.Authority")
 
    # Check auth against polkit; if it times out, try again
    try:
        auth_response = self.polkit.CheckAuthorization(
            ("unix-process", {"pid": dbus.UInt32(pid, variant_level=1),
                              "start-time": dbus.UInt64(0, variant_level=1)}),
            privilege, {"AllowUserInteraction": "true"}, dbus.UInt32(1), "", timeout=600)
        print(auth_response)
        (is_auth, _, details) = auth_response
    except dbus.DBusException as e:
        if e._dbus_error_name == "org.freedesktop.DBus.Error.ServiceUnknown":
            # polkitd timeout, retry
            self.polkit = None
            return self._check_polkit_privilege(sender, conn, privilege)
        else:
            # it's another error, propagate it
            raise
 
    if not is_auth:
        # Aww, not authorized :(
        print(":(")
        return False
 
    print("Successful authorization!")
    return True
