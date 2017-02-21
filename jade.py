#!/usr/bin/python
try:
    from j import AK

except Exception as err:
    print("Ops something went wrong: " + str(err))

import subprocess
import sys
import os
import pwd
import xdg.Menu
import xdg.DesktopEntry
try:
    import gi
except ImportError:
    print("PyGObject not found")
    sys.exit(0)

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2, GLib, GObject, Gio, Gdk


userName = pwd.getpwuid(os.getuid())[4]
userName = userName.replace(",", " ")

def diskUsage():
    list = []
    getDiskUsage = os.popen('df --total')
    for entry in getDiskUsage:
        if entry.startswith("total"):

            list.append(entry)
            percentage = list[0].split("%")[0].strip().split(" ")[-1].strip()
            diskusage = "<div style='font-size: 12px;'>Storage</div>" + "<div style='font-size: 18px;padding: 1px;'>" + percentage + "%</div><div style='font-size: 12px;'>Used</div>"
            return diskusage

with open('ui.html','r') as file:
    html = file.read()

def fetchIcon(iconName):

    if iconName.endswith(".png" or ".svg"):
        return iconName

    else:
        try:
            def checkIcon(iconName):
                checkIcon = Gtk.IconTheme.get_default().has_icon(iconName)

                if checkIcon == True:
                    pass

                else:
                    iconName = "stock_dialog-error"

                return iconName

            checkIcon(iconName)

            iconName = Gtk.IconTheme.get_default().lookup_icon(iconName, 64, 0)
            iconName = iconName.get_filename()

            if iconName == None or iconName.endswith(".xpm"):
                iconName = "stock_dialog-error"
                iconName = Gtk.IconTheme.get_default().lookup_icon(iconName, 64, 0)
                iconName = iconName.get_filename()

            return iconName

        except Exception as err:
            print("Something went wrong loading application icon: " + str(err))
            pass
#schemas = Gio.Settings.list_schemas ()
#settings = Gio.Settings('com.deepin.wrap.gnome.desktop.interface')
#font = settings.get_string('font-name')
#test = settings.list_children()
#for item in schemas:
 #   print(item)
#print(test)
html = '''%s''' % (html % (fetchIcon("app-launcher"), diskUsage(), fetchIcon("emblem-favorite"), fetchIcon("document-open-recent"), fetchIcon("file-manager"), fetchIcon("org.gnome.Software"), fetchIcon("system-settings"), fetchIcon("deepin-terminal"), userName, fetchIcon("system-users"), fetchIcon("system-log-out"), fetchIcon("system-shutdown"), fetchIcon("system-reboot"), fetchIcon("system-hibernate"), fetchIcon("system-suspend"), fetchIcon("system-hibernate"), fetchIcon("distributor-logo-manjaro"),))

AK.Api.html = html
AK.Api.html += "<div id='search-icon'><img src='%s'></div>" % (fetchIcon("search"))

def get_menu(menu, depth=0):

    category = menu.getName()
    category = category.lower()
    category = category.replace(" ", "-")
    menuIcon = "applications-" + menu.getName().lower()

    if menuIcon == "applications-education":
        menuIcon = "applications-science"

    elif menuIcon == None:
        menuIcon = "applications-other"

    if depth == 0:
        pass

    else:
        category_description = ""
        if category == "games":
            category_description = "Break time, let's play some games!"

        elif category == "accessories":
            category_description = "Useful bits & bobs"

        elif category == "development":
            category_description = "Change the world, build awesome software!"

        elif category == "education":
            category_description = "Knowledge is power, educate yourself!"

        elif category == "graphics":
            category_description = "Get those creative juices flowing!"

        elif category == "internet":
            category_description = "Be social, go online and talk to everyone!"

        elif category == "multimedia":
            category_description = "Listen to music, watch a film, or create your next masterpiece!"

        elif category == "office":
            category_description = "I know! this sucks, get to work!"

        elif category == "system":
            category_description = "Administer your system and change configurations!"

        AK.Api.html += "<div id='%s" % (category) + "-msg' class='category-msg'><h5>%s<br>%s</h5><img class='category-icon %s' src='%s'></div>" % (category, category_description, menu.getName(), fetchIcon(menuIcon))
        AK.Api.html += "<div id='%s' class='category-container row'>" % (category)
        AK.Api.html += "<li class='application-category %s'><a href='#' onclick=\"display('#%s, #%s-msg ');grid('#%s');\">" % (category, category, category, category) + menu.getName() + "</a></li>"

    depth += 1
    for entry in menu.getEntries():
        if isinstance(entry, xdg.Menu.Menu):
            get_menu(entry, depth)

        elif isinstance(entry, xdg.Menu.MenuEntry):
            terminal = entry.DesktopEntry.getTerminal()
            if terminal == "true":
                pass
            else:
                app_exec = entry.DesktopEntry.getExec()
                app_icon = entry.DesktopEntry.getIcon()
                app_exec = app_exec.split('%')[0].strip()

                app_id = entry.DesktopEntry.getName()
                app_name = app_id

                app_id = app_id.lower()
                app_id = app_id.replace(" ", "-")
                app_id = app_id.replace(")", " ")
                app_id = app_id.replace("(", " ")
                app_id = app_id.replace("/", "-")
                generic_name = entry.DesktopEntry.getGenericName()
                app_comment = entry.DesktopEntry.getComment()
                #keywords = entry.DesktopEntry.getKeywords()

                #print(keywords)

                AK.Api.html += "<div class='application-wrapper col l4 xl3' id='%s'>" % (app_id)
                AK.Api.html += "<a class='application-box card'  href = 'shell:%s'>" %(app_exec)
                AK.Api.html += "<img class='application-icon' src='%s'>" % (fetchIcon(app_icon))
                AK.Api.html += "<img class='info-icon' src='%s'>" % (fetchIcon("help-faq"))
                AK.Api.html += "<h5 class='application-name card'>%s</h5>" % (app_name)

                if app_comment == "":
                    app_comment = "Description not available."

                if generic_name == "":
                    generic_name = "Generic name not available."

                AK.Api.html += "<p class='application-comment'>Application description:<br>%s<br><br>%s</p></a></div>" % (generic_name, app_comment)


    AK.Api.html += "</div>"

def menu():
    menu = xdg.Menu.parse('/etc/xdg/menus/manjaro-applications.menu')
    get_menu(menu)

menu()

def recentlyUsed(application = None):
    recentManager = Gtk.RecentManager.get_default()

    AK.Api.html += "<div id='recently-used-files' class='col m12'><div class='box row'><div class='center recent-files-msg'>Recently Used Files <a id='recent-files-button-close' href='#'>Close</a></div>"

    if application != None:
        pass

    for item in recentManager.get_items():

            itemName = item.get_uri().split("/")[-1].strip()
            itemPath = item.get_uri()
            uri = "xdg-open:" + itemPath
            AK.Api.html += "<div class='used-container-files col l4 xl3 center'><a href = ' " + uri + "'><img src='%s'><div class='filename'>" % (fetchIcon("font")) + itemName + "</div></a></div>"
         #content_type = Gio.content_type_from_mime_type(mime)
          #icon = Gio.content_type_get_icon(content_type)
        #AK.Api.html += "<a href = ' " + uri + "'><img src='%s'><h6>"  % (fetchIcon("font")) + itemName +"<h6></a>"

        #print(icon)


    AK.Api.html += "</div></div>"

recentlyUsed()

AK.Api.html += "</body></html>"

class Jade(AK.AppWindow):

  def __init__(self):
    super(Jade,self).__init__()

    def on_decide_policy(webview, decision, decision_type):

          if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:

              navigation_action = decision.get_navigation_action()
              navigation_request = navigation_action.get_request()
              navigation_type = navigation_action.get_navigation_type()
              uri = navigation_request.get_uri()

              if uri.startswith("shell:"):
                    uri = uri.replace('shell:', '')

                    subprocess.Popen(uri, shell=True)
                    decision.ignore()
                    return True

              elif uri.startswith("xdg-open:"):
                    uri = uri.replace('xdg-open:', 'xdg-open ')
                    print(uri)
                    subprocess.Popen(uri, shell=True)
                    decision.ignore()
                    return True

          return False
    self.webview.run_javascript("var jade='test'")
    self.webview.run_javascript("var jade.window='test'")
    self.webview.connect("decide-policy", on_decide_policy)
    settings = self.webview.get_settings()
    settings.set_enable_smooth_scrolling(self)



w = Jade()
w.add(Jade())
w.connect('destroy', Gtk.main_quit)
w.show_all()
Gtk.main()



