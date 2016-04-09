from tkinter import *
from tkinter import ttk
from AWSExportImportManager import EndpointManager

class GraphicElementContainer(object):
    def __init__(self, component, reference_id, subsection):
        super().__init__()
        self.component = component
        self.reference_id = reference_id
        self.subsection = subsection

class UIObject(object):
    '''Base class for all user interface components'''

    def __init__(self, master, controller: object=None):
        self.frame = ttk.Frame(master)
        self.contr = controller

        self.frame.grid(column=0, row=0)


class EntryField(UIObject):
    '''basic inputfield wrapped in a class'''

    def __init__(self, master, width_num=15):
        super().__init__(master)
        self.variable = StringVar()
        # self.frame = ttk.Frame(master)
        self.entry = ttk.Entry(self.frame, textvariable=self.variable, width=width_num)
        self.entry.grid(column=0, row=0)

    def set(self, value):
        self.variable.set(str(value))

    def get(self):
        return self.variable.get()



class ListTableRows(object):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.rows = {}

    def add(self, row: {}):
            self.rows[self.counter] = row
            self.counter += 1

    def get_rows(self):
            return self.rows

class LabelWithVariable(UIObject):
    def __init__(self, master, text):
        super().__init__(master, None)
        self.variable = StringVar()
        # self.label = ttk.Label(self.frame, textvariable=self.variable)
        self.label = Label(self.frame, textvariable=self.variable, anchor=NW)
        self.label.grid(column=0, row=0)


class CustomPanedWindow(UIObject):
    '''Paned'''

    def __init__(self, master, controller, vertical=True):
        super().__init__(master, controller)
        self.components = []
        if vertical:
            self.group = ttk.Panedwindow(self.frame, orient=VERTICAL)
            self.group.grid(column=0, row=0)
        else:
            self.group = ttk.Panedwindow(self.frame, orient=HORIZONTAL)
            self.group.grid(column=0, row=0)

    def add(self, reference_id, component_frame=None, component=None, subsection=None, from_array_to_labels=False,
            array=None):
        if from_array_to_labels:
            added_values_array = []
            for cell in array:
                if cell == "":
                    continue
                label = ttk.Label(self.group, text=cell)
                self.components.append(GraphicElementContainer(component=label,
                                                               reference_id=reference_id, subsection=subsection))
                added_values_array.append(cell)
                self.group.add(label)
        else:
            self.components.append(
                GraphicElementContainer(component=component, reference_id=reference_id, subsection=subsection))

            self.group.add(component_frame)

    def get(self, reference_id, subsection):
        for component in self.components:
            if component.reference_id == reference_id and component.subsection == subsection:
                return component
        return None

    def clear(self):
        self.components.clear()
        for child in self.group.panes():
            self.group.remove(child)

class ListTable(UIObject):
    def __init__(self, master, controller, headers=None):
        super().__init__(master, controller)
        if headers == None:
            headers = []
        self.columns = {}
        self.groups = {}
        self.access_data = {}
        self.entry_fields = []
        self.headers = headers
        self.data = {}
        self.identifiers = {}
        self.rows = ListTableRows()
        self.custom_components = []
        self.display_blocs = {}
        self.current_bloc = 1
        self.current_bloc_array = []

        for header in headers:
            self.columns[header] = ttk.Labelframe(self.frame, text=header)
            self.groups[header] = CustomPanedWindow(self.columns[header], self.contr)
            self.groups[header].frame.grid(column=0, row=0)

        column_num = 0
        row_num = 0

        for header in headers:
            self.columns[header].grid(column=column_num, row=row_num, sticky=(W, N))
            column_num = column_num + 1


    def clear(self):
        for key, value in self.groups.items():
            custom_paned_window = self.groups[key]
            custom_paned_window.group.grid_remove()

    def add(self, data: {}, unique_identifier):
        row = {'id': unique_identifier}
        for key, value in data.items():
            element = EntryField(self.groups[key].frame)
            element.set(value)
            self.entry_fields.append(element)

            self.groups[key].add(unique_identifier, element.frame, key)
            row[key] = value
            row[key + '-entryfield'] = element
        self.rows.add(row)
        # print(row)

class SkillList(UIObject):
    def __init__(self, master, controller, table_name, carbon_copies):
        super().__init__(master, controller)
        self.temporary_id = 0
        self.table_type = table_name

        self.carbon_copies = carbon_copies

        # ------------Scrollstuff----------
        self.canvas = Canvas(self.frame)
        self.frame2 = Frame(self.canvas)
        self.vsb = Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        # self.vsb.pack(side="right", fill="y")
        self.vsb.grid(column=1, row=0, sticky=(N, S))
        # self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.grid(column=0, row=0, sticky=(N, W))

        self.frame2.grid(column=0, row=0, sticky=(N, W))

        self.frame2.bind("<Configure>", self.on_frame_configure)

        self.list_table = ListTable(master=self.frame2, controller=None, headers=['name', 'stat', 'category',
                                                                                  'chippable', 'diff', 'short', 'cost',
                                                                                  'chip_lvl_cost', 'desc'])
        self.list_table.frame.grid(column=1, row=0)

        self.canvas.create_window((0, 0), window=self.frame2, anchor="nw", tags="self.frame2")
        self.canvas.update_idletasks()

    def on_frame_configure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=1000)
        self.canvas.update_idletasks()

    def save_to_aws(self):
        print('saving to aws..')
        rows = self.list_table.rows.get_rows()
        for s in self.carbon_copies:
            for key, s2 in rows.items():
                if s['name'] == s2['id']:

                    modified = is_skill_modified(s, s2)
                    if modified:
                        ep_mgr = EndpointManager()
                        stat = s2['stat-entryfield'].get()
                        category = s2['category-entryfield'].get()
                        desc = s2['desc-entryfield'].get()
                        chippable = s2['chippable-entryfield'].get()
                        diff = s2['diff-entryfield'].get()
                        short = s2['short-entryfield'].get()
                        chip_lvl_cost = s2['chip_lvl_cost-entryfield'].get()
                        cost = s2['cost-entryfield'].get()
                        ep_mgr.add_attribute_blueprint(name=s2['id'], stat=stat, category=category, desc=desc,
                                                       chippable=chippable, diff=diff, short=short,
                                                       chip_lvl_cost=chip_lvl_cost, cost=cost, blueprint_type=self.table_type)
                else:
                    pass
        print('saving complete')

def is_skill_modified(s1, s2):
    if s1['stat'] != s2['stat-entryfield'].get():
        print('modified: stat')
        return True
    if s1['category'] != s2['category-entryfield'].get():
        print('modified: category')
        return True
    if s1['chippable'] != s2['chippable-entryfield'].get():
        print('modified: chippable')
        return True
    if s1['diff'] != s2['diff-entryfield'].get():
        print('modified: diff')
        return True
    if s1['short'] != s2['short-entryfield'].get():
        print('modified: short')
        return True
    if s1['desc'] != s2['desc-entryfield'].get():
        print('modified: desc')
        return True
    if s1['chip_lvl_cost'] != s2['chip_lvl_cost-entryfield'].get():
        print('modified: chip_lvl')
        return True
    if s1['cost'] != s2['cost-entryfield'].get():
        print('modified: cost')
        return True
    # print('modified: false')
    return False


def main():
    start_graphical_interface(attribute_type='talent', master=None)


def start_graphical_interface(attribute_type:str, master=None):
    root = None
    if not master:
        root = Tk()
        root.title('attribute modifier 1.0')
    else:
        root = master
    frame = ttk.Frame(root)

    frame.grid(column=0, row=0)

    ep_mgr = EndpointManager()
    attributes = ep_mgr.get_attributes(attribute_type)
    global skill_table
    skill_table = SkillList(frame, None, attribute_type, attributes)
    for attribute in attributes:
        name = attribute['name']
        stat = attribute['stat']
        category = attribute['category']
        chippable = attribute['chippable']
        diff = attribute['diff']
        short = attribute['short']
        cost = attribute['cost']
        chip_lvl_cost = attribute['chip_lvl_cost']
        desc = attribute['desc']
        skill_table.list_table.add({'name': name, 'stat': stat, 'category': category, 'chippable': chippable,
                                    'diff': diff, 'short': short, 'cost': cost, 'chip_lvl_cost': chip_lvl_cost,
                                    'desc': desc}, name)
    btn_save = ttk.Button(text="save", command=skill_table.save_to_aws)
    btn_save.grid(column=0, row=1)
    if not master:
        root.mainloop()

if __name__ == '__main__':
    main()