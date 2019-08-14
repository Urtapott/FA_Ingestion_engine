
def velsidu(event, siduval_dict):
    item = siduval_dict['møguleikar_tree'].identify('item', event.x, event.y)
    if not siduval_dict['valdar_tree'].exists(item):
        siduval_dict['valdar_tree'].insert('', 'end', item, text=item)


def filltradi(tree, siduval_dict, siduval_list):

    for item in siduval_list:
        tree.insert('', 'end', item, text=item)
