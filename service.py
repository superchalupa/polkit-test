import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
class HelloWorld(dbus.service.Object):
    def __init__(self, conn=None, object_path=None, bus_name=None):
        dbus.service.Object.__init__(self, conn, object_path, bus_name)
        self.dbus_info = dbus.Interface(conn.get_object("org.freedesktop.DBus",
                    "/org/freedesktop/DBus/Bus", False),
                "org.freedesktop.DBus")
        self.polkit = dbus.Interface(dbus.SystemBus().get_object(
                    "org.freedesktop.PolicyKit1",
                    "/org/freedesktop/PolicyKit1/Authority", False),
                "org.freedesktop.PolicyKit1.Authority")

       
    @dbus.service.method(dbus_interface="com.example.HelloWorld", in_signature="s", out_signature="s", sender_keyword="sender", connection_keyword="conn")
    def SayHello(self, name, sender=None, conn=None):
        print("enter")
        is_auth = self._check_polkit_privilege(sender, conn, "com.example.HelloWorld.auth", {"AllowUserInteraction": "true", "theirname": name})
        print("is_auth: ", is_auth)
        print("return")
        if is_auth:
            return "Hello " + name
        return "UNAUTHORIZED"

    def _check_polkit_privilege(self, sender, conn, privilege, details):
        # Get Peer PID
        pid = self.dbus_info.GetConnectionUnixProcessID(sender)
     
        # Check auth against polkit; if it times out, try again
        try:
            auth_response = self.polkit.CheckAuthorization(
                ("unix-process", {"pid": dbus.UInt32(pid, variant_level=1),
                                  "start-time": dbus.UInt64(0, variant_level=1)}),
                privilege, details, dbus.UInt32(1), "", timeout=600)
            print(auth_response)
            (is_auth, is_chal, respDetails) = auth_response
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
     
        print("Successful authorization: ", is_auth, is_chal, respDetails)
        return True


if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    name = dbus.service.BusName("com.example.HelloWorld", bus)
    helloworld = HelloWorld(bus, "/HelloWorld")
    mainloop = GLib.MainLoop()
    mainloop.run()


