import pygame as pg
from pygame.locals import *
from pygame_gui import UI_SELECTION_LIST_NEW_SELECTION, UI_BUTTON_PRESSED, UI_SELECTION_LIST_DROPPED_SELECTION, UI_TEXT_ENTRY_CHANGED
from pygame_gui.core import ObjectID

from module.utils import world_to_screen, screen_to_world
from module.curves import ComplexCurve
from module.gui import UIManager
import module.undo as undo
from module.sequence import *
from module.file import FileHandler

from simulation.pure_pursuit import PurePursuitSimulation

from math import dist, sin, cos, radians
from copy import deepcopy
from pyperclip import copy
from sys import exit

pg.init()
pg.font.init()
SCREEN_SIZE = (900, 600)
display_surface = pg.display.set_mode(SCREEN_SIZE, flags=RESIZABLE)
font = pg.font.Font(r"assets\font\Inter\static\Inter_18pt-Regular.ttf")
background = pg.image.load(r"assets\graphics\match.png").convert()
bg_width, bg_height = background.get_size()

offset = offset_x, offset_y = 150, 0
zoom = 0.3
scaled_bg = pg.transform.smoothscale(background, (int(bg_width * zoom), int(bg_height * zoom)))
WORLD_SIZE = int(1785*2)

ui_manager = UIManager(SCREEN_SIZE)
undo_manager = undo.UndoManager()
file_manager = FileHandler()
simulator = PurePursuitSimulation()

clock = pg.time.Clock()
sequence: list[SequenceType] = []

sequence.append(SequenceInitialPose())
ui_manager.element.sequence_list.add_items([f"[{sequence[0].symbol}] {sequence[0].properties["name"]}"])
selected_item: None | SequenceType = None

num_curves = 0

running = True
dragging_curve = False
dragging_map = False
selected_curve = None
selected_point = None
hovering_on_point = False
map_interaction = True
drag_start_offset = offset

while running:
    display_surface.fill((40, 40, 40))
    screen_mouse = pg.mouse.get_pos()

    mouse_pos = screen_to_world(screen_mouse, zoom, offset)
    mouse_pos = mouse_x, mouse_y = [int(mouse_pos[0]), int(mouse_pos[1])]
    mouse_buttons = pg.mouse.get_pressed()
    just_pressed = pg.mouse.get_just_pressed()
    mods = pg.key.get_mods()
    rel_x, rel_y = pg.mouse.get_rel()
    dt = clock.tick(60)/1000

    for event in pg.event.get():
        ui_manager.manager.process_events(event)

        if event.type == UI_SELECTION_LIST_DROPPED_SELECTION:
            if event.ui_element == ui_manager.element.sequence_list:
                for item in ui_manager.element.sequence_list.item_list:
                    if item['selected']:
                        break
                else:
                    selected_item = None
                    ui_manager.changed_selection(selected_item)

        if event.type == UI_SELECTION_LIST_NEW_SELECTION:
            # selected somehting in the sequence list
            if event.ui_element == ui_manager.element.sequence_list:
                # for each item in the sequence list
                for item in ui_manager.element.sequence_list.item_list:
                    # if this item is selected
                    if item['selected']:
                        for function in sequence:
                            if f"[{function.symbol}] {function.properties["name"]}" == item["text"]:
                                selected_item = function
                                # stop looking for other items
                                break
                        ui_manager.changed_selection(selected_item)

            # add sequence event
            if event.ui_element == ui_manager.element.add_dialogue_options_list:
                ui_manager.toggle_add_dialogue()
                map_interaction = True

                function = sequence_classes[sequence_types.index(event.text)]()

                if type(function) == SequencePath:
                    num_curves += 1
                    function.properties["name"] = f"Path {num_curves}"
                
                sequence.append(function)
                ui_manager.add_sequence_item(function)
            
            # add argument
            if event.ui_element == ui_manager.element.add_argument_dialogue_options:
                ui_manager.toggle_argument_dialogue()
                map_interaction = True

                arg = event.text.split(" ")[1][:-1]
                if arg in selected_item.format["arguments"] and arg not in selected_item.custom_args:
                    selected_item.custom_args[arg] = deepcopy(selected_item.format["arguments"][arg])
                    ui_manager.update_arguments()
                    ui_manager.update_custom_arguments()
            
            # change properties dropdown
            if event.ui_object_id == "panel.panel.scrolling_container.drop_down_menu.#drop_down_options_list":
                if type(selected_item) == SequenceMotor:
                    selected_item.properties['motor'][2] = event.text

        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == ui_manager.element.sequence_add_button:
                if not ui_manager.showing_add_dialogue:
                    ui_manager.toggle_add_dialogue()
                    map_interaction = False
            elif event.ui_element == ui_manager.element.sequence_remove_button:
                if selected_item is not None and type(selected_item) != SequenceInitialPose:
                    sequence.remove(selected_item)
                    ui_manager.element.sequence_list.remove_items([selected_item.properties["name"]])
                    selected_item = None
                    ui_manager.changed_selection(selected_item)
            elif event.ui_element == ui_manager.element.arguments_add_button:
                ui_manager.toggle_argument_dialogue()
                map_interaction = False
            elif event.ui_object_id == 'panel.panel.scrolling_container.button':
                # remove this argument from the custom list of the selected item
                for item in ui_manager.arguments_UI_list:
                    if item[2] == event.ui_element:
                        selected_item.custom_args.pop(item[0].text.split(" ")[1])
                        ui_manager.update_custom_arguments()
                        ui_manager.update_arguments()
            elif event.ui_element == ui_manager.element.file_dropdown:
                ui_manager.showing_toolbar_dropdown = not ui_manager.showing_toolbar_dropdown

                if ui_manager.showing_toolbar_dropdown:
                    ui_manager.panel.file_dropdown.show()
                    # ui_manager.panel.file_dropdown.change_layer(5)
                    # ui_manager.element.sequence_list.hide()
                else: 
                    ui_manager.panel.file_dropdown.hide()
                    # ui_manager.element.sequence_list.show()
            elif event.ui_element == ui_manager.element.file_save:
                file_manager.save(sequence)
                ui_manager.showing_toolbar_dropdown = False
                ui_manager.panel.file_dropdown.hide()

            elif event.ui_element == ui_manager.element.file_save_as:
                file_manager.save_as(sequence)
                ui_manager.showing_toolbar_dropdown = False
                ui_manager.panel.file_dropdown.hide()

            elif event.ui_element == ui_manager.element.file_export:
                print("\n", "*"*50)
                out = str(file_manager.export_lossy(sequence)).replace(" ", "")
                copy(out)
                print(f"Copied {len(out)} chars to clipboard!")
                ui_manager.showing_toolbar_dropdown = False
                ui_manager.panel.file_dropdown.hide()
            
            if event.ui_element == ui_manager.element.sequence_move_up_button:
                if selected_item is not None:
                    ind = sequence.index(selected_item)
                    if ind > 1:
                        item = sequence.pop(ind)
                        sequence.insert(ind-1, item)
                        ui_manager.refresh_sequence(sequence)
            if event.ui_element == ui_manager.element.sequence_move_down_button:
                if selected_item is not None and type(selected_item) != SequenceInitialPose:
                    ind = sequence.index(selected_item)
                    if ind + 1 < len(sequence):
                        item = sequence.pop(ind)
                        sequence.insert(ind+1, item)
                        ui_manager.refresh_sequence(sequence)
        
        # changed argument
        if event.type == UI_TEXT_ENTRY_CHANGED:
            for row in ui_manager.arguments_UI_list:
                # get type validation to work with complex arguments
                if event.ui_element in row:
                    value: str = event.text
                    argument = row[0].text.split(" ")[1] # get argument name
                    data = selected_item.custom_args[argument]["value"]
                    # try to converty to the data type
                    try:
                        if data[0] == bool:
                            if value.lower() in ["true", "false"]:
                                if value.lower() in ["true", "false"]:
                                    converted = (value.lower() == "true")
                            else:
                                raise ValueError
                        elif type(data[0]) == tuple:
                            converted = [data[0][1](item) for item in value.split(" ")]
                        else:
                            converted = data[0](value)  # Attempt conversion
                        
                        if 'valid_types' in selected_item.custom_args[argument]:
                            # if type(selected_item.custom_args[argument]['valid_types']) == tuple:
                            #     print(selected_item.custom_args[argument]['valid_types'])
                            if converted not in selected_item.custom_args[argument]['valid_types']:
                                raise ValueError
                        if 'incompatible_with' in selected_item.custom_args[argument]:
                            for item in selected_item.custom_args:
                                if item != argument:
                                    if item in selected_item.custom_args[argument]['incompatible_with']:
                                        raise ValueError
                        # set custom argument in selected item
                        selected_item.custom_args[argument]["value"][1] = converted
                        event.ui_element.change_object_id(ObjectID(class_id="@normal"))
                    except ValueError:
                        event.ui_element.change_object_id(ObjectID(class_id="@error"))

                    break

            for row in ui_manager.properties_list:
                if event.ui_element in row:
                    # check each key in properties
                    for item in selected_item.properties:
                        data = selected_item.properties[item]
                        value = event.text
                        
                        # we match with the row's text box at word 2 (name of property)
                        if item == (row[0].text.split(" ")[1]):
                            if item == "name":
                                selected_item.properties["name"] = str(value)
                                ui_manager.refresh_sequence(sequence)
                            else:
                                # validate the type of input
                                try:
                                    data_type = type(getattr(data[1], data[2]))
                                    if data_type == bool:
                                        if value.lower() in ["true", "false"]:
                                            converted = (value.lower() == "true")
                                        else:
                                            raise ValueError
                                    else:
                                        converted = data_type(value)  # Attempt conversion
                                    # valid input
                                    event.ui_element.change_object_id(ObjectID(class_id="@normal"))
                                    selected_item.properties[item][3] = converted
                                    setattr(data[1], data[2], data[3])

                                    # check to ensure we don't set spacing to 0, would be an infinite number of points :)
                                    if type(data[1]) == ComplexCurve:
                                        if converted == 0:
                                            setattr(data[1], data[2], 1)
                                            raise ValueError
                                        
                                        data[1].update_all_curves()
                                except ValueError:
                                    # invalid input
                                    event.ui_element.change_object_id(ObjectID(class_id="@error"))
        
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            # undo
            if event.key == K_z and mods & KMOD_CTRL:
                undo_manager.undo()
            
            # file management
            if event.key == K_s and mods & KMOD_CTRL and not mods & KMOD_SHIFT:
                file_manager.save(sequence)
            if event.key == K_s and mods & KMOD_CTRL and mods & KMOD_SHIFT:
                file_manager.save_as(sequence)
            if event.key == K_e and mods & KMOD_CTRL:
                print("\n", "*"*50)
                out = str(file_manager.export_lossy(sequence)).replace(" ", "")
                copy(out)
                print(f"Copied {len(out)} chars to clipboard!")

            # sequence
            if mods & KMOD_ALT:
                if event.key == K_p:
                    # Add PATH function
                    function = SequencePath()

                    num_curves += 1
                    function.properties["name"] = f"Path {num_curves}"
                    
                    sequence.append(function)
                    ui_manager.add_sequence_item(function)
                if event.key == K_m:
                    function = SequenceMotor()
                    sequence.append(function)
                    ui_manager.add_sequence_item(function)
                if event.key == K_f:
                    function = SequenceFlag()
                    sequence.append(function)
                    ui_manager.add_sequence_item(function)
            
        if event.type == MOUSEBUTTONUP:
            if dragging_map:
                dragging_map = False
            
            if event.button == 1:
                if dragging_curve:
                    dragging_curve = False
                    selected_curve.finalize_curve()
                    # selected_item.curve.sim = simulator.simulate_path(item)

                    # if we just tap on the point don't add to undo history
                    if type(undo_manager.history[-1]) == undo.point.PointMove:
                        new_pos = selected_curve.control_points[selected_point[0]][selected_point[1]]
                        if undo_manager.history[-1].pos_before == new_pos:
                            undo_manager.history.pop()
                elif type(selected_item) == SequencePath:
                    if not hovering_on_point and map_interaction:
                        # if we are clicking on the map panel
                        if ui_manager.rect.CENTER_PANEL_RECT.collidepoint(screen_mouse):
                            # if we haven't moved around
                            if drag_start_offset == offset:
                                # add a curve to the selected curve
                                selected_item.curve.add_curve(mouse_pos)
                                # ui_manager.refresh_sequence(sequence)
            
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [1, 2, 3]:
                if ui_manager.showing_toolbar_dropdown:
                    if not ui_manager.element.file_dropdown.get_abs_rect().collidepoint(screen_mouse) and not ui_manager.panel.file_dropdown.get_abs_rect().collidepoint(screen_mouse):
                        ui_manager.panel.file_dropdown.hide()
                        # ui_manager.element.sequence_list.show()
                        ui_manager.showing_toolbar_dropdown = False
                else:
                    if not dragging_map and not hovering_on_point and map_interaction and not ui_manager.open_dialogue:
                        if ui_manager.rect.CENTER_PANEL_RECT.collidepoint(screen_mouse):
                            dragging_map = True
                            drag_start_offset = offset
                    elif not map_interaction and ui_manager.open_dialogue: # check if we can't press map and have an open dialogue
                        # function dialogue
                        if ui_manager.showing_add_dialogue:
                            if not ui_manager.panel.add_dialogue.get_abs_rect().collidepoint(screen_mouse):
                                ui_manager.toggle_add_dialogue()
                                map_interaction = True

                        # argument dialogue
                        if ui_manager.showing_arguments_dialogue:
                            if not ui_manager.panel.arguments_dialogue.get_abs_rect().collidepoint(screen_mouse):
                                ui_manager.toggle_argument_dialogue()
                                map_interaction = True

        if event.type == VIDEORESIZE:
            ui_manager.rescale(pg.display.get_window_size())
        if event.type == MOUSEWHEEL:
            if not ui_manager.open_dialogue:
                if ui_manager.rect.CENTER_PANEL_RECT.collidepoint(screen_mouse):  # Only zoom if in map area
                    world_pos_before = screen_to_world(screen_mouse, zoom, offset)
            
                    # Adjust zoom based on scroll direction
                    zoom_factor = 1.1 if event.y > 0 else 0.9
                    new_zoom = zoom * zoom_factor
                    
                    # Prevent excessive zooming
                    if 0.25 < new_zoom < 5:
                        zoom = new_zoom
                        
                        # Calculate where the world position would be after zoom
                        new_screen_pos = world_to_screen(world_pos_before, zoom, offset)
                        
                        # Adjust offset to keep mouse over the same world position
                        offset_x += (screen_mouse[0] - new_screen_pos[0])
                        offset_y += (screen_mouse[1] - new_screen_pos[1])

                        scaled_bg = pg.transform.smoothscale(background, (int(bg_width * zoom), int(bg_height * zoom)))
                        offset = (offset_x, offset_y)

    # logic
    if dragging_curve:
        x, y = screen_mouse
        sel = selected_point

        new_pos = screen_to_world([x, y], zoom, offset)
        new_pos = [int(new_pos[0]), int(new_pos[1])]
        # if selected point is the same number in both spots (endpoint of curve)
        if sel[0] == sel[1]:
            # move our control point to new
            selected_curve.move_control(sel[0], new_pos)
        else:
            # this is a handle, not an endpoint
            selected_curve.control_points[sel[0]][sel[1]] = new_pos
        
        if overlap_index is not None:
            # move overlap point to new position
            selected_curve.parent.overlap_points[overlap_index] = new_pos
            # move connected curves start point to new position
            selected_curve.next_curve.move_control(0, new_pos)

        selected_curve.parent.update_all_curves()
        
    if dragging_map:
        offset_x += rel_x
        offset_y += rel_y
        offset = (offset_x, offset_y)

    # rendering
    bg_rect = scaled_bg.get_rect(topleft=offset)
    display_surface.blit(scaled_bg, bg_rect)

    hovering_on_point = False
    
    for item in sequence:
        if type(item) == SequencePath:
            complex_curve = item.curve
            for point in complex_curve.sim:
                pg.draw.circle(display_surface, (0, 0, 255), world_to_screen((point[0], -point[1]), zoom, offset), 2)
                # pg.draw.circle(display_surface, (0, 0, 255), world_to_screen((0, 0), zoom, offset), 10)

            # draw points
            complex_curve.draw(display_surface, zoom, offset)
            if selected_item == item:
                # do logic and stuff
                if map_interaction:
                    for curve in complex_curve.curves:
                        curve.draw_control(display_surface, zoom, offset)
                        if not dragging_curve:
                            control_points = [*curve.control_points[0], *curve.control_points[1]]
                            for control_point in control_points:
                                if dist(screen_mouse, world_to_screen(control_point, zoom, offset)) < 10 and not hovering_on_point:
                                    hovering_on_point = True
                                    pg.draw.circle(display_surface, (255, 0, 255), world_to_screen(control_point, zoom, offset), 7)
                                    
                                    selected_point = control_points.index(control_point)

                                    overlap_index = None
                                    if selected_point == 3:
                                        if control_point in complex_curve.overlap_points:
                                            overlap_index = complex_curve.overlap_points.index(control_point)

                                    if selected_point >= 2:
                                        selected_point = [1, curve.control_points[1].index(control_point)]
                                    else:
                                        selected_point = [0, curve.control_points[0].index(control_point)]
                                                            
                                    if just_pressed[0] and not dragging_curve:
                                    #     # start dragging_curve
                                        dragging_curve = True
                                        selected_curve = curve

                                        undo_manager.add_event(undo.point.PointMove(undo_manager, control_point, overlap_index, selected_curve, selected_point))
            # draw checkpoints
            if 'checkpoints' in item.custom_args:
                if type(item.custom_args['checkpoints']['value'][1]) == list:
                    for point in item.custom_args['checkpoints']['value'][1]:
                        curve = complex_curve.get_points()
                        if point < len(curve):
                            pos_x, pos_y = world_to_screen([curve[point][0], curve[point][1]], zoom, offset)
                            pg.draw.circle(display_surface, (0, 255, 255), (pos_x, pos_y), 10*zoom)

    # print(sequence[0].x, sequence[0].y)
    pg.draw.circle(display_surface, (0, 200, 200), world_to_screen((sequence[0].x, sequence[0].y), zoom, offset), 5)
    if selected_item == sequence[0]:
        angle = -radians(sequence[0].a - 90)
        pg.draw.line(display_surface, (255, 255, 255), world_to_screen((sequence[0].x, sequence[0].y), zoom, offset), 
                     world_to_screen((sequence[0].x+50*cos(angle), (sequence[0].y)+50*sin(angle)), zoom, offset))

    ui_manager.update(dt)
    ui_manager.draw(display_surface)

    if ui_manager.rect.CENTER_PANEL_RECT.collidepoint(screen_mouse) and not dragging_map:
        ui_manager.update_pos(mouse_pos)

    # pg.draw.rect(display_surface, (255, 0, 0), ui_manager.panel.arguments_scroll.get_abs_rect())

    pg.display.update()

pg.quit()
exit()
