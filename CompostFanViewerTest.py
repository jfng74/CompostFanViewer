from Tkinter import *
import pygubu


class Application:
    def __init__(self, master):
        self.master = master

        # create builder
        self.builder = builder = pygubu.Builder()

        # load ui file
        builder.add_from_file('CompostFanViewer.ui')

        # create a widget, using master as parent
        self.mainwindow = builder.get_object('CompostFanWidget', master)

        self.bt_relais = builder.get_object('bt_relais_update')

        self.notebook_node = builder.get_object('notebook_node')
        self.notebook_node.bind('<<NotebookTabChanged>>', self.notebook_node_tab_change)
        self.bt_relais.config(state="normal")
        self.en_relais_t_consigne = builder.get_object('en_relais_t_consigne')

        self.en_relais_t_consigne.delete(0, END)
        self.en_relais_t_consigne.insert(0, '10')

        # Connect callbacks
        builder.connect_callbacks(self)

    def on_button_relais_clicked(self):
        self.master.quit()

    def notebook_node_tab_change(self, event=None):
        print ('notebook_tab_change')


if __name__ == '__main__':
    root = Tk()
    app = Application(root)
    root.mainloop()
