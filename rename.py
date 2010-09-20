# Copyright (C) 2010 Elijah Rutschman <elijahr@gmail.com>, GPL v3

import gedit
import gtk
import os
import urllib

class RenameCurrentFilePlugin(gedit.Plugin):

    line_tools_str = """
        <ui>
            <menubar name="MenuBar">
                <menu name="FileMenu" action="File">
                    <placeholder name="FileOps_3">
	                    <menuitem action="RenameCurrentFile"/>
                    </placeholder>
                </menu>
            </menubar>
        </ui>
        """
    bookmarks = {}
    
    def __init__(self):
        gedit.Plugin.__init__(self)
        
    def activate(self, window):
        actions = [
            ('RenameCurrentFile', None, '_Rename File', '<Alt><Control>r', 
             'Completely remove the current line and retains cursor offset', 
             self.rename_current_file),
        ]
        windowdata = dict()
        window.set_data("RenameCurrentFilePluginWindowDataKey", windowdata)
        windowdata["action_group"] = gtk.ActionGroup(
            "GeditRenameCurrentFilePluginActions")

        windowdata["action_group"].add_actions(actions, window)
        manager = window.get_ui_manager()
        manager.insert_action_group(windowdata["action_group"], -1)
        windowdata["ui_id"] = manager.add_ui_from_string(self.line_tools_str)
        window.set_data("RenameCurrentFilePluginInfo", windowdata)
        
    def deactivate(self, window):
        windowdata = window.get_data("RenameCurrentFilePluginWindowDataKey")
        manager = window.get_ui_manager()
        manager.remove_ui(windowdata["ui_id"])
        manager.remove_action_group(windowdata["action_group"])

    def update_ui(self, window):
        view = window.get_active_view()
        windowdata = window.get_data("RenameCurrentFilePluginWindowDataKey")
        windowdata["action_group"].set_sensitive(bool(view and view.get_editable()))

    def rename_current_file(self, action, window):
        document = window.get_active_document()
        old_uri = document.get_uri()

        dialog = gtk.FileChooserDialog("Rename current file as...", None,
                gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_uri(old_uri)

        if dialog.run() == gtk.RESPONSE_OK:
            new_uri = dialog.get_uri()
            encoding = document.get_encoding()
            document.save_as(new_uri, encoding, gedit.DOCUMENT_SAVE_PRESERVE_BACKUP)
            # a lil hack to convert the uri to a path.  what if uri is not a fs path? 
            # whats the better way?
            if old_uri:
                path = old_uri.replace('file://', '')
                path = urllib.url2pathname(path)
                os.remove(path)

        dialog.destroy()

