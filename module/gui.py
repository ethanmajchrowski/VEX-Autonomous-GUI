import pygame as pg
import pygame_gui
import pygame_gui.elements.ui_button
import pygame_gui.elements.ui_label
from module.sequence import SequenceType, sequence_types, SequencePath

# Alignment	Anchors
# Center	                            {"center": "center"}
# Top-Left	                            {"topleft": "topleft"}
# Top-Center	                        {"midtop": "midtop"}
# Top-Right	                            {"topright": "topright"}
# Center-Left	                        {"midleft": "midleft"}
# Center-Right	                        {"midright": "midright"}
# Bottom-Left	                        {"bottomleft": "bottomleft"}
# Bottom-Center	                        {"midbottom": "midbottom"}
# Bottom-Right	                        {"bottomright": "bottomright"}
# Stretch Full Width (Fixed Height)	    {"left": "left", "right": "right", "top": "top"}
# Stretch Full Height (Fixed Width)	    {"top": "top", "bottom": "bottom", "left": "left"}
# Stretch Full Screen	                {"left": "left", "right": "right", "top": "top", "bottom": "bottom"}

class UIManager:
    def __init__(self, screen_size: tuple[int, int]):
        """
        Creates UIManager for all UI.
        Arguments:
            screen_size: dimensions of display window
        """
        self.manager = pygame_gui.UIManager(screen_size)
        self.manager.get_theme().load_theme(r'assets\themes\arguments.json')

        self.showing_add_dialogue = False
        self.showing_arguments_dialogue = False
        self.showing_events_dialogue = False
        self.open_dialogue = False
        self.showing_toolbar_dropdown = False

        self.selected_item: None | SequenceType = None
        self.arguments_UI_list = []
        self.arguments_list = []
        self.properties_list = []

        self.events_list = []
        self.event_config = []
        self.selected_config: None | int = None

        w, h = screen_size
        left_width = int(w * 0.25)
        center_width = int(w * 0.5)
        right_width = int(w * 0.25)

        # Store UI rect
        class rect:
            LEFT_PANEL_RECT = pg.Rect(0, 0, left_width, h)
            DISPLAY_RECT = pg.Rect(0, 0, w, h)
            RIGHT_PANEL_RECT = pg.Rect(w - right_width, 0, right_width, h)
            CENTER_PANEL_RECT = pg.Rect(left_width, 0, center_width, h)
        self.rect = rect

        # Store UI components
        class panel:
            left_panel = pygame_gui.elements.UIPanel(manager=self.manager,
                relative_rect=self.rect.LEFT_PANEL_RECT)

            right_panel = pygame_gui.elements.UIPanel(manager=self.manager,
                relative_rect=(self.rect.DISPLAY_RECT.w-self.rect.RIGHT_PANEL_RECT.w, 0,
                               self.rect.RIGHT_PANEL_RECT.w, self.rect.DISPLAY_RECT.h))

            center_panel = pygame_gui.elements.UIPanel(manager=self.manager,
                relative_rect=pg.Rect(self.rect.LEFT_PANEL_RECT.w, 0,
                                    self.rect.CENTER_PANEL_RECT.w, self.rect.CENTER_PANEL_RECT.h))
            center_panel.hide()

            add_dialogue = pygame_gui.elements.UIPanel(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 200, 200),
                container=center_panel,
                anchors={"center": "center"},
                visible = self.showing_add_dialogue, starting_height=2)
            
            properties = pygame_gui.elements.UIPanel(manager=self.manager,
                relative_rect=pg.Rect(5, 5, 
                    right_panel.get_relative_rect().w-10, 220), 
                container=right_panel,
                parent_element=right_panel,
                anchors={"top": "top", "left": "left", "right": "right"},
                visible = True)

            arguments = pygame_gui.elements.UIPanel(manager=self.manager,
                relative_rect=pg.Rect(5, 0, 
                    right_panel.get_relative_rect().w-10, 40), 
                container=right_panel,
                parent_element=right_panel,
                anchors={"left": "left", "right": "right", "top_target": properties},
                visible = True)
        
            arguments_dialogue = pygame_gui.elements.UIPanel(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 300, 400),
                container=center_panel,
                anchors={"center": "center"})

            arguments_scroll = pygame_gui.elements.UIScrollingContainer(manager=self.manager,
                relative_rect=pg.Rect(0, 50, 
                    right_panel.get_relative_rect().w-10, right_panel.get_relative_rect().h-150-15-55-100),
                container=arguments,
                anchors={"left": "left", "right": "right"},
                allow_scroll_x=False,
                should_grow_automatically=True)

            properties_scroll = pygame_gui.elements.UIScrollingContainer(manager=self.manager,
                relative_rect=pg.Rect(2, 20,
                    right_panel.get_relative_rect().w-20, properties.get_relative_rect().h - 30),
                container=properties,
                anchors={"left": "left", "right": "right"},
                allow_scroll_x=False,
                should_grow_automatically=True)
            
            file_dropdown = pygame_gui.elements.UIPanel(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 70, 140),
                container=left_panel, starting_height=3)
            file_dropdown.hide()

            path_events_dialogue = pygame_gui.elements.UIPanel(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 0.99*self.rect.CENTER_PANEL_RECT.w, 0.99*self.rect.CENTER_PANEL_RECT.h),
                container=center_panel,
                anchors={"center": "center"})
            path_events_dialogue.show()

            path_events_scroll = pygame_gui.elements.UIScrollingContainer(manager=self.manager,
                relative_rect=pg.Rect(0, 30, 
                    path_events_dialogue.get_relative_rect().w-10, right_panel.get_relative_rect().h-150-15-55-100),
                container=path_events_dialogue,
                anchors={"left": "left", "right": "right"},
                allow_scroll_x=False,
                should_grow_automatically=True)
            path_events_dialogue.hide()

            event_config_popup = pygame_gui.elements.UIPanel(manager=self.manager,
                relative_rect=pg.Rect(0, 0, (2/3)*self.rect.CENTER_PANEL_RECT.w, (2/3)*self.rect.CENTER_PANEL_RECT.h),
                container=center_panel,
                anchors={"center": "center"})
            
        self.panel = panel

        class labels:
            coord_label = pygame_gui.elements.UILabel(manager=self.manager,
                container=self.panel.right_panel,
                relative_rect=pg.Rect(0, -20, 170, 25),
                anchors={"centerx": "centerx", "bottom": "bottom"},
                text="(0, 0)"
            )

            add_sequence_dialogue_title = pygame_gui.elements.UILabel(manager=self.manager,
                container=self.panel.add_dialogue,
                relative_rect=pg.Rect(0, 0, 120, 20),
                anchors={"centerx": "centerx", "top": "top"},
                text="Add New")

            properties_title = pygame_gui.elements.UILabel(manager=self.manager,
                container=self.panel.properties,
                relative_rect=pg.Rect(0, 0, 100, -1),
                anchors={"centerx": "centerx", "top": "top"},
                text="Properties")

            arguments_title = pygame_gui.elements.UILabel(manager=self.manager,
                container=self.panel.arguments,
                relative_rect=pg.Rect(0, 0, 100, -1),
                anchors={"centerx": "centerx", "top": "top"},
                text="Arguments")
            
            add_arguments_dialogue_title = pygame_gui.elements.UILabel(manager=self.manager,
                container=self.panel.arguments_dialogue,
                relative_rect=pg.Rect(0, 0, -1, -1),
                anchors={"centerx": "centerx", "top": "top"},
                text="Add non-default argument")

            events_dialogue_title = pygame_gui.elements.UILabel(manager=self.manager,
                relative_rect=pg.Rect(0, 0, -1, -1),
                text="Manage path events",
                anchors={"centerx": "centerx", "top": "top"},
                container=self.panel.path_events_dialogue)
            
            arguments_UI_list = []
        
        self.labels = labels

        class element:
            file_dropdown = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, -1, -1),
                text="File", container=self.panel.left_panel)

            self.panel.file_dropdown.set_anchors({"top_target": file_dropdown})

            file_new = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 64, -1),
                text="New", container=self.panel.file_dropdown, starting_height=3,
                parent_element=self.panel.file_dropdown)
            file_open = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 64, -1),
                text="Open", container=self.panel.file_dropdown, parent_element=self.panel.file_dropdown, 
                starting_height=3,
                anchors={"top_target": file_new})
            file_save = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 64, -1),
                text="Save", container=self.panel.file_dropdown, parent_element=self.panel.file_dropdown, 
                starting_height=3,
                anchors={"top_target": file_open})
            file_save_as = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 64, -1),
                text="Save As", container=self.panel.file_dropdown, parent_element=self.panel.file_dropdown, 
                starting_height=3,
                anchors={"top_target": file_save})
            file_export = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 64, -1),
                text="Export", container=self.panel.file_dropdown, parent_element=self.panel.file_dropdown, 
                starting_height=3,
                anchors={"top_target": file_save_as})
            
            view_dropdown = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, -1, -1),
                text="View", container=self.panel.left_panel, anchors={"left_target": file_dropdown})
            run_dropdown = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, -1, -1),
                text="Run", container=self.panel.left_panel, anchors={"left_target": view_dropdown})
            
            sequence_add_button = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, self.rect.LEFT_PANEL_RECT.w//4, 40),
                text="Add", 
                container=self.panel.left_panel,
                anchors={'top_target': file_dropdown})
            sequence_add_button.set_tooltip("Add new item to the sequence.")
            
            sequence_remove_button = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, self.rect.LEFT_PANEL_RECT.w//4, 40),
                text="Remove", 
                container=self.panel.left_panel,
                anchors={'top_target': file_dropdown, 'left_target': sequence_add_button})
            sequence_remove_button.set_tooltip("Remove selected item from the sequence.")
            
            sequence_move_up_button = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, self.rect.LEFT_PANEL_RECT.w//4, 40),
                text="Up", 
                container=self.panel.left_panel,
                anchors={'top_target': file_dropdown, 'left_target': sequence_remove_button})
            sequence_move_up_button.set_tooltip("Move selected item up in the sequence.")
            
            sequence_move_down_button = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, self.rect.LEFT_PANEL_RECT.w//4, 40),
                text="Down", 
                container=self.panel.left_panel,
                anchors={'top_target': file_dropdown, 'left_target': sequence_move_up_button})
            sequence_move_down_button.set_tooltip("Move selected item down in the sequence.")
            
            arguments_add_button = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, self.rect.RIGHT_PANEL_RECT.w, 30),
                text="Add Argument", 
                container=self.panel.arguments,
                anchors={"top_target": self.labels.arguments_title})
            arguments_add_button.set_tooltip("Open a list of arguments to change.")
            
            sequence_list = pygame_gui.elements.UISelectionList(manager=self.manager,
                relative_rect=pg.Rect(0, 
                    file_dropdown.relative_rect.h + sequence_add_button.relative_rect.h + 10, 
                    self.rect.LEFT_PANEL_RECT.w-5, self.rect.LEFT_PANEL_RECT.h - 100),
                item_list=[], allow_multi_select=False,
                container=self.panel.left_panel,
                anchors={"left": "left", "right": "right", "top": "top", "bottom": "bottom"})
            
            r = self.panel.add_dialogue.get_abs_rect()
            r2 = self.labels.add_sequence_dialogue_title.get_abs_rect()
            add_dialogue_options_list = pygame_gui.elements.UISelectionList(manager=self.manager,
                relative_rect=pg.Rect(0, r2.h, r.w-10, r.h-r2.h-10),
                container=self.panel.add_dialogue,
                item_list=sequence_types
            )

            r = self.panel.arguments_dialogue.get_abs_rect()
            r2 = self.labels.add_arguments_dialogue_title.get_abs_rect()
            add_argument_dialogue_options = pygame_gui.elements.UISelectionList(manager=self.manager,
                relative_rect=pg.Rect(0, r2.h, r.w-10, r.h-r2.h-10),
                container=self.panel.arguments_dialogue,
                item_list=[])
            
            path_events_button = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, -40, 170, 25),
                text="Events", 
                container=self.panel.right_panel,
                anchors={"bottom": "bottom", "centerx": "centerx"},
            )
            path_events_button.hide()

            path_events_add_function_event_button = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 20, 20),
                text="F",
                container=self.panel.path_events_dialogue)
            
            path_events_add_variable_event_button = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(22, 0, 20, 20),
                text="V",
                container=self.panel.path_events_dialogue)

            event_config_close_button = pygame_gui.elements.UIButton(manager=self.manager,
                relative_rect=pg.Rect(0, 0, 20, 20),
                text="<",
                container=self.panel.event_config_popup)
        
        self.element = element

        self.rescale(screen_size)
        self.changed_selection(None)

    def update_pos(self, mouse_world_pos):
        """
        Updates content of position label.
        Arguments:
            mouse_world_pos: position of mouse cursor in world
        """
        self.labels.coord_label.set_text(str(mouse_world_pos))

    def refresh_sequence(self, sequence: list[SequenceType]):
        """
        Updates contents of sequence list.
        Arguments:
            sequence: sequence list of commands
        """
        self.element.sequence_list.set_item_list([])
        for item in sequence:
            self.element.sequence_list.add_items([f"[{item.symbol}] {item.properties["name"]}"])
    
    def add_sequence_item(self, item: SequenceType) -> None:
        """Adds sequence element with correct format to sequence"""
        self.element.sequence_list.add_items([f"[{item.symbol}] {item.properties["name"]}"])

    def update(self, time_delta):
        """
        Updates misc things, like panel visibilities. Also updates pygame_gui.UIManager
        """
        self.manager.update(time_delta)
    
    def toggle_add_dialogue(self):
        self.open_dialogue = not self.showing_add_dialogue

        if self.showing_add_dialogue:
            self.panel.add_dialogue.hide()
            self.showing_add_dialogue = False
        else:
            self.panel.add_dialogue.show()
            self.open_dialogue = True
            self.showing_add_dialogue = True

        self.element.add_dialogue_options_list.set_item_list(sequence_types)

    def draw(self, surf: pg.Surface):
        """
        Draws UI onto surface.
        Arguments:
            screen: display surface to draw all UI on.
        """
        self.manager.draw_ui(surf)

    def changed_selection(self, selection: None | SequenceType) -> None:
        """
        User changed selected sequence function. Update data in properties and arguments.
        """
        self.selected_item = selection
        if selection is None:
            self.panel.arguments.hide()
            self.panel.properties.hide()
            self.panel.arguments_scroll.hide()
            self.element.path_events_button.hide()
        else:
            self.panel.arguments.show()
            self.panel.properties.show()
            self.panel.arguments_scroll.show()
        
            self.update_custom_arguments()
            self.update_arguments()
            self.update_properties()

            if type(selection) == SequencePath:
                self.element.path_events_button.show()
            else:
                self.element.path_events_button.hide()

            if len(self.arguments_list) == 0:
                self.element.arguments_add_button.hide()
            else:
                self.element.arguments_add_button.show()
    
    def toggle_argument_dialogue(self) -> None:
        self.open_dialogue = not self.showing_arguments_dialogue

        if self.showing_arguments_dialogue:
            self.panel.arguments_dialogue.hide()
            self.showing_arguments_dialogue = False
        else:
            # get list of strings from self.arguments_list
            item_list = []
            for to_add_item in self.arguments_list:
                # check for any already added arguments that may have a incompatible list
                if 'incompatible_with' in to_add_item:
                    for item in self.selected_item.custom_args:
                        if item in to_add_item['incompatible_with']:
                            break
                    else:
                        item_list.append((to_add_item["value"][0], to_add_item["value"][1]))
                else:
                    item_list.append((to_add_item["value"][0], to_add_item["value"][1]))
            
            self.element.add_argument_dialogue_options.set_item_list(item_list)
            self.panel.arguments_dialogue.show()
            self.showing_arguments_dialogue = True
    
    def update_arguments(self) -> None:
        """
        Update the argument dictionary with proper & consistent format from the selected item.
        """
        # simple format: {"value": ('bool backwards: False', 'backwards')}
        # complex format: {"value": ('bool backwards: False', 'backwards'), "incompatible_with": ["name"], ...}
        output = []
        args = self.selected_item.format["arguments"]
        for item in args:
            if item not in self.selected_item.custom_args:
                if type(args[item]) == list:
                    output.append({"value": (f"{args[item][0].__name__} {item}: {args[item][1]}", item)})
                else:
                    # complex format
                    entry = {}
                    if type(args[item]['value'][0]) == tuple:
                        # this is a list argument (list, item_type)
                        entry["value"] = (f"list[{args[item]["value"][0][1].__name__}] {item}: []", item)
                    else:
                        entry["value"] = (f"{args[item]["value"][0].__name__} {item}: {args[item]["value"][1]}", item)
                    for setting in args[item]:
                        if setting != "value":
                            entry[setting] = args[item][setting]

                    valid = True
                    if 'incompatible_with' in entry:
                        for invalid in self.selected_item.custom_args:
                            if invalid in entry['incompatible_with']:
                                valid = False
                    
                    if valid:
                        output.append(entry)
        self.arguments_list = output

        if len(self.arguments_list) == 0:
            self.element.arguments_add_button.hide()
        else:
            self.element.arguments_add_button.show()

    def update_custom_arguments(self):
        """
        Setup custom arguments to be modified in the arguments panel.
        (text labels and text entry)
        """
        for label in self.arguments_UI_list:
            for item in label:
                item.kill()
        self.arguments_UI_list = []

        w = self.panel.arguments.get_relative_rect().w//2
        for i, arg in enumerate(self.selected_item.custom_args):
            if type(self.selected_item.custom_args[arg]) == dict:
                l = self.selected_item.custom_args[arg]["value"]
            else:
                l = self.selected_item.custom_args[arg]
            
            if type(l[0]) == tuple:
                text = f"list[{l[0][1].__name__}] {arg}"
            else:
                text = f"{l[0].__name__} {arg}"
            label = pygame_gui.elements.UILabel(
                manager=self.manager,
                relative_rect=pg.Rect(0, (i*20)+10, -1, 20),
                container=self.panel.arguments_scroll,
                text=text)
            
            tooltip_list = []
            for complex_arg in self.selected_item.custom_args[arg]:
                if complex_arg != "value":
                    tooltip_list.append(f"{complex_arg}: {self.selected_item.custom_args[arg][complex_arg]}\n")
            if tooltip_list:
                label.set_tooltip("".join(tooltip_list), wrap_width=200)

            w = self.panel.arguments_scroll.get_relative_rect().w - label.get_relative_rect().w - 25

            initial_text = str(l[1])
            if type(l[1]) == list:
                initial_text = ""
                for item in l[1]:
                    initial_text += str(item) + " "
                
            text_box = pygame_gui.elements.UITextEntryLine(
                manager=self.manager,
                relative_rect=pg.Rect(label.relative_rect.w+2, (i*20)+10, w, 20),
                container=self.panel.arguments_scroll,
                initial_text=initial_text,
                object_id=pygame_gui.core.ObjectID(class_id="@normal")
            )

            if l[0] == int:
                text_box.set_allowed_characters(["-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
            if l[0] == float:
                text_box.set_allowed_characters(["-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."])
            if type(l[0]) == tuple:
                if l[0][1] == int:
                    text_box.set_allowed_characters(["-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", " "])
                if l[0][1] == float:
                    text_box.set_allowed_characters(["-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", " "])
            remove_button = pygame_gui.elements.UIButton(
                manager=self.manager,
                relative_rect=pg.Rect(text_box.get_relative_rect().w + label.get_relative_rect().w, (i*20)+10,
                                      20, 20),
                text="X",
                container=self.panel.arguments_scroll,
            )
            remove_button.set_tooltip("Reset this argument to default.")

            self.arguments_UI_list.append((label, text_box, remove_button))
    
    def update_properties(self):
        """
        Updates the contents of the properties panel based off the properties 
        dictionary within the selected item.
        """
        for item in self.properties_list:
            if type(item) == tuple:
                for component in item:
                    component.kill()
            else:
                item.kill()
            
        self.properties_list = []

        for i, item in enumerate(self.selected_item.properties):
            data = self.selected_item.properties[item] # [obj, name, value]
            if data[0] == "list":
                # list item, show a small panel with scrollable options
                dropdown = pygame_gui.elements.UIDropDownMenu(
                    manager=self.manager,
                    relative_rect=pg.Rect(0, (i*20)+10, self.panel.arguments_scroll.get_relative_rect().w-10, 30),
                    container=self.panel.properties_scroll,
                    options_list=["Select option", *data[1]],
                    starting_option="Select option")
                self.properties_list.append(dropdown)
            if data[0] == "value" or (item == "name" and not self.selected_item.properties['name'] == "InitialPose"):
                text = f"{type(data[3]).__name__} {item}"

                label = pygame_gui.elements.UILabel(
                    manager=self.manager,
                    relative_rect=pg.Rect(0, (i*20)+10, -1, 20),
                    container=self.panel.properties_scroll,
                    text=text)
                w = self.panel.arguments_scroll.get_relative_rect().w - label.get_relative_rect().w
                if item == "name":
                    data = data
                else:
                    data = data[3]
                text_box = pygame_gui.elements.UITextEntryLine(
                    manager=self.manager,
                    relative_rect=pg.Rect(label.relative_rect.w+2, (i*20)+10, w, 20),
                    container=self.panel.properties_scroll,
                    initial_text=str(data),
                    object_id=pygame_gui.core.ObjectID(class_id="@normal")
                )
                if type(data) == int:
                    text_box.set_allowed_characters(["-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
                if type(data) == float:
                    text_box.set_allowed_characters(["-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."])
                self.properties_list.append((label, text_box))

    def toggle_events_dialogue(self):
        self.open_dialogue = not self.showing_events_dialogue

        if self.showing_events_dialogue:
            self.panel.path_events_dialogue.hide()
            self.showing_events_dialogue = False
        else:
            self.panel.path_events_dialogue.show()
            self.showing_events_dialogue = True
        
        self.update_events_list()
    
    def update_events_list(self):
        if type(self.selected_item) == SequencePath and self.showing_events_dialogue:
            for item in self.events_list:
                for component in item: component.kill()
            self.events_list = []
            
            for i, item in enumerate(self.selected_item.events):
                del_button = pygame_gui.elements.UIButton(manager=self.manager,
                    relative_rect=pg.Rect(0, i*30, 20, 20),
                    text="X",
                    container=self.panel.path_events_scroll)
                name = pygame_gui.elements.UILabel(manager=self.manager,
                    relative_rect=pg.Rect(22, i*30, -1, 20),
                    text=f"{item["name"]}",
                    container=self.panel.path_events_scroll)
                event_pos_button = pygame_gui.elements.UIButton(manager=self.manager,
                    relative_rect=pg.Rect(self.panel.path_events_scroll.get_relative_rect().w-40, i*30, 20, 20),
                    text="P",
                    container=self.panel.path_events_scroll)
                event_config_button = pygame_gui.elements.UIButton(manager=self.manager,
                    relative_rect=pg.Rect(self.panel.path_events_scroll.get_relative_rect().w-40-25, i*30, 20, 20),
                    text="C",
                    container=self.panel.path_events_scroll)
                self.events_list.append((del_button, name, event_pos_button, event_config_button))

    def update_event_config(self, i):
        event = self.selected_item.events[i]
        for item in self.event_config:
            item[0].kill()
            item[1].kill()
        self.event_config = []

        # draw out info in event
        layer = self.panel.event_config_popup.get_top_layer() + 1
        if event['type'] == 'variable':
            name_label = pygame_gui.elements.UILabel(manager=self.manager,
                relative_rect=pg.Rect(0, 20, -1, -1),
                container=self.panel.event_config_popup,
                text="name: ")
            name_label.change_layer(layer)

            name_text_box = pygame_gui.elements.UITextEntryLine(manager=self.manager,
                relative_rect=pg.Rect(0, 20, self.panel.event_config_popup.get_abs_rect().w-20, 20),
                anchors={"left_target": name_label},
                initial_text=event['name'],
                container=self.panel.event_config_popup)
            name_text_box.change_layer(layer)

            value_label = pygame_gui.elements.UILabel(manager=self.manager,
                relative_rect=pg.Rect(0, 0, -1, -1),
                container=self.panel.event_config_popup,
                text="value: ",
                anchors={"top_target": name_label})
            value_label.change_layer(layer)

            value_text_box = pygame_gui.elements.UITextEntryLine(manager=self.manager,
                relative_rect=pg.Rect(0, 0, self.panel.event_config_popup.get_abs_rect().w-20, 20),
                anchors={"left_target": name_label, "top_target": name_label},
                initial_text=str(event['value']),
                container=self.panel.event_config_popup)
            value_text_box.change_layer(layer)

            self.event_config.append((name_label, name_text_box))
            self.event_config.append((value_label, value_text_box))

        elif event['type'] == 'function':
            name_label = pygame_gui.elements.UILabel(manager=self.manager,
                relative_rect=pg.Rect(0, 20, -1, -1),
                container=self.panel.event_config_popup,
                text="name: ")
            name_label.change_layer(layer)

            name_text_box = pygame_gui.elements.UITextEntryLine(manager=self.manager,
                relative_rect=pg.Rect(0, 20, self.panel.event_config_popup.get_abs_rect().w-20, 20),
                anchors={"left_target": name_label},
                initial_text=event['name'],
                container=self.panel.event_config_popup)
            name_text_box.change_layer(layer)

            args_label = pygame_gui.elements.UILabel(manager=self.manager,
                relative_rect=pg.Rect(0, 0, -1, -1),
                container=self.panel.event_config_popup,
                text="args: ",
                anchors={"top_target": name_label})
            args_label.change_layer(layer)

            args_text_box = pygame_gui.elements.UITextEntryLine(manager=self.manager,
                relative_rect=pg.Rect(0, 0, self.panel.event_config_popup.get_abs_rect().w-20, 20),
                anchors={"left_target": name_label, "top_target": name_label},
                initial_text=str(event['args']),
                container=self.panel.event_config_popup)
            args_text_box.change_layer(layer)

            object_label = pygame_gui.elements.UILabel(manager=self.manager,
                relative_rect=pg.Rect(0, 0, -1, -1),
                container=self.panel.event_config_popup,
                text="object: ",
                anchors={"top_target": args_label})
            object_label.change_layer(layer)

            object_text_box = pygame_gui.elements.UITextEntryLine(manager=self.manager,
                relative_rect=pg.Rect(0, 0, self.panel.event_config_popup.get_abs_rect().w-20, 20),
                anchors={"left_target": object_label, "top_target": args_label},
                initial_text=str(event['obj']),
                container=self.panel.event_config_popup)
            object_text_box.change_layer(layer)

            self.event_config.append((name_label, name_text_box))
            self.event_config.append((args_label, args_text_box))
            self.event_config.append((object_label, object_text_box))

    def rescale(self, new_size: tuple[int, int]):
        """
        Rescales UI (if window is scaled).
        Arguments:
            new_size: new dimensions of window.
        """
        w, h = new_size

        left_width = int(w * 0.25)
        center_width = int(w * 0.5)
        right_width = int(w * 0.25)

        self.rect.DISPLAY_RECT = pg.Rect(0, 0, w, h)
        self.rect.LEFT_PANEL_RECT = pg.Rect(0, 0, left_width, h)
        self.rect.RIGHT_PANEL_RECT = pg.Rect(w - right_width, 0, right_width, h)
        self.rect.CENTER_PANEL_RECT = pg.Rect(left_width, 0, center_width, h)

        self.panel.left_panel.set_dimensions((left_width, h))

        self.panel.right_panel.set_dimensions((right_width, h))
        self.panel.right_panel.set_position((w-right_width, 0))

        self.panel.center_panel.set_dimensions((center_width, h))
        self.panel.center_panel.set_position((right_width, 0))

        self.panel.arguments.set_dimensions((self.panel.right_panel.get_relative_rect().w-10, 
                                             self.panel.right_panel.get_relative_rect().h-150-15))

        self.element.sequence_add_button.set_dimensions((left_width//4, 40))
        self.element.sequence_remove_button.set_dimensions((left_width//4, 40))
        self.element.arguments_add_button.set_dimensions((self.rect.RIGHT_PANEL_RECT.w, 30))

        w, h = (2/3)*self.rect.CENTER_PANEL_RECT.w, (2/3)*self.rect.CENTER_PANEL_RECT.h
        self.panel.path_events_dialogue.set_dimensions((w, h))
        self.panel.path_events_scroll.set_dimensions((w-12, h-40))
        self.update_events_list()

        self.changed_selection(self.selected_item)

        self.manager.set_window_resolution(new_size)
